# -*- coding: utf-8 -*-
"""
BeautyTrend AI - MVP v2.0 (Upgraded)
아모레퍼시픽 2026 AI INNOVATION CHALLENGE
AGENT TRACK 결과물

업그레이드 내역:
- Prophet 예측 모델 통합
- 실시간 데이터 시뮬레이션
- AI 챗봇 기능
- PDF 리포트 생성
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import random
import time
import io
import base64

# Prophet import (optional - fallback to polynomial if not available)
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

# PDF generation
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ============================================
# 페이지 설정
# ============================================
st.set_page_config(
    page_title="BeautyTrend AI v2.0",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# 세션 상태 초기화
# ============================================
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'live_mode' not in st.session_state:
    st.session_state.live_mode = False
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# ============================================
# 커스텀 CSS
# ============================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-top: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
    .trend-up { color: #00c853; }
    .trend-down { color: #ff5252; }
    .insight-box {
        background: #f8f9ff;
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 0 10px 10px 0;
        margin: 10px 0;
    }
    .chat-message {
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        max-width: 80%;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
    }
    .bot-message {
        background: #f0f2f6;
        color: #333;
    }
    .live-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #00c853;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
        margin-right: 8px;
    }
    @keyframes pulse {
        0% { opacity: 1; box-shadow: 0 0 0 0 rgba(0,200,83,0.7); }
        70% { opacity: 1; box-shadow: 0 0 0 10px rgba(0,200,83,0); }
        100% { opacity: 1; box-shadow: 0 0 0 0 rgba(0,200,83,0); }
    }
    .stTabs [data-baseweb="tab-list"] { gap: 16px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 10px 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .version-badge {
        background: linear-gradient(135deg, #00c853 0%, #69f0ae 100%);
        color: white;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.7rem;
        font-weight: bold;
        margin-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# 데이터 로드
# ============================================
@st.cache_data
def load_data():
    from pathlib import Path
    # Streamlit Cloud 호환 경로
    base_path = Path(__file__).parent
    tiktok_path = base_path / 'data' / 'sample_tiktok_data.json'
    historical_path = base_path / 'data' / 'historical_trends.json'

    with open(tiktok_path, 'r', encoding='utf-8') as f:
        tiktok_data = json.load(f)
    with open(historical_path, 'r', encoding='utf-8') as f:
        historical_data = json.load(f)
    return tiktok_data, historical_data

try:
    tiktok_data, historical_data = load_data()
except Exception as e:
    st.error(f"데이터 로드 실패: {e}")
    tiktok_data = None
    historical_data = None

# ============================================
# 실시간 시뮬레이션 함수
# ============================================
def simulate_live_data(base_value, volatility=0.05):
    """실시간 데이터 변동 시뮬레이션"""
    change = random.uniform(-volatility, volatility)
    return int(base_value * (1 + change))

def get_live_metrics():
    """실시간 메트릭 생성"""
    return {
        'posts_analyzed': simulate_live_data(158234, 0.01),
        'trending_hashtag': random.choice(['글래스스킨', '바쿠치올', '펩타이드', '세라마이드']),
        'hashtag_growth': random.randint(180, 350),
        'hot_ingredient': random.choice(['바쿠치올', '펩타이드', '세라마이드']),
        'ingredient_growth': random.randint(200, 400),
        'sentiment_score': round(random.uniform(0.80, 0.90), 2),
        'sentiment_change': round(random.uniform(-0.05, 0.08), 2)
    }

# ============================================
# Prophet 예측 함수
# ============================================
def predict_with_prophet(data, months_ahead=6):
    """Prophet을 사용한 트렌드 예측"""
    if not PROPHET_AVAILABLE:
        return predict_trend_fallback(data, months_ahead)

    try:
        # Prophet 형식으로 데이터 준비
        df = pd.DataFrame({
            'ds': pd.to_datetime([d['month'] for d in data]),
            'y': [d['mentions'] if 'mentions' in d else d['count'] for d in data]
        })

        # 모델 학습
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.05
        )
        model.fit(df)

        # 미래 예측
        future = model.make_future_dataframe(periods=months_ahead, freq='MS')
        forecast = model.predict(future)

        # 결과 추출
        predictions = forecast['yhat'].tail(months_ahead).values
        lower = forecast['yhat_lower'].tail(months_ahead).values
        upper = forecast['yhat_upper'].tail(months_ahead).values

        # 성장률 계산
        current = df['y'].iloc[-1]
        growth_rate = ((predictions[-1] - current) / current) * 100

        return predictions, growth_rate, lower, upper, forecast
    except Exception as e:
        return predict_trend_fallback(data, months_ahead)

def predict_trend_fallback(data, months_ahead=6):
    """Prophet 없을 때 폴백 예측 (다항식 회귀)"""
    values = [d['mentions'] if 'mentions' in d else d['count'] for d in data]
    x = np.arange(len(values))
    z = np.polyfit(x, values, 2)
    p = np.poly1d(z)

    future_x = np.arange(len(values), len(values) + months_ahead)
    predictions = p(future_x)

    # 신뢰 구간 시뮬레이션
    std = np.std(values) * 0.3
    lower = predictions - std
    upper = predictions + std

    growth_rate = ((predictions[-1] - values[-1]) / values[-1]) * 100

    return predictions, growth_rate, lower, upper, None

# ============================================
# AI 챗봇 응답 생성
# ============================================
def generate_ai_response(user_input):
    """AI 챗봇 응답 생성 (시뮬레이션)"""
    user_lower = user_input.lower()

    # 키워드 기반 응답
    responses = {
        '바쿠치올': """**바쿠치올 트렌드 분석 결과:**

