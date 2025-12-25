# -*- coding: utf-8 -*-
"""
BeautyTrend AI - MVP v3.0 (Enhanced)
아모레퍼시픽 2026 AI INNOVATION CHALLENGE
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import io
import base64

# PDF 생성
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# 페이지 설정
st.set_page_config(
    page_title="BeautyTrend AI",
    page_icon="💄",
    layout="wide"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
    .insight-box {
        background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 100%);
        border-left: 4px solid #667eea;
        padding: 15px 20px;
        border-radius: 0 15px 15px 0;
        margin: 10px 0;
    }
    .trend-up { color: #10b981; font-weight: bold; }
    .trend-down { color: #ef4444; font-weight: bold; }
    .agent-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 5px;
    }
    .feature-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 데이터 정의 (Inline Data)
# ============================================================
@st.cache_data
def load_data():
    # TikTok 트렌드 데이터
    tiktok_data = {
        "hashtag_trends": [
            {"tag": "#글래스스킨", "count": 158000, "growth": 245, "region": "Global"},
            {"tag": "#스킨미니멀리즘", "count": 92000, "growth": 189, "region": "Korea"},
            {"tag": "#세라마이드", "count": 87000, "growth": 156, "region": "Asia"},
            {"tag": "#바쿠치올", "count": 65000, "growth": 312, "region": "US"},
            {"tag": "#펩타이드", "count": 54000, "growth": 178, "region": "Europe"},
            {"tag": "#슬로우에이징", "count": 48000, "growth": 267, "region": "Global"},
            {"tag": "#비건뷰티", "count": 42000, "growth": 134, "region": "Europe"},
            {"tag": "#클린뷰티", "count": 38000, "growth": 98, "region": "US"}
        ],
        "ingredient_mentions": [
            {"name": "세라마이드", "count": 45000, "sentiment_avg": 0.86, "category": "보습"},
            {"name": "나이아신아마이드", "count": 62000, "sentiment_avg": 0.82, "category": "미백"},
            {"name": "펩타이드", "count": 38000, "sentiment_avg": 0.88, "category": "안티에이징"},
            {"name": "바쿠치올", "count": 28000, "sentiment_avg": 0.91, "category": "안티에이징"},
            {"name": "레티놀", "count": 51000, "sentiment_avg": 0.71, "category": "안티에이징"},
            {"name": "히알루론산", "count": 72000, "sentiment_avg": 0.85, "category": "보습"},
            {"name": "비타민C", "count": 68000, "sentiment_avg": 0.79, "category": "미백"},
            {"name": "스쿠알란", "count": 31000, "sentiment_avg": 0.87, "category": "보습"}
        ]
    }

    # 시계열 데이터
    historical_data = {
        "ingredient_trends": {
            "세라마이드": [{"month": f"2024-{i:02d}", "mentions": int(12000 + i*3000 + random.randint(-1000, 1000))} for i in range(1, 13)],
            "바쿠치올": [{"month": f"2024-{i:02d}", "mentions": int(2000 + i*2500 + random.randint(-500, 500))} for i in range(1, 13)],
            "펩타이드": [{"month": f"2024-{i:02d}", "mentions": int(8000 + i*2500 + random.randint(-800, 800))} for i in range(1, 13)],
            "나이아신아마이드": [{"month": f"2024-{i:02d}", "mentions": int(15000 + i*2000 + random.randint(-1000, 1000))} for i in range(1, 13)],
            "레티놀": [{"month": f"2024-{i:02d}", "mentions": int(20000 + i*1500 + random.randint(-1200, 1200))} for i in range(1, 13)]
        }
    }

    # 컬러 트렌드 데이터
    color_trends = [
        {"color": "Soft Pink", "hex": "#FFB6C1", "growth": 45, "season": "S/S 2025"},
        {"color": "Terracotta", "hex": "#E2725B", "growth": 38, "season": "F/W 2025"},
        {"color": "Mauve", "hex": "#E0B0FF", "growth": 52, "season": "S/S 2025"},
        {"color": "Brick Red", "hex": "#CB4154", "growth": 28, "season": "F/W 2025"},
        {"color": "Nude Beige", "hex": "#F5DEB3", "growth": 61, "season": "All Season"},
        {"color": "Berry", "hex": "#8E4585", "growth": 33, "season": "F/W 2025"},
        {"color": "Coral", "hex": "#FF7F50", "growth": 47, "season": "S/S 2025"},
        {"color": "Dusty Rose", "hex": "#DCAE96", "growth": 55, "season": "All Season"}
    ]

    # 경쟁사 데이터
    competitor_data = [
        {"brand": "에스티로더", "product": "Advanced Night Repair 2.0", "launch": "2025-02", "category": "세럼", "key_ingredient": "크로노럭신"},
        {"brand": "로레알", "product": "Revitalift Laser X4", "launch": "2025-03", "category": "크림", "key_ingredient": "레티놀"},
        {"brand": "시세이도", "product": "Ultimune Power Infusing 4.0", "launch": "2025-01", "category": "세럼", "key_ingredient": "ImuGeneration"},
        {"brand": "SK-II", "product": "GenOptics Ultra Aura", "launch": "2025-04", "category": "에센스", "key_ingredient": "피테라"},
        {"brand": "랑콤", "product": "Absolue Rich Cream 2025", "launch": "2025-02", "category": "크림", "key_ingredient": "그랑로즈"}
    ]

    return tiktok_data, historical_data, color_trends, competitor_data

tiktok_data, historical_data, color_trends, competitor_data = load_data()

# ============================================================
# PDF 리포트 생성 함수
# ============================================================
class TrendReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('NanumGothic', '', 'C:/Windows/Fonts/malgun.ttf', uni=True)

    def header(self):
        self.set_font('NanumGothic', '', 16)
        self.set_text_color(102, 126, 234)
        self.cell(0, 10, 'BeautyTrend AI Report', ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('NanumGothic', '', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Amorepacific AI Innovation Challenge 2026', align='C')

def generate_pdf_report(ingredient, prediction_data, growth):
    """PDF 리포트 생성"""
    if not PDF_AVAILABLE:
        return None

    try:
        pdf = FPDF()
        pdf.add_page()

        # 폰트 설정 (한글 지원)
        try:
            pdf.add_font('Malgun', '', 'C:/Windows/Fonts/malgun.ttf', uni=True)
            pdf.set_font('Malgun', '', 16)
        except:
            pdf.set_font('Helvetica', '', 16)

        # 타이틀
        pdf.set_text_color(102, 126, 234)
        pdf.cell(0, 15, 'BeautyTrend AI - Trend Analysis Report', ln=True, align='C')
        pdf.ln(10)

        # 날짜
        pdf.set_font_size(10)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 8, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True, align='R')
        pdf.ln(10)

        # 성분 정보
        pdf.set_text_color(51, 51, 51)
        pdf.set_font_size(14)
        pdf.cell(0, 10, f'Analysis Target: {ingredient}', ln=True)
        pdf.ln(5)

        # 예측 결과
        pdf.set_font_size(12)
        pdf.cell(0, 8, f'6-Month Growth Prediction: {growth:+.1f}%', ln=True)
        pdf.cell(0, 8, f'Predicted Mentions: {int(prediction_data[-1]):,}', ln=True)
        pdf.ln(10)

        # 추천
        pdf.set_font_size(11)
        if growth > 50:
            recommendation = "STRONG BUY - Recommend active investment in this ingredient"
        elif growth > 20:
            recommendation = "HOLD - Monitor and maintain interest"
        else:
            recommendation = "WATCH - Continue observation"
        pdf.cell(0, 8, f'Recommendation: {recommendation}', ln=True)

        # 푸터
        pdf.ln(20)
        pdf.set_font_size(9)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 8, 'Powered by BeautyTrend AI | Amorepacific AI Innovation Challenge 2026', ln=True, align='C')

        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        st.error(f"PDF 생성 오류: {e}")
        return None

# ============================================================
# 예측 모델 (향상된 버전)
# ============================================================
def advanced_forecast(data, periods=6):
    """향상된 시계열 예측 (Prophet 스타일)"""
    values = np.array([d['mentions'] for d in data])
    n = len(values)
    x = np.arange(n)

    # 2차 다항식 + 계절성 시뮬레이션
    z = np.polyfit(x, values, 2)
    trend = np.poly1d(z)

    # 잔차에서 패턴 추출
    residuals = values - trend(x)
    seasonal_amplitude = np.std(residuals) * 0.5

    # 미래 예측
    future_x = np.arange(n, n + periods)
    predictions = trend(future_x)

    # 계절성 추가
    seasonal = seasonal_amplitude * np.sin(2 * np.pi * future_x / 12)
    predictions = predictions + seasonal

    # 신뢰 구간
    std_error = np.std(residuals)
    lower = predictions - 1.96 * std_error
    upper = predictions + 1.96 * std_error

    return predictions, lower, upper

# ============================================================
# 사이드바
# ============================================================
with st.sidebar:
    st.markdown("### 💄 BeautyTrend AI")
    st.markdown("글로벌 뷰티 트렌드 예측 AI 에이전트")
    st.markdown("---")

    st.markdown("##### 🤖 AI 에이전트 구성")
    agents = ["Orchestrator", "Data Fetch", "Trend Model", "Color Analysis", "Competitor Monitor"]
    for agent in agents:
        st.markdown(f'<span class="agent-badge">{agent}</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### 📊 데이터 소스")
    st.markdown("- TikTok API")
    st.markdown("- Instagram Graph API")
    st.markdown("- YouTube Data API")
    st.markdown("- 뷰티 커뮤니티 크롤링")

    st.markdown("---")
    st.markdown("##### 🏆 AI INNOVATION CHALLENGE 2026")
    st.markdown("AGENT TRACK")

# ============================================================
# 헤더
# ============================================================
st.markdown('<h1 class="main-header">💄 BeautyTrend AI</h1>', unsafe_allow_html=True)
st.markdown("**글로벌 뷰티 트렌드 예측 AI 에이전트** | Multi-Agent 기반 실시간 트렌드 분석 및 6~12개월 선행 예측")
st.markdown("---")

# ============================================================
# 탭 구성
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 대시보드",
    "🔮 트렌드 예측",
    "🎨 컬러 트렌드",
    "🏢 경쟁사 모니터링",
    "⚡ 시뮬레이션",
    "💬 AI 챗봇"
])

# ============================================================
# TAB 1: 대시보드
# ============================================================
with tab1:
    # 메트릭 카드
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📱 분석 게시물", "158,234", "+12,543 (7일)")
    with col2:
        st.metric("🔥 급상승 키워드", "#글래스스킨", "+245%")
    with col3:
        st.metric("🧪 주목 성분", "바쿠치올", "+312%")
    with col4:
        st.metric("😊 평균 감성 점수", "0.84", "+0.05")

    st.markdown("---")

    # 차트 영역
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🏷️ 해시태그 트렌드 TOP 8")
        df_hashtag = pd.DataFrame(tiktok_data['hashtag_trends'])
        fig = px.bar(
            df_hashtag,
            x='count',
            y='tag',
            orientation='h',
            color='growth',
            color_continuous_scale='RdYlGn',
            hover_data=['region']
        )
        fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 🧪 성분별 감성 분석")
        df_ingredient = pd.DataFrame(tiktok_data['ingredient_mentions'])
        fig = px.scatter(
            df_ingredient,
            x='count',
            y='sentiment_avg',
            size='count',
            color='category',
            hover_name='name',
            size_max=50
        )
        fig.update_layout(height=400)
        fig.update_xaxes(title="언급량")
        fig.update_yaxes(title="감성 점수", range=[0.6, 1.0])
        st.plotly_chart(fig, use_container_width=True)

    # 인사이트 박스
    st.markdown("---")
    st.markdown("#### 💡 AI 인사이트")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="insight-box">
        <strong>🚀 급상승 트렌드</strong><br>
        바쿠치올이 레티놀 대안으로 급부상 중입니다. 민감성 피부 시장에서 312% 성장률을 보이며,
        특히 25-34세 여성층에서 높은 관심을 받고 있습니다.
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="insight-box">
        <strong>🎯 추천 액션</strong><br>
        슬로우에이징 트렌드와 바쿠치올을 결합한 신제품 라인 검토를 권장합니다.
        예상 시장 규모: 2026년 $2.3B (YoY +45%)
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# TAB 2: 트렌드 예측
# ============================================================
with tab2:
    st.markdown("### 🔮 AI 기반 트렌드 예측")
    st.markdown("시계열 분석 모델을 활용한 6개월 선행 트렌드 예측")

    col1, col2 = st.columns([1, 3])

    with col1:
        ingredient = st.selectbox(
            "분석 성분 선택",
            list(historical_data['ingredient_trends'].keys())
        )

        forecast_period = st.slider("예측 기간 (개월)", 3, 12, 6)

    # 예측 수행
    data = historical_data['ingredient_trends'][ingredient]
    df = pd.DataFrame(data)
    df['month'] = pd.to_datetime(df['month'])

    predictions, lower, upper = advanced_forecast(data, forecast_period)

    # 예측 날짜 생성
    future_dates = [df['month'].max() + timedelta(days=30*(i+1)) for i in range(forecast_period)]

    # 성장률 계산
    current_value = df['mentions'].iloc[-1]
    predicted_value = predictions[-1]
    growth = ((predicted_value - current_value) / current_value) * 100

    with col2:
        # 차트
        fig = go.Figure()

        # 실제 데이터
        fig.add_trace(go.Scatter(
            x=df['month'],
            y=df['mentions'],
            mode='lines+markers',
            name='실제 데이터',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ))

        # 예측 데이터
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=predictions,
            mode='lines+markers',
            name='예측',
            line=dict(color='#764ba2', width=3, dash='dash'),
            marker=dict(size=8)
        ))

        # 신뢰 구간
        fig.add_trace(go.Scatter(
            x=future_dates + future_dates[::-1],
            y=list(upper) + list(lower[::-1]),
            fill='toself',
            fillcolor='rgba(118, 75, 162, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='95% 신뢰구간'
        ))

        fig.update_layout(
            height=450,
            title=f"{ingredient} 트렌드 예측",
            xaxis_title="날짜",
            yaxis_title="언급량",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

    # 예측 결과 카드
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "현재 언급량",
            f"{int(current_value):,}",
            ""
        )
    with col2:
        st.metric(
            f"{forecast_period}개월 후 예측",
            f"{int(predicted_value):,}",
            f"{growth:+.1f}%"
        )
    with col3:
        if growth > 50:
            st.success("🚀 **적극 투자 추천**")
            recommendation = "이 성분을 활용한 신제품 개발을 적극 권장합니다."
        elif growth > 20:
            st.info("📈 **관심 유지**")
            recommendation = "지속적인 모니터링과 단계적 투자를 권장합니다."
        else:
            st.warning("👀 **관망**")
            recommendation = "시장 상황을 지켜보며 신중한 접근이 필요합니다."

    st.markdown(f"**AI 추천**: {recommendation}")

    # PDF 다운로드 버튼
    st.markdown("---")
    if PDF_AVAILABLE:
        pdf_bytes = generate_pdf_report(ingredient, predictions, growth)
        if pdf_bytes:
            st.download_button(
                label="📥 PDF 리포트 다운로드",
                data=pdf_bytes,
                file_name=f"BeautyTrend_AI_{ingredient}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
    else:
        st.info("💡 PDF 기능은 로컬 환경에서 사용 가능합니다.")

# ============================================================
# TAB 3: 컬러 트렌드
# ============================================================
with tab3:
    st.markdown("### 🎨 컬러 트렌드 분석")
    st.markdown("소셜 미디어 이미지 분석을 통한 뷰티 컬러 트렌드 예측")

    col1, col2 = st.columns([2, 1])

    with col1:
        # 컬러 팔레트 시각화
        df_color = pd.DataFrame(color_trends)

        fig = go.Figure()
        for i, row in df_color.iterrows():
            fig.add_trace(go.Bar(
                x=[row['growth']],
                y=[row['color']],
                orientation='h',
                marker_color=row['hex'],
                name=row['color'],
                text=f"+{row['growth']}%",
                textposition='outside',
                hovertemplate=f"<b>{row['color']}</b><br>성장률: +{row['growth']}%<br>시즌: {row['season']}<extra></extra>"
            ))

        fig.update_layout(
            height=450,
            title="2025 뷰티 컬러 트렌드 성장률",
            xaxis_title="성장률 (%)",
            yaxis_title="",
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 🔝 TOP 3 컬러")
        for i, row in df_color.nlargest(3, 'growth').iterrows():
            st.markdown(f"""
            <div style="background: {row['hex']}; padding: 15px; border-radius: 10px; margin: 10px 0; color: {'white' if row['hex'] in ['#8E4585', '#CB4154', '#E2725B'] else 'black'};">
                <strong>{row['color']}</strong><br>
                성장률: +{row['growth']}%<br>
                시즌: {row['season']}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 💄 추천 제품 카테고리")
        st.markdown("- 립스틱 / 립글로스")
        st.markdown("- 블러셔 / 치크")
        st.markdown("- 아이섀도우 팔레트")