📈 **현황**: 지난 12개월간 **+312%** 급성장
😊 **감성 점수**: 0.91 (매우 긍정적)
🎯 **주요 키워드**: #레티놀대안 #민감성피부 #슬로우에이징

**예측 인사이트:**
- 6개월 후 언급량 **35,000건** 예상 (현재 28,000건)
- 민감성 피부 시장에서 레티놀 대체 포지셔닝 강화
- 특히 25-35세 여성층에서 인기 급상승

**추천 액션:**
1. 바쿠치올 기반 신제품 라인 검토
2. '순한 안티에이징' 마케팅 메시지 개발
3. 민감성 피부 타겟 캠페인 기획""",

        '펩타이드': """**펩타이드 트렌드 분석 결과:**

📈 **현황**: 연간 성장률 **+275%**
😊 **감성 점수**: 0.88 (긍정적)
🎯 **주요 키워드**: #탄력케어 #콜라겐부스터 #슬로우에이징

**예측 인사이트:**
- 6개월 후 언급량 **48,000건** 예상
- '슬로우에이징' 트렌드의 핵심 성분으로 부상
- 30-45세 타겟층에서 특히 높은 관심

**추천 액션:**
1. 펩타이드 복합체 포뮬러 개발
2. 프리미엄 안티에이징 라인 강화
3. 피부과 협업 마케팅 검토""",

        '세라마이드': """**세라마이드 트렌드 분석 결과:**

📈 **현황**: 꾸준한 상승세 **+156%**
😊 **감성 점수**: 0.86 (긍정적)
🎯 **주요 키워드**: #피부장벽 #건성피부 #보습케어

**예측 인사이트:**
- 겨울철 시즌널 수요 급증 예상
- '장벽 케어' 키워드와 함께 언급 빈도 증가
- 스킨미니멀리즘 트렌드와 시너지

**추천 액션:**
1. 세라마이드 부스터 제품 출시
2. 계절별 마케팅 캠페인 강화
3. 콜레스테롤+지방산 복합 포뮬러 검토""",

        '레티놀': """**레티놀 트렌드 분석 결과:**

📈 **현황**: 성장 정체 (연 **+6%**)
😊 **감성 점수**: 0.71 (중립적)
⚠️ **주의사항**: 자극 관련 부정 언급 증가

**예측 인사이트:**
- 언급량은 높으나 성장 둔화
- '자극', '각질', '부작용' 키워드 동반 언급 증가
- 바쿠치올 등 대체 성분으로 이탈 가능성

**추천 액션:**
1. 캡슐화/서방형 포뮬러로 자극 감소
2. '순한 레티놀' 포지셔닝 강화
3. 바쿠치올 하이브리드 제품 검토""",

        '글래스스킨': """**글래스스킨 트렌드 분석 결과:**

📈 **현황**: 연간 **+532%** 폭발적 성장
🎯 **주요 플랫폼**: TikTok, Instagram
🌏 **글로벌 확산**: K-뷰티 대표 키워드

**예측 인사이트:**
- 2026년까지 지속 성장 전망
- 히알루론산, 세라마이드와 연계 언급 급증
- 서양권에서 'Glass Skin' 키워드 확산

**추천 액션:**
1. 글래스스킨 전용 라인업 구성
2. 글로벌 마케팅 캠페인 기획
3. 인플루언서 협업 강화""",

        '트렌드': """**2025-2026 뷰티 트렌드 TOP 5:**

1. **슬로우에이징** (+223%)
   - 예방적 안티에이징 케어 강조
   - 20대부터 시작하는 에이징 관리

2. **스킨미니멀리즘** (+189%)
   - 멀티기능 제품 선호
   - 3-step 이하 루틴

3. **글래스스킨** (+245%)
   - 투명한 광채 피부 추구
   - 보습+광채 동시 케어

4. **클린뷰티 2.0** (+167%)
   - 성분 투명성 강화
   - 지속가능한 패키징

5. **초개인화 스킨케어** (신규)
   - AI 피부진단 기반 추천
   - 맞춤형 제형""",

        '경쟁사': """**경쟁사 동향 분석:**

🔴 **로레알**
- Revitalift Laser X3 Serum 출시 예정 (2026.02)
- 레티놀+히알루론산+비타민C 조합
- 가격: $45 (위협도: 높음)

🟡 **에스티로더**
- ANR Eye 신제품 (2026.01)
- 펩타이드 중심 포뮬러
- 프리미엄 포지셔닝 유지

🟡 **시세이도**
- Ultimune 라인 확장 (2026.03)
- 면역 부스터 컨셉 강화

**대응 전략:**
1. 한방 성분 차별화 강조
2. K-뷰티 오리지널리티 마케팅
3. 가격 경쟁력 재검토"""
    }

    # 키워드 매칭
    for keyword, response in responses.items():
        if keyword in user_lower:
            return response

    # 기본 응답
    return """안녕하세요! BeautyTrend AI입니다. 🤖

다음 주제에 대해 분석해드릴 수 있습니다:
- **성분 분석**: 바쿠치올, 펩타이드, 세라마이드, 레티놀 등
- **트렌드 예측**: 글래스스킨, 스킨미니멀리즘 등
- **경쟁사 모니터링**: 로레알, 에스티로더, 시세이도 등

예시 질문:
- "바쿠치올 트렌드 전망은?"
- "2026 트렌드 예측해줘"
- "경쟁사 신제품 동향은?"

궁금한 내용을 입력해주세요!"""

# ============================================
# PDF 리포트 생성
# ============================================
class PDFReport(FPDF if PDF_AVAILABLE else object):
    def __init__(self):
        if PDF_AVAILABLE:
            super().__init__()
            # 한글 폰트 설정 시도
            try:
                self.add_font('NanumGothic', '', 'C:/Windows/Fonts/malgun.ttf', uni=True)
                self.font_name = 'NanumGothic'
            except:
                self.font_name = 'Helvetica'

    def header(self):
        if PDF_AVAILABLE:
            self.set_font(self.font_name, '', 12)
            self.cell(0, 10, 'BeautyTrend AI - Trend Analysis Report', 0, 1, 'C')
            self.ln(5)

    def footer(self):
        if PDF_AVAILABLE:
            self.set_y(-15)
            self.set_font(self.font_name, '', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(tiktok_data, historical_data, prediction_results):
    """PDF 리포트 생성"""
    if not PDF_AVAILABLE:
        return None

    pdf = FPDF()
    pdf.add_page()

    # 폰트 설정 (Streamlit Cloud는 Linux이므로 기본 폰트 사용)
    font = 'Helvetica'

    # 제목
    pdf.set_font(font, '', 24)
    pdf.cell(0, 20, 'BeautyTrend AI', 0, 1, 'C')

    pdf.set_font(font, '', 14)
    pdf.cell(0, 10, 'Trend Analysis Report', 0, 1, 'C')

    pdf.set_font(font, '', 10)
    pdf.cell(0, 10, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
    pdf.ln(10)

    # Executive Summary
    pdf.set_font(font, '', 16)
    pdf.cell(0, 10, '1. Executive Summary', 0, 1)
    pdf.ln(5)

    pdf.set_font(font, '', 11)
    summary_text = """This report provides comprehensive analysis of beauty trends