# ============================================================
# TAB 4: 경쟁사 모니터링
# ============================================================
with tab4:
    st.markdown("### 🏢 경쟁사 신제품 모니터링")
    st.markdown("AI 기반 경쟁사 신제품 조기 탐지 및 분석")

    df_competitor = pd.DataFrame(competitor_data)

    # 타임라인 차트
    fig = px.timeline(
        df_competitor,
        x_start="launch",
        x_end="launch",
        y="brand",
        color="category",
        hover_data=["product", "key_ingredient"],
        title="2025 경쟁사 신제품 출시 타임라인"
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

    # 상세 테이블
    st.markdown("#### 📋 신제품 상세 정보")
    st.dataframe(
        df_competitor,
        column_config={
            "brand": "브랜드",
            "product": "제품명",
            "launch": "출시 예정",
            "category": "카테고리",
            "key_ingredient": "핵심 성분"
        },
        hide_index=True,
        use_container_width=True
    )

    # 인사이트
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="insight-box">
        <strong>🔍 경쟁 분석 인사이트</strong><br>
        에스티로더와 시세이도가 2025년 초 프리미엄 세럼 라인 강화 예정.
        레티놀 대체 성분과 피부 장벽 강화 성분이 주요 트렌드로 부상.
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="insight-box">
        <strong>🎯 전략 제안</strong><br>
        바쿠치올 기반 안티에이징 세럼으로 시장 선점 기회.
        Q1 2025 출시 타겟으로 개발 가속화 권장.
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# TAB 5: 시뮬레이션
# ============================================================
with tab5:
    st.markdown("### ⚡ 신제품 성공 시뮬레이션")
    st.markdown("AI 모델 기반 신제품 시장 성공 확률 예측")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### 제품 정보 입력")

        product_name = st.text_input("제품명", "뉴 바쿠치올 세럼")

        category = st.selectbox("카테고리", ["세럼", "크림", "에센스", "토너", "마스크팩"])

        main_ingredient = st.selectbox(
            "주요 성분",
            ["바쿠치올", "펩타이드", "세라마이드", "나이아신아마이드", "레티놀"]
        )

        target_age = st.multiselect(
            "타겟 연령층",
            ["20대", "30대", "40대", "50대+"],
            default=["30대", "40대"]
        )

        price_range = st.select_slider(
            "가격대",
            options=["저가", "중저가", "중가", "중고가", "고가", "프리미엄"],
            value="중고가"
        )

        simulate_btn = st.button("🚀 시뮬레이션 실행", use_container_width=True)

    with col2:
        if simulate_btn:
            with st.spinner("AI 시뮬레이션 중..."):
                import time
                time.sleep(1)  # 시뮬레이션 효과

                # 성공 확률 계산 (시뮬레이션)
                base_score = 60

                # 성분 점수
                ingredient_scores = {
                    "바쿠치올": 25, "펩타이드": 20, "세라마이드": 18,
                    "나이아신아마이드": 15, "레티놀": 10
                }
                score = base_score + ingredient_scores.get(main_ingredient, 10)

                # 가격대 조정
                price_adj = {"저가": -5, "중저가": 0, "중가": 5, "중고가": 8, "고가": 5, "프리미엄": 0}
                score += price_adj.get(price_range, 0)

                # 랜덤 요소
                score += random.randint(-5, 5)
                score = min(max(score, 0), 100)

                # 결과 표시
                st.markdown("#### 📊 시뮬레이션 결과")

                # 게이지 차트
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "시장 성공 확률"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#667eea"},
                        'steps': [
                            {'range': [0, 40], 'color': "#fee2e2"},
                            {'range': [40, 70], 'color': "#fef3c7"},
                            {'range': [70, 100], 'color': "#d1fae5"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 70
                        }
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

                # 상세 분석
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("##### 강점")
                    st.markdown(f"- ✅ {main_ingredient} 트렌드 상승세")
                    st.markdown(f"- ✅ {category} 시장 성장 중")
                with col_b:
                    st.markdown("##### 개선 권장")
                    st.markdown("- 💡 인플루언서 마케팅 강화")
                    st.markdown("- 💡 샘플 배포 캠페인")

                # 예상 매출
                st.markdown("---")
                st.markdown("##### 💰 예상 매출 (출시 1년)")
                estimated_revenue = score * 50  # 억 단위
                st.metric("예상 매출", f"{estimated_revenue}억 원", f"점유율 {score/10:.1f}%")
        else:
            st.info("👈 왼쪽에서 제품 정보를 입력하고 시뮬레이션을 실행하세요.")

# ============================================================
# TAB 6: AI 챗봇
# ============================================================
with tab6:
    st.markdown("### 💬 AI 트렌드 어시스턴트")
    st.markdown("BeautyTrend AI에게 뷰티 트렌드에 대해 질문하세요")

    # 챗봇 응답 데이터베이스
    chatbot_responses = {
        "바쿠치올": """
**🧪 바쿠치올 (Bakuchiol) 트렌드 분석**

바쿠치올은 현재 뷰티 업계에서 가장 주목받는 성분 중 하나입니다.

📊 **핵심 데이터**
- 소셜 미디어 언급량: 28,000+ (월간)
- 성장률: +312% (YoY)
- 감성 점수: 0.91 (매우 긍정)

🎯 **주요 타겟**
- 민감성 피부를 가진 25-40세 여성
- 레티놀 부작용 경험자
- 클린뷰티 선호층

💡 **추천 전략**
레티놀 대체 안티에이징 라인 출시를 적극 권장합니다.
        """,
        "트렌드": """
**📈 2025-2026 뷰티 메가 트렌드**

1️⃣ **슬로우에이징** (+267%)
   - 급진적 안티에이징에서 자연스러운 노화 관리로 전환

2️⃣ **스킨미니멀리즘** (+189%)
   - 복잡한 루틴 → 효과적인 멀티 기능 제품

3️⃣ **글래스스킨** (+245%)
   - 투명하고 건강한 피부 광채 추구

4️⃣ **클린뷰티 2.0** (+134%)
   - 성분 투명성 + 지속가능한 패키징

🎯 **전략 제안**: 바쿠치올 기반 슬로우에이징 라인 Q1 2025 출시 권장
        """,
        "펩타이드": """
**🔬 펩타이드 (Peptide) 분석**

펩타이드는 콜라겐 생성 촉진 효과로 안티에이징 시장의 핵심 성분입니다.

📊 **시장 데이터**
- 언급량: 38,000+ (월간)
- 성장률: +178% (YoY)
- 감성 점수: 0.88

🎯 **핵심 타겟**
- 30-50대 안티에이징 관심층
- 과학적 근거 중시 소비자

💊 **주목 펩타이드 종류**
- 아르지렐린 (보톡스 대안)
- 마트릭실 (콜라겐 합성)
- 코퍼 펩타이드 (상처 치유)
        """,
        "경쟁사": """
**🏢 경쟁사 동향 분석**

**에스티로더**
- Advanced Night Repair 2.0 출시 예정 (2025.02)
- 핵심 성분: 크로노럭신

**시세이도**
- Ultimune Power Infusing 4.0 (2025.01)
- 핵심 성분: ImuGeneration

**로레알**
- Revitalift Laser X4 (2025.03)
- 핵심 성분: 레티놀

🎯 **시사점**: 바쿠치올 기반 제품으로 레티놀 대안 시장 선점 기회
        """,
        "컬러": """
**🎨 2025 컬러 트렌드**

**TOP 3 상승 컬러**
1. Nude Beige (+61%) - 올시즌 스테디셀러
2. Dusty Rose (+55%) - 자연스러운 뉴트럴
3. Mauve (+52%) - 2025 S/S 키 컬러

**시즌별 추천**
- S/S 2025: Soft Pink, Coral, Mauve
- F/W 2025: Terracotta, Brick Red, Berry

💄 **립 제품 추천**: Dusty Rose 계열 MLBB 라인
        """
    }

    # 예시 질문 버튼
    st.markdown("##### 💡 추천 질문")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("바쿠치올 전망은?"):
            st.session_state['chat_input'] = "바쿠치올"
    with col2:
        if st.button("2025 트렌드는?"):
            st.session_state['chat_input'] = "트렌드"
    with col3:
        if st.button("경쟁사 동향"):
            st.session_state['chat_input'] = "경쟁사"
    with col4:
        if st.button("컬러 트렌드"):
            st.session_state['chat_input'] = "컬러"

    st.markdown("---")

    # 사용자 입력
    default_input = st.session_state.get('chat_input', '')
    user_input = st.text_input(
        "질문을 입력하세요",
        value=default_input,
        placeholder="예: 바쿠치올 시장 전망은 어떤가요?"
    )

    if user_input:
        # 응답 생성
        response = """
안녕하세요! BeautyTrend AI입니다. 🤖

궁금하신 내용에 대해 더 자세히 알려드리기 위해, 다음 키워드로 질문해주세요:
- **바쿠치올**: 성분 트렌드 분석
- **트렌드**: 2025-2026 메가 트렌드
- **펩타이드**: 안티에이징 성분
- **경쟁사**: 경쟁사 신제품 동향
- **컬러**: 컬러 트렌드 분석
        """

        for key, val in chatbot_responses.items():
            if key in user_input:
                response = val
                break

        st.markdown(response)

        # 세션 상태 초기화
        if 'chat_input' in st.session_state:
            del st.session_state['chat_input']

# ============================================================
# 푸터
# ============================================================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("💄 **BeautyTrend AI** v3.0")
with col2:
    st.markdown("🤖 Multi-Agent 기반 트렌드 예측")
with col3:
    st.markdown("🏆 **AI INNOVATION CHALLENGE 2026**")