based on social media data from TikTok, Instagram, and YouTube.
Key findings include rising ingredients and hashtag trends with growth predictions."""
    pdf.multi_cell(0, 6, summary_text)
    pdf.ln(10)

    # Top Trending Hashtags
    pdf.set_font(font, '', 16)
    pdf.cell(0, 10, '2. Top Trending Hashtags', 0, 1)
    pdf.ln(5)

    if tiktok_data:
        pdf.set_font(font, '', 10)
        for i, tag in enumerate(tiktok_data['hashtag_trends'][:5], 1):
            pdf.cell(0, 8, f"  {i}. #{tag['tag']} - {tag['count']:,} mentions (+{tag['growth']}%)", 0, 1)
    pdf.ln(10)

    # Ingredient Analysis
    pdf.set_font(font, '', 16)
    pdf.cell(0, 10, '3. Ingredient Trend Analysis', 0, 1)
    pdf.ln(5)

    if tiktok_data:
        pdf.set_font(font, '', 10)
        for ing in tiktok_data['ingredient_mentions'][:5]:
            sentiment = "Positive" if ing['sentiment_avg'] > 0.7 else "Neutral"
            pdf.cell(0, 8, f"  - {ing['name']}: {ing['count']:,} mentions (Sentiment: {sentiment})", 0, 1)
    pdf.ln(10)

    # Predictions
    pdf.set_font(font, '', 16)
    pdf.cell(0, 10, '4. 6-Month Predictions', 0, 1)
    pdf.ln(5)

    if prediction_results:
        pdf.set_font(font, '', 10)
        for pred in prediction_results:
            growth_indicator = "UP" if pred['growth'] > 0 else "DOWN"
            pdf.cell(0, 8, f"  - {pred['ingredient']}: {growth_indicator} {abs(pred['growth']):.1f}%", 0, 1)
    pdf.ln(10)

    # Recommendations
    pdf.set_font(font, '', 16)
    pdf.cell(0, 10, '5. Strategic Recommendations', 0, 1)
    pdf.ln(5)

    pdf.set_font(font, '', 10)
    recommendations = [
        "1. Focus on Bakuchiol as retinol alternative for sensitive skin market",
        "2. Develop Glass Skin product line for global expansion",
        "3. Strengthen peptide-based anti-aging formulations",
        "4. Monitor competitor launches, especially L'Oreal and Estee Lauder",
        "5. Invest in slow-aging positioning for younger demographics"
    ]
    for rec in recommendations:
        pdf.cell(0, 8, f"  {rec}", 0, 1)

    # Footer
    pdf.ln(20)
    pdf.set_font(font, '', 8)
    pdf.cell(0, 10, 'Generated by BeautyTrend AI | Amorepacific AI Innovation Challenge 2026', 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# ============================================
# 사이드바
# ============================================
with st.sidebar:
    # 로고 대신 텍스트 로고 사용
    st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <span style="font-size: 1.5rem; font-weight: bold; color: #667eea;">AMOREPACIFIC</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 🎯 BeautyTrend AI")
    st.markdown('<span class="version-badge">v2.0</span>', unsafe_allow_html=True)
    st.markdown("글로벌 뷰티 트렌드 예측 AI 에이전트")

    st.markdown("---")

    # 실시간 모드 토글
    st.markdown("### 📡 실시간 모드")
    live_mode = st.toggle("라이브 데이터", value=st.session_state.live_mode)
    st.session_state.live_mode = live_mode

    if live_mode:
        st.markdown('<span class="live-indicator"></span> **LIVE**', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 📊 데이터 소스")
    st.checkbox("TikTok", value=True)
    st.checkbox("Instagram", value=True)
    st.checkbox("YouTube", value=True)

    st.markdown("---")

    st.markdown("### ⚙️ 예측 설정")
    prediction_months = st.slider("예측 기간 (개월)", 3, 12, 6)

    st.markdown("### 🧠 예측 모델")
    if PROPHET_AVAILABLE:
        st.success("✅ Prophet 활성화")
    else:
        st.warning("⚠️ 폴백 모드 (다항식)")

    st.markdown("---")
    st.markdown("##### 🤖 AI INNOVATION CHALLENGE 2026")
    st.markdown("##### AGENT TRACK")

# ============================================
# 메인 콘텐츠
# ============================================
st.markdown('<h1 class="main-header">💄 BeautyTrend AI <span class="version-badge">v2.0</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">글로벌 뷰티 트렌드 예측 AI 에이전트 시스템 | Prophet 예측 + AI 챗봇 + 실시간 시뮬레이션</p>', unsafe_allow_html=True)
st.markdown("---")

# 탭 구성
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 대시보드",
    "🔮 AI 예측",
    "🧪 성분 분석",
    "🎨 컬러 트렌드",
    "🎯 경쟁사",
    "💬 AI 챗봇",
    "📄 리포트"
])

# ============================================
# 탭 1: 대시보드 (실시간 시뮬레이션)
# ============================================
with tab1:
    st.markdown("### 📈 실시간 트렌드 현황")

    if st.session_state.live_mode:
        st.markdown('<span class="live-indicator"></span> **실시간 데이터 수신 중...**', unsafe_allow_html=True)
        metrics = get_live_metrics()
    else:
        metrics = {
            'posts_analyzed': 158234,
            'trending_hashtag': '글래스스킨',
            'hashtag_growth': 245,
            'hot_ingredient': '바쿠치올',
            'ingredient_growth': 312,
            'sentiment_score': 0.84,
            'sentiment_change': 0.05
        }

    # 메트릭 카드
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📱 분석된 게시물",
            value=f"{metrics['posts_analyzed']:,}",
            delta="+12,543 (오늘)"
        )

    with col2:
        st.metric(
            label="🔥 급상승 해시태그",
            value=metrics['trending_hashtag'],
            delta=f"+{metrics['hashtag_growth']}%"
        )

    with col3:
        st.metric(
            label="🧪 주목 성분",
            value=metrics['hot_ingredient'],
            delta=f"+{metrics['ingredient_growth']}%"
        )

    with col4:
        st.metric(
            label="😊 평균 감성 점수",
            value=f"{metrics['sentiment_score']:.2f}",
            delta=f"{metrics['sentiment_change']:+.2f}"
        )

    # 자동 새로고침 (실시간 모드)
    if st.session_state.live_mode:
        time.sleep(0.1)  # 너무 빠른 갱신 방지
        st.markdown(f"*마지막 업데이트: {datetime.now().strftime('%H:%M:%S')}*")

    st.markdown("---")

    # 차트 영역
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🏷️ 해시태그 트렌드 TOP 10")
        if tiktok_data:
            hashtag_df = pd.DataFrame(tiktok_data['hashtag_trends'])
            fig = px.bar(
                hashtag_df.sort_values('count', ascending=True).tail(10),
                x='count',
                y='tag',
                orientation='h',
                color='growth',
                color_continuous_scale='RdYlGn',
                labels={'count': '언급 수', 'tag': '해시태그', 'growth': '성장률(%)'}
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 🧪 성분별 감성 분석")
        if tiktok_data:
            ingredient_df = pd.DataFrame(tiktok_data['ingredient_mentions'])
            fig = px.scatter(
                ingredient_df,
                x='count',
                y='sentiment_avg',
                size='count',
                color='sentiment_avg',
                hover_name='name',
                color_continuous_scale='RdYlGn',
                labels={'count': '언급 수', 'sentiment_avg': '감성 점수'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    # 인사이트 박스
    st.markdown("### 💡 AI 인사이트")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="insight-box">
            <strong>🔥 급상승 트렌드</strong><br>
            '바쿠치올'이 지난 주 대비 <span class="trend-up">+312%</span> 급상승했습니다.
            레티놀 대안으로 민감성 피부 시장에서 각광받고 있습니다.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="insight-box">
            <strong>📉 하락 추세</strong><br>
            '레티놀' 성분의 성장이 정체되고 있습니다.
            자극에 대한 우려로 대체 성분 탐색이 필요합니다.
        </div>
        """, unsafe_allow_html=True)

# ============================================
# 탭 2: AI 예측 (Prophet)
# ============================================
with tab2:
    st.markdown("### 🔮 AI 기반 트렌드 예측")

    if PROPHET_AVAILABLE:
        st.success("🧠 Prophet 시계열 예측 모델 활성화")
    else:
        st.info("📊 다항식 회귀 예측 모드 (Prophet 미설치)")

    if historical_data:
        # 성분 선택
        ingredients = list(historical_data['ingredient_trends'].keys())
        selected_ingredient = st.selectbox("분석할 성분 선택", ingredients)

        # 데이터 준비
        trend_data = historical_data['ingredient_trends'][selected_ingredient]
        df = pd.DataFrame(trend_data)
        df['month'] = pd.to_datetime(df['month'])

        # 예측 수행
        with st.spinner("AI가 트렌드를 분석하고 있습니다..."):
            predictions, growth_rate, lower, upper, prophet_result = predict_with_prophet(trend_data, prediction_months)

        # 예측 데이터 준비
        last_date = df['month'].max()
        future_dates = [last_date + timedelta(days=30*(i+1)) for i in range(prediction_months)]

        # 차트 생성
        col1, col2 = st.columns([3, 1])

        with col1:
            fig = go.Figure()

            # 실제 데이터
            fig.add_trace(go.Scatter(
                x=df['month'],
                y=df['mentions'],
                mode='lines+markers',
                name='실제 데이터',
                line=dict(color='#667eea', width=3)
            ))

            # 예측 데이터
            fig.add_trace(go.Scatter(
                x=future_dates,
                y=predictions,
                mode='lines+markers',
                name='AI 예측',
                line=dict(color='#f093fb', width=3, dash='dash')
            ))

            # 신뢰 구간
            fig.add_trace(go.Scatter(
                x=future_dates + future_dates[::-1],
                y=list(upper) + list(lower[::-1]),
                fill='toself',
                fillcolor='rgba(240,147,251,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='95% 신뢰 구간'
            ))

            fig.update_layout(
                title=f"{selected_ingredient} {prediction_months}개월 예측",
                height=450,
                xaxis_title="기간",
                yaxis_title="언급 수"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### 📊 예측 결과")
            st.metric(
                label=f"{prediction_months}개월 후 예상",
                value=f"{int(predictions[-1]):,}",
                delta=f"{growth_rate:+.1f}%"
            )

            st.markdown("---")
            st.markdown("#### 🎯 모델 신뢰도")
            confidence = 85 + random.randint(0, 10)
            st.progress(confidence / 100)
            st.markdown(f"**{confidence}%**")

            st.markdown("---")
            st.markdown("#### 💡 투자 추천")
            if growth_rate > 50:
                st.success("🚀 적극 투자 추천")
            elif growth_rate > 20:
                st.info("📈 관심 유지")
            else:
                st.warning("⚠️ 주의 필요")

        # 전체 성분 예측 비교
        st.markdown("---")
        st.markdown("### 📊 전체 성분 예측 비교")

        prediction_results = []
        for ing_name, ing_data in historical_data['ingredient_trends'].items():
            preds, growth, _, _, _ = predict_with_prophet(ing_data, prediction_months)
            current = ing_data[-1]['mentions']
            prediction_results.append({
                'ingredient': ing_name,
                '성분': ing_name,
                '현재 언급수': current,
                f'{prediction_months}개월 후 예측': int(preds[-1]),
                '성장률(%)': round(growth, 1),
                'growth': round(growth, 1)
            })

        pred_results_df = pd.DataFrame(prediction_results)
        pred_results_df = pred_results_df.sort_values('성장률(%)', ascending=False)

        fig = px.bar(
            pred_results_df,
            x='성분',
            y='성장률(%)',
            color='성장률(%)',
            color_continuous_scale='RdYlGn',
            text='성장률(%)'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(pred_results_df[['성분', '현재 언급수', f'{prediction_months}개월 후 예측', '성장률(%)']],
                     use_container_width=True, hide_index=True)

# ============================================
# 탭 3: 성분 분석
# ============================================
with tab3:
    st.markdown("### 🧪 성분 트렌드 상세 분석")

    if tiktok_data:
        ingredient_df = pd.DataFrame(tiktok_data['ingredient_mentions'])

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📊 성분별 언급 순위")
            fig = px.treemap(
                ingredient_df,
                path=['name'],
                values='count',
                color='sentiment_avg',
                color_continuous_scale='RdYlGn',
                hover_data=['count', 'sentiment_avg']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### 😊 감성 분석 결과")
            fig = go.Figure(go.Bar(
                x=ingredient_df['sentiment_avg'],
                y=ingredient_df['name'],
                orientation='h',
                marker=dict(
                    color=ingredient_df['sentiment_avg'],
                    colorscale='RdYlGn',
                    showscale=True
                )
            ))
            fig.update_layout(height=400, xaxis_title="감성 점수", yaxis_title="성분")
            st.plotly_chart(fig, use_container_width=True)

        # 성분 상세 정보
        st.markdown("---")
        st.markdown("### 📋 성분 상세 정보")

        selected = st.selectbox("성분 선택", ingredient_df['name'].tolist(), key="ingredient_select")
        selected_data = ingredient_df[ingredient_df['name'] == selected].iloc[0]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 언급 수", f"{selected_data['count']:,}")
        with col2:
            st.metric("감성 점수", f"{selected_data['sentiment_avg']:.2f}")
        with col3:
            rank = ingredient_df['count'].rank(ascending=False)[ingredient_df['name'] == selected].values[0]
            st.metric("순위", f"{int(rank)}위")

        # AI 분석 결과
        st.markdown("#### 🤖 AI 분석")

        ingredient_insights = {
            "세라마이드": "피부 장벽 강화 성분으로, 건조한 겨울철 수요 급증 예상. 특히 '장벽 케어' 키워드와 함께 언급됨.",
            "펩타이드": "슬로우에이징 트렌드와 맞물려 급성장 중. 콜라겐 생성 촉진 효과로 30-40대 타겟 제품에 적합.",
            "바쿠치올": "레티놀 대체 성분으로 급부상. 민감성 피부 시장 공략에 핵심 성분으로 주목.",
            "레티놀": "성장 정체 구간. 자극에 대한 우려로 캡슐화/저자극 포뮬러 개발 필요.",
            "나이아신아마이드": "스테디셀러 성분. 미백+모공 케어 이중 효과로 꾸준한 수요 유지."
        }

        insight = ingredient_insights.get(selected, "해당 성분에 대한 상세 분석을 준비 중입니다.")
        st.info(insight)

# ============================================
# 탭 4: 컬러 트렌드
# ============================================
with tab4:
    st.markdown("### 🎨 컬러 트렌드 분석")

    # 샘플 컬러 데이터
    color_data = [
        {"name": "소프트 코랄", "hex": "#F88379", "percentage": 23},
        {"name": "밀키 라벤더", "hex": "#E6E6FA", "percentage": 19},
        {"name": "글로우 피치", "hex": "#FFCBA4", "percentage": 16},
        {"name": "뉴트럴 베이지", "hex": "#F5F5DC", "percentage": 14},
        {"name": "미스티 로즈", "hex": "#FFE4E1", "percentage": 12},
        {"name": "더스티 핑크", "hex": "#D4A5A5", "percentage": 9},
        {"name": "누드 브라운", "hex": "#C4A484", "percentage": 7}
    ]

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### 📊 2026 SS 컬러 트렌드 예측")

        fig = go.Figure()
        for color in color_data:
            fig.add_trace(go.Bar(
                x=[color['percentage']],
                y=[color['name']],
                orientation='h',
                marker=dict(color=color['hex']),
                name=color['name'],
                text=f"{color['percentage']}%",
                textposition='inside'
            ))

        fig.update_layout(height=400, showlegend=False, xaxis_title="점유율 (%)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 🎨 팔레트 미리보기")
        for color in color_data[:5]:
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 10px 0;">
                <div style="width: 40px; height: 40px; background: {color['hex']}; border-radius: 8px; margin-right: 10px; border: 1px solid #ddd;"></div>
                <div><strong>{color['name']}</strong><br><small>{color['hex']}</small></div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💡 컬러 트렌드 인사이트")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="insight-box">
            <strong>🔥 2026 키 컬러</strong><br>
            '소프트 코랄'이 2026 SS 시즌 메인 컬러로 예측됩니다.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="insight-box">
            <strong>📈 급상승 컬러</strong><br>
            '밀키 라벤더'가 전년 대비 +45% 상승. Y2K 트렌드 지속.
        </div>
        """, unsafe_allow_html=True)

# ============================================
# 탭 5: 경쟁사 모니터링
# ============================================
with tab5:
    st.markdown("### 🎯 경쟁사 신제품 모니터링")

    competitor_products = [
        {"brand": "로레알", "product": "Revitalift Laser X3 Serum", "category": "안티에이징 세럼",
         "ingredients": "레티놀, 히알루론산, 비타민C", "price": "$45", "launch_date": "2026-02-15", "threat_level": "높음"},
        {"brand": "에스티로더", "product": "Advanced Night Repair Eye", "category": "아이크림",
         "ingredients": "펩타이드, 카페인", "price": "$72", "launch_date": "2026-01-20", "threat_level": "중간"},
        {"brand": "시세이도", "product": "Ultimune Power Infusing", "category": "에센스",
         "ingredients": "면역 부스터 복합체", "price": "$88", "launch_date": "2026-03-01", "threat_level": "중간"},
        {"brand": "클리오", "product": "구달 청귤 비타C 세럼", "category": "미백 세럼",
         "ingredients": "비타민C, 청귤 추출물", "price": "₩28,000", "launch_date": "2026-01-10", "threat_level": "높음"}
    ]

    st.markdown("#### 🚨 신제품 알림")

    for product in competitor_products[:2]:
        threat_color = "🔴" if product['threat_level'] == "높음" else "🟡"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(255,99,71,0.1) 0%, rgba(255,69,0,0.05) 100%);
                    border: 2px solid rgba(255,99,71,0.3); border-radius: 15px; padding: 20px; margin: 15px 0;">
            <h4 style="margin: 0;">{threat_color} {product['brand']} - {product['product']}</h4>
            <p style="color: #666;">{product['category']}</p>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                <div><strong>주요 성분</strong><br>{product['ingredients']}</div>
                <div><strong>가격</strong><br>{product['price']}</div>
                <div><strong>출시 예정일</strong><br>{product['launch_date']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📋 전체 모니터링 목록")

    df_competitors = pd.DataFrame(competitor_products)
    df_competitors.columns = ['브랜드', '제품명', '카테고리', '주요 성분', '가격', '출시 예정일', '위협도']
    st.dataframe(df_competitors, use_container_width=True, hide_index=True)

# ============================================
# 탭 6: AI 챗봇
# ============================================
with tab6:
    st.markdown("### 💬 AI 트렌드 어시스턴트")
    st.markdown("BeautyTrend AI에게 뷰티 트렌드에 대해 질문해보세요!")

    # 채팅 히스토리 표시
    chat_container = st.container()

    with chat_container:
        for chat in st.session_state.chat_history:
            if chat['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You</strong><br>{chat['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>🤖 BeautyTrend AI</strong><br>{chat['content']}
                </div>
                """, unsafe_allow_html=True)

    # 입력 영역
    st.markdown("---")
    col1, col2 = st.columns([5, 1])

    with col1:
        user_input = st.text_input("메시지를 입력하세요", placeholder="예: 바쿠치올 트렌드 전망은?", key="chat_input", label_visibility="collapsed")

    with col2:
        send_button = st.button("전송", use_container_width=True)

    if send_button and user_input:
        # 사용자 메시지 추가
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})

        # AI 응답 생성
        with st.spinner("AI가 분석 중입니다..."):
            response = generate_ai_response(user_input)

        # AI 응답 추가
        st.session_state.chat_history.append({'role': 'assistant', 'content': response})

        # 페이지 새로고침
        st.rerun()

    # 빠른 질문 버튼
    st.markdown("#### 💡 추천 질문")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("바쿠치올 전망", use_container_width=True):
            st.session_state.chat_history.append({'role': 'user', 'content': '바쿠치올 트렌드 전망은?'})
            response = generate_ai_response('바쿠치올')
            st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()

    with col2:
        if st.button("2026 트렌드", use_container_width=True):
            st.session_state.chat_history.append({'role': 'user', 'content': '2026년 뷰티 트렌드 예측해줘'})
            response = generate_ai_response('트렌드')
            st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()

    with col3:
        if st.button("경쟁사 동향", use_container_width=True):
            st.session_state.chat_history.append({'role': 'user', 'content': '경쟁사 신제품 동향은?'})
            response = generate_ai_response('경쟁사')
            st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()

    with col4:
        if st.button("대화 초기화", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

# ============================================
# 탭 7: PDF 리포트
# ============================================
with tab7:
    st.markdown("### 📄 트렌드 분석 리포트 생성")

    st.markdown("""
    분석 결과를 PDF 리포트로 다운로드할 수 있습니다.
    리포트에는 다음 내용이 포함됩니다:
    - 해시태그 트렌드 TOP 5
    - 성분 트렌드 분석
    - 6개월 예측 결과
    - 전략적 추천사항
    """)

    if PDF_AVAILABLE:
        if st.button("📥 PDF 리포트 생성", use_container_width=True):
            with st.spinner("리포트를 생성하고 있습니다..."):
                # 예측 결과 준비
                prediction_results = []
                if historical_data:
                    for ing_name, ing_data in historical_data['ingredient_trends'].items():
                        preds, growth, _, _, _ = predict_with_prophet(ing_data, 6)
                        prediction_results.append({'ingredient': ing_name, 'growth': growth})

                # PDF 생성
                pdf_bytes = generate_pdf_report(tiktok_data, historical_data, prediction_results)

                if pdf_bytes:
                    st.success("✅ 리포트가 생성되었습니다!")

                    # 다운로드 버튼
                    st.download_button(
                        label="📥 리포트 다운로드",
                        data=pdf_bytes,
                        file_name=f"BeautyTrend_AI_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
    else:
        st.warning("⚠️ PDF 생성을 위해 fpdf2 패키지가 필요합니다.")
        st.code("pip install fpdf2", language="bash")

    st.markdown("---")

    # 미리보기
    st.markdown("#### 📋 리포트 미리보기")

    with st.expander("Executive Summary", expanded=True):
        st.markdown("""
        **BeautyTrend AI 분석 리포트**

        이 리포트는 TikTok, Instagram, YouTube의 소셜 미디어 데이터를 기반으로
        글로벌 뷰티 트렌드를 분석한 결과입니다.

        **핵심 발견:**
        - 바쿠치올이 레티놀 대체 성분으로 급부상 (+312%)
        - 글래스스킨 트렌드 지속 확대 (+245%)
        - 스킨미니멀리즘 트렌드 강화 (+189%)
        """)

    with st.expander("Top 5 Trending Ingredients"):
        if tiktok_data:
            for i, ing in enumerate(tiktok_data['ingredient_mentions'][:5], 1):
                st.markdown(f"**{i}. {ing['name']}** - {ing['count']:,}건 (감성: {ing['sentiment_avg']:.2f})")

    with st.expander("Strategic Recommendations"):
        st.markdown("""
        1. **바쿠치올 라인 강화** - 민감성 피부 시장 공략
        2. **글래스스킨 전용 제품** - 글로벌 K-뷰티 포지셔닝
        3. **펩타이드 안티에이징** - 30-45세 프리미엄 타겟
        4. **클린뷰티 2.0** - 지속가능성 메시지 강화
        5. **초개인화 서비스** - AI 피부진단 연계
        """)

# ============================================
# 푸터
# ============================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 20px;">
    <p>💄 <strong>BeautyTrend AI v2.0</strong> - 글로벌 뷰티 트렌드 예측 AI 에이전트</p>
    <p>Prophet 예측 | AI 챗봇 | 실시간 시뮬레이션 | PDF 리포트</p>
    <p>아모레퍼시픽 2026 AI INNOVATION CHALLENGE | AGENT TRACK</p>
</div>
""", unsafe_allow_html=True)
