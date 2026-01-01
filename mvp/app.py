# -*- coding: utf-8 -*-
"""
BeautyTrend AI - MVP v4.0 (Multi-Agent System)
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
import asyncio
import nest_asyncio
nest_asyncio.apply()

# Multi-Agent System 임포트
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from agents import (
        OrchestratorAgent,
        DataFetchAgent,
        TrendModelAgent,
        ColorAnalysisAgent,
        CompetitorAgent,
        AgentStatus
    )
    AGENTS_AVAILABLE = True
except ImportError as e:
    AGENTS_AVAILABLE = False
    print(f"Warning: Could not import agents: {e}")

# v4.0 - Multi-Agent 시스템 통합

# 페이지 설정
st.set_page_config(
    page_title="BeautyTrend AI",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# Multi-Agent 시스템 초기화
# ============================================================
@st.cache_resource
def initialize_agents():
    """에이전트 시스템 초기화 (캐시됨)"""
    if not AGENTS_AVAILABLE:
        print("Warning: Agents not available")
        return None

    try:
        # API 키 가져오기 (Streamlit secrets 또는 환경변수)
        api_key = None
        try:
            api_key = st.secrets.get("ANTHROPIC_API_KEY", None)
        except Exception:
            api_key = os.getenv("ANTHROPIC_API_KEY")

        # 오케스트레이터 생성
        orchestrator = OrchestratorAgent(api_key=api_key)

        # 서브 에이전트 등록
        orchestrator.register_agent("data_fetch", DataFetchAgent())
        orchestrator.register_agent("trend_model", TrendModelAgent())
        orchestrator.register_agent("color_analysis", ColorAnalysisAgent())
        orchestrator.register_agent("competitor", CompetitorAgent())

        print(f"Agents initialized successfully. API key: {'set' if api_key else 'not set'}")
        return orchestrator
    except Exception as e:
        print(f"Error initializing agents: {e}")
        return None

# 에이전트 초기화 (캐시 리소스 사용)
_orchestrator = initialize_agents()

# 세션 상태 초기화
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

if 'agent_logs' not in st.session_state:
    st.session_state.agent_logs = []

def get_orchestrator():
    """오케스트레이터 가져오기"""
    return _orchestrator

def run_agent_async(agent, task, context=None):
    """에이전트 비동기 실행 래퍼"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(agent.execute(task, context))
        return result
    finally:
        loop.close()

# ============================================================
# 향상된 CSS 스타일
# ============================================================
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    }

    /* 메인 헤더 */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 10px 0;
        letter-spacing: -0.02em;
    }

    .sub-header {
        text-align: center;
        color: rgba(255,255,255,0.7);
        font-size: 1.1rem;
        margin-bottom: 20px;
    }

    /* 메트릭 카드 스타일 개선 */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }

    [data-testid="stMetricLabel"] {
        color: rgba(255,255,255,0.8) !important;
        font-size: 0.9rem !important;
    }

    [data-testid="stMetricValue"] {
        color: #fff !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricDelta"] {
        color: #10b981 !important;
    }

    /* 인사이트 박스 */
    .insight-box {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-left: 4px solid #667eea;
        padding: 20px 25px;
        border-radius: 0 16px 16px 0;
        margin: 15px 0;
        backdrop-filter: blur(10px);
    }

    .insight-box strong {
        color: #c4b5fd;
        font-size: 1.1rem;
    }

    .insight-box br + * {
        color: rgba(255,255,255,0.8);
    }

    /* 에이전트 배지 */
    .agent-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 25px;
        font-size: 0.85rem;
        margin: 5px 3px;
        font-weight: 500;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
    }

    /* 섹션 헤더 */
    .section-header {
        color: #fff;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
    }

    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.05);
        padding: 10px;
        border-radius: 16px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 12px 24px;
        color: rgba(255,255,255,0.7);
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }

    /* 사이드바 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(102, 126, 234, 0.2);
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: rgba(255,255,255,0.8);
    }

    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }

    /* 셀렉트박스 */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
    }

    /* 텍스트 인풋 */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        color: white;
    }

    /* 데이터프레임 */
    .stDataFrame {
        background: rgba(255,255,255,0.02);
        border-radius: 12px;
        overflow: hidden;
    }

    /* 구분선 */
    hr {
        border-color: rgba(102, 126, 234, 0.2);
        margin: 30px 0;
    }

    /* 푸터 스타일 */
    .footer-container {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 16px;
        padding: 20px;
        margin-top: 40px;
        text-align: center;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }

    /* 컬러 카드 */
    .color-card {
        border-radius: 12px;
        padding: 15px;
        margin: 8px 0;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }

    .color-card:hover {
        transform: scale(1.02);
    }

    /* 성공/정보/경고 알림 */
    .stSuccess, .stInfo, .stWarning {
        border-radius: 12px;
    }

    /* 스피너 */
    .stSpinner > div {
        border-color: #667eea;
    }

    /* 히든 Streamlit 브랜딩 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* 스크롤바 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.5);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.7);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 데이터 정의
# ============================================================
@st.cache_data
def load_data():
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

    historical_data = {
        "ingredient_trends": {
            "세라마이드": [{"month": f"2025-{i:02d}", "mentions": int(12000 + i*3000 + random.randint(-1000, 1000))} for i in range(1, 13)],
            "바쿠치올": [{"month": f"2025-{i:02d}", "mentions": int(2000 + i*2500 + random.randint(-500, 500))} for i in range(1, 13)],
            "펩타이드": [{"month": f"2025-{i:02d}", "mentions": int(8000 + i*2500 + random.randint(-800, 800))} for i in range(1, 13)],
            "나이아신아마이드": [{"month": f"2025-{i:02d}", "mentions": int(15000 + i*2000 + random.randint(-1000, 1000))} for i in range(1, 13)],
            "레티놀": [{"month": f"2025-{i:02d}", "mentions": int(20000 + i*1500 + random.randint(-1200, 1200))} for i in range(1, 13)]
        }
    }

    color_trends = [
        {"color": "Soft Pink", "hex": "#FFB6C1", "growth": 45, "season": "S/S 2026"},
        {"color": "Terracotta", "hex": "#E2725B", "growth": 38, "season": "F/W 2026"},
        {"color": "Mauve", "hex": "#E0B0FF", "growth": 52, "season": "S/S 2026"},
        {"color": "Brick Red", "hex": "#CB4154", "growth": 28, "season": "F/W 2026"},
        {"color": "Nude Beige", "hex": "#F5DEB3", "growth": 61, "season": "All Season"},
        {"color": "Berry", "hex": "#8E4585", "growth": 33, "season": "F/W 2026"},
        {"color": "Coral", "hex": "#FF7F50", "growth": 47, "season": "S/S 2026"},
        {"color": "Dusty Rose", "hex": "#DCAE96", "growth": 55, "season": "All Season"}
    ]

    competitor_data = [
        {"brand": "에스티로더", "product": "Advanced Night Repair 3.0", "launch": "2026-02", "category": "세럼", "key_ingredient": "크로노럭신 NEO"},
        {"brand": "로레알", "product": "Revitalift Laser X5", "launch": "2026-03", "category": "크림", "key_ingredient": "프로-레티놀"},
        {"brand": "시세이도", "product": "Ultimune Power Infusing 5.0", "launch": "2026-01", "category": "세럼", "key_ingredient": "ImuGeneration RED"},
        {"brand": "SK-II", "product": "GenOptics Aura Essence 2026", "launch": "2026-04", "category": "에센스", "key_ingredient": "피테라 크리스탈"},
        {"brand": "랑콤", "product": "Absolue Rich Cream 2026", "launch": "2026-02", "category": "크림", "key_ingredient": "그랑로즈 엑스트랙트"}
    ]

    return tiktok_data, historical_data, color_trends, competitor_data

tiktok_data, historical_data, color_trends, competitor_data = load_data()

# ============================================================
# 예측 함수
# ============================================================
def advanced_forecast(data, periods=6):
    values = np.array([d['mentions'] for d in data])
    n = len(values)
    x = np.arange(n)
    z = np.polyfit(x, values, 2)
    trend = np.poly1d(z)
    residuals = values - trend(x)
    seasonal_amplitude = np.std(residuals) * 0.5
    future_x = np.arange(n, n + periods)
    predictions = trend(future_x)
    seasonal = seasonal_amplitude * np.sin(2 * np.pi * future_x / 12)
    predictions = predictions + seasonal
    std_error = np.std(residuals)
    lower = predictions - 1.96 * std_error
    upper = predictions + 1.96 * std_error
    return predictions, lower, upper

# ============================================================
# 사이드바
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 3rem;">💄</div>
        <h2 style="color: #fff; margin: 10px 0;">BeautyTrend AI</h2>
        <p style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">글로벌 뷰티 트렌드 예측</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("##### 🤖 AI 에이전트")

    # 동적 에이전트 상태 표시
    orchestrator = get_orchestrator()
    if AGENTS_AVAILABLE and orchestrator:
        agent_info = [
            ("Orchestrator", orchestrator),
            ("Data Fetch", orchestrator.sub_agents.get("data_fetch")),
            ("Trend Model", orchestrator.sub_agents.get("trend_model")),
            ("Color Analysis", orchestrator.sub_agents.get("color_analysis")),
            ("Competitor", orchestrator.sub_agents.get("competitor"))
        ]
        for name, agent in agent_info:
            if agent:
                emoji = agent.get_status_emoji()
                st.markdown(f'<span class="agent-badge">{emoji} {name}</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="agent-badge">⚪ {name}</span>', unsafe_allow_html=True)
    else:
        agents = ["Orchestrator", "Data Fetch", "Trend Model", "Color Analysis", "Competitor"]
        for agent in agents:
            st.markdown(f'<span class="agent-badge">⚪ {agent}</span>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("##### 📊 데이터 소스")
    st.markdown("""
    <div style="color: rgba(255,255,255,0.7); font-size: 0.85rem; line-height: 1.8;">
    • TikTok API<br>
    • Instagram Graph API<br>
    • YouTube Data API<br>
    • 뷰티 커뮤니티
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="text-align: center; padding: 15px; background: rgba(102, 126, 234, 0.1); border-radius: 12px;">
        <div style="color: #c4b5fd; font-size: 0.8rem;">🏆 AI INNOVATION CHALLENGE</div>
        <div style="color: #fff; font-weight: 700; margin-top: 5px;">AGENT TRACK 2026</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 메인 헤더
# ============================================================
st.markdown('<h1 class="main-header">💄 BeautyTrend AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Multi-Agent 기반 글로벌 뷰티 트렌드 예측 시스템 | 실시간 분석 & 6~12개월 선행 예측</p>', unsafe_allow_html=True)

# ============================================================
# 탭 구성
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 대시보드",
    "🔮 트렌드 예측",
    "🎨 컬러 트렌드",
    "🏢 경쟁사 분석",
    "⚡ 시뮬레이션",
    "💬 AI 어시스턴트"
])

# ============================================================
# TAB 1: 대시보드
# ============================================================
with tab1:
    # 메트릭
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📱 분석 게시물", "158,234", "+12,543")
    with col2:
        st.metric("🔥 급상승 키워드", "#글래스스킨", "+245%")
    with col3:
        st.metric("🧪 주목 성분", "바쿠치올", "+312%")
    with col4:
        st.metric("😊 감성 점수", "0.84", "+0.05")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">🏷️ 해시태그 트렌드 TOP 8</div>', unsafe_allow_html=True)
        df_hashtag = pd.DataFrame(tiktok_data['hashtag_trends'])
        fig = px.bar(
            df_hashtag,
            x='count',
            y='tag',
            orientation='h',
            color='growth',
            color_continuous_scale='Viridis',
            hover_data=['region']
        )
        fig.update_layout(
            height=400,
            yaxis={'categoryorder': 'total ascending'},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            coloraxis_colorbar=dict(title="성장률 %")
        )
        fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">🧪 성분별 감성 분석</div>', unsafe_allow_html=True)
        df_ingredient = pd.DataFrame(tiktok_data['ingredient_mentions'])
        fig = px.scatter(
            df_ingredient,
            x='count',
            y='sentiment_avg',
            size='count',
            color='category',
            hover_name='name',
            size_max=50,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        fig.update_xaxes(title="언급량", showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        fig.update_yaxes(title="감성 점수", range=[0.65, 0.95], showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">💡 AI 인사이트</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="insight-box">
        <strong>🚀 급상승 트렌드 분석</strong><br><br>
        <span style="color: rgba(255,255,255,0.8);">바쿠치올이 레티놀 대안으로 급부상 중입니다. 민감성 피부 시장에서
        <span style="color: #10b981; font-weight: 600;">312% 성장률</span>을 보이며,
        특히 25-34세 여성층에서 높은 관심을 받고 있습니다.</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="insight-box">
        <strong>🎯 전략 추천</strong><br><br>
        <span style="color: rgba(255,255,255,0.8);">슬로우에이징 트렌드와 바쿠치올을 결합한 신제품 라인 개발을 권장합니다.
        <span style="color: #c4b5fd; font-weight: 600;">예상 시장 규모: 2026년 $2.3B</span> (YoY +45%)</span>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# TAB 2: 트렌드 예측
# ============================================================
with tab2:
    st.markdown('<div class="section-header">🔮 AI 기반 트렌드 예측</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("##### 분석 설정")
        ingredient = st.selectbox("성분 선택", list(historical_data['ingredient_trends'].keys()))
        forecast_period = st.slider("예측 기간 (개월)", 3, 12, 6)

        st.markdown("---")
        st.markdown("##### 📈 분석 정보")
        st.markdown(f"**선택 성분**: {ingredient}")
        st.markdown(f"**예측 기간**: {forecast_period}개월")

    data = historical_data['ingredient_trends'][ingredient]
    df = pd.DataFrame(data)
    df['month'] = pd.to_datetime(df['month'])
    predictions, lower, upper = advanced_forecast(data, forecast_period)
    future_dates = [df['month'].max() + timedelta(days=30*(i+1)) for i in range(forecast_period)]
    current_value = df['mentions'].iloc[-1]
    predicted_value = predictions[-1]
    growth = ((predicted_value - current_value) / current_value) * 100

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['month'], y=df['mentions'],
            mode='lines+markers', name='실제 데이터',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8, symbol='circle')
        ))
        fig.add_trace(go.Scatter(
            x=future_dates, y=predictions,
            mode='lines+markers', name='AI 예측',
            line=dict(color='#f093fb', width=3, dash='dash'),
            marker=dict(size=8, symbol='diamond')
        ))
        fig.add_trace(go.Scatter(
            x=future_dates + future_dates[::-1],
            y=list(upper) + list(lower[::-1]),
            fill='toself', fillcolor='rgba(240, 147, 251, 0.15)',
            line=dict(color='rgba(255,255,255,0)'),
            name='95% 신뢰구간'
        ))
        fig.update_layout(
            height=450, title=f"{ingredient} 트렌드 예측",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            hovermode='x unified'
        )
        fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("현재 언급량", f"{int(current_value):,}")
    with col2:
        st.metric(f"{forecast_period}개월 후 예측", f"{int(predicted_value):,}", f"{growth:+.1f}%")
    with col3:
        if growth > 50:
            st.success("🚀 **적극 투자 추천**")
        elif growth > 20:
            st.info("📈 **관심 유지 권장**")
        else:
            st.warning("👀 **시장 관망**")

# ============================================================
# TAB 3: 컬러 트렌드
# ============================================================
with tab3:
    st.markdown('<div class="section-header">🎨 2026 컬러 트렌드 분석</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        df_color = pd.DataFrame(color_trends)
        fig = go.Figure()
        for i, row in df_color.iterrows():
            fig.add_trace(go.Bar(
                x=[row['growth']], y=[row['color']],
                orientation='h', marker_color=row['hex'],
                name=row['color'],
                text=f"+{row['growth']}%", textposition='outside',
                hovertemplate=f"<b>{row['color']}</b><br>성장률: +{row['growth']}%<br>시즌: {row['season']}<extra></extra>"
            ))
        fig.update_layout(
            height=450, title="컬러별 성장률 (%)",
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            yaxis={'categoryorder': 'total ascending'}
        )
        fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("##### 🔝 TOP 3 트렌드 컬러")
        for _, row in df_color.nlargest(3, 'growth').iterrows():
            text_color = 'white' if row['hex'] in ['#8E4585', '#CB4154', '#E2725B'] else '#333'
            st.markdown(f"""
            <div class="color-card" style="background: {row['hex']}; color: {text_color};">
                <div style="font-size: 1.1rem;">{row['color']}</div>
                <div style="font-size: 0.85rem; opacity: 0.9;">+{row['growth']}% | {row['season']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### 💄 제품 카테고리 추천")
        st.markdown("• 립스틱 / 립글로스")
        st.markdown("• 블러셔 / 치크")
        st.markdown("• 아이섀도우 팔레트")

# ============================================================
# TAB 4: 경쟁사 분석
# ============================================================
with tab4:
    st.markdown('<div class="section-header">🏢 경쟁사 신제품 모니터링</div>', unsafe_allow_html=True)

    df_competitor = pd.DataFrame(competitor_data)

    # 카드 형식으로 표시
    cols = st.columns(len(df_competitor))
    for idx, (_, row) in enumerate(df_competitor.iterrows()):
        with cols[idx]:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); border-radius: 16px; padding: 20px; text-align: center; border: 1px solid rgba(102, 126, 234, 0.2); height: 200px;">
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.5);">{row['launch']}</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #fff; margin: 10px 0;">{row['brand']}</div>
                <div style="font-size: 0.85rem; color: #c4b5fd; margin-bottom: 10px;">{row['product']}</div>
                <div style="background: rgba(102, 126, 234, 0.2); padding: 5px 10px; border-radius: 20px; display: inline-block; font-size: 0.75rem;">
                    {row['category']} | {row['key_ingredient']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="insight-box">
        <strong>🔍 경쟁 분석 인사이트</strong><br><br>
        <span style="color: rgba(255,255,255,0.8);">에스티로더와 시세이도가 2026년 초 프리미엄 세럼 라인 강화 예정.
        레티놀 대체 성분과 피부 장벽 강화 성분이 주요 트렌드로 부상.</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="insight-box">
        <strong>🎯 대응 전략 제안</strong><br><br>
        <span style="color: rgba(255,255,255,0.8);">바쿠치올 기반 안티에이징 세럼으로 시장 선점 기회.
        Q1 2026 출시 타겟으로 개발 가속화를 권장합니다.</span>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# TAB 5: 시뮬레이션
# ============================================================
with tab5:
    st.markdown('<div class="section-header">⚡ 신제품 성공 시뮬레이션</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("##### 제품 정보 입력")
        product_name = st.text_input("제품명", "뉴 바쿠치올 세럼")
        category = st.selectbox("카테고리", ["세럼", "크림", "에센스", "토너", "마스크팩"])
        main_ingredient = st.selectbox("주요 성분", ["바쿠치올", "펩타이드", "세라마이드", "나이아신아마이드", "레티놀"])
        target_age = st.multiselect("타겟 연령층", ["20대", "30대", "40대", "50대+"], default=["30대", "40대"])
        price_range = st.select_slider("가격대", options=["저가", "중저가", "중가", "중고가", "고가", "프리미엄"], value="중고가")
        simulate_btn = st.button("🚀 시뮬레이션 실행", use_container_width=True)

    with col2:
        if simulate_btn:
            with st.spinner("AI 분석 중..."):
                import time
                time.sleep(1)

                base_score = 60
                ingredient_scores = {"바쿠치올": 25, "펩타이드": 20, "세라마이드": 18, "나이아신아마이드": 15, "레티놀": 10}
                score = base_score + ingredient_scores.get(main_ingredient, 10)
                price_adj = {"저가": -5, "중저가": 0, "중가": 5, "중고가": 8, "고가": 5, "프리미엄": 0}
                score += price_adj.get(price_range, 0)
                score += random.randint(-5, 5)
                score = min(max(score, 0), 100)

                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "시장 성공 확률", 'font': {'color': 'white'}},
                    number={'font': {'color': 'white', 'size': 60}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': 'white'},
                        'bar': {'color': "#667eea"},
                        'bgcolor': 'rgba(255,255,255,0.1)',
                        'steps': [
                            {'range': [0, 40], 'color': "rgba(239, 68, 68, 0.3)"},
                            {'range': [40, 70], 'color': "rgba(234, 179, 8, 0.3)"},
                            {'range': [70, 100], 'color': "rgba(16, 185, 129, 0.3)"}
                        ]
                    }
                ))
                fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                st.plotly_chart(fig, use_container_width=True)

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("##### ✅ 강점")
                    st.markdown(f"• {main_ingredient} 트렌드 상승세")
                    st.markdown(f"• {category} 시장 성장 중")
                with col_b:
                    st.markdown("##### 💡 개선 권장")
                    st.markdown("• 인플루언서 마케팅 강화")
                    st.markdown("• 샘플링 캠페인 진행")

                st.markdown("---")
                estimated_revenue = score * 50
                st.metric("💰 예상 매출 (1년)", f"{estimated_revenue}억 원", f"점유율 {score/10:.1f}%")
        else:
            st.markdown("""
            <div style="text-align: center; padding: 80px 20px; color: rgba(255,255,255,0.5);">
                <div style="font-size: 4rem; margin-bottom: 20px;">🎯</div>
                <div>왼쪽에서 제품 정보를 입력하고<br>시뮬레이션을 실행하세요</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# TAB 6: AI 챗봇 (Multi-Agent 기반)
# ============================================================
with tab6:
    st.markdown('<div class="section-header">💬 AI 트렌드 어시스턴트</div>', unsafe_allow_html=True)

    # 에이전트 상태 표시
    tab6_orchestrator = get_orchestrator()
    if AGENTS_AVAILABLE and tab6_orchestrator:
        has_api = tab6_orchestrator.client is not None
        if has_api:
            st.success("🤖 Claude API 연결됨 - 실시간 AI 분석 가능")
        else:
            st.info("🤖 규칙 기반 모드 - API 키 설정 시 고급 기능 활성화")
    else:
        st.warning("⚠️ 에이전트 시스템 로딩 중...")

    # 추천 질문 버튼
    st.markdown("##### 💡 추천 질문")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("🧪 바쿠치올", key="btn_bakuchiol", use_container_width=True):
            st.session_state['pending_query'] = "바쿠치올 트렌드 분석해줘"
    with col2:
        if st.button("📈 트렌드", key="btn_trend", use_container_width=True):
            st.session_state['pending_query'] = "2026년 뷰티 트렌드 전망"
    with col3:
        if st.button("🎨 컬러", key="btn_color", use_container_width=True):
            st.session_state['pending_query'] = "2026 컬러 트렌드 분석"
    with col4:
        if st.button("🏢 경쟁사", key="btn_competitor", use_container_width=True):
            st.session_state['pending_query'] = "경쟁사 신제품 분석"
    with col5:
        if st.button("📊 종합", key="btn_comprehensive", use_container_width=True):
            st.session_state['pending_query'] = "종합 트렌드 리포트 생성"

    st.markdown("---")

    # 대화 입력
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        pending = st.session_state.get('pending_query', '')
        user_query = st.text_input(
            "질문을 입력하세요",
            value=pending,
            placeholder="예: 바쿠치올 시장 전망은? / 경쟁사 신제품 분석해줘",
            key="chat_input_field"
        )
    with col_btn:
        send_btn = st.button("전송", type="primary", use_container_width=True)

    # 대화 처리
    if send_btn and user_query:
        # pending_query 초기화
        if 'pending_query' in st.session_state:
            del st.session_state['pending_query']

        # 메시지 저장
        st.session_state.chat_messages.append({"role": "user", "content": user_query})

        # 에이전트 실행
        with st.spinner("🤖 AI 에이전트 분석 중..."):
            chat_orchestrator = get_orchestrator()
            if AGENTS_AVAILABLE and chat_orchestrator:
                try:
                    response = run_agent_async(chat_orchestrator, user_query)
                    agent_response = response.message

                    # 에이전트 로그 저장
                    st.session_state.agent_logs.append({
                        "timestamp": datetime.now().isoformat(),
                        "query": user_query,
                        "agents_used": response.data.get("agents_used", []) if response.data else [],
                        "execution_time": response.execution_time
                    })
                except Exception as e:
                    agent_response = f"처리 중 오류가 발생했습니다: {str(e)}"
            else:
                agent_response = """## 👋 BeautyTrend AI 입니다!

현재 에이전트 시스템이 초기화 중입니다.
잠시 후 다시 시도해 주세요.

**지원 기능:**
- 성분 트렌드 분석 (바쿠치올, 펩타이드 등)
- 2026 뷰티 메가 트렌드
- 컬러 트렌드 분석
- 경쟁사 신제품 모니터링
"""

        st.session_state.chat_messages.append({"role": "assistant", "content": agent_response})

    # 대화 히스토리 표시
    st.markdown("### 💬 대화")
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_messages[-10:]:  # 최근 10개만 표시
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="background: rgba(102, 126, 234, 0.2); border-radius: 12px; padding: 15px; margin: 10px 0; border-left: 4px solid #667eea;">
                    <strong>👤 사용자</strong><br>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; margin: 10px 0; border-left: 4px solid #10b981;">
                    <strong>🤖 BeautyTrend AI</strong>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(msg["content"])

    # 대화 초기화 버튼
    col_clear, col_export = st.columns(2)
    with col_clear:
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state.chat_messages = []
            clear_orchestrator = get_orchestrator()
            if clear_orchestrator:
                clear_orchestrator.clear_history()
            st.rerun()

    with col_export:
        if st.button("📥 에이전트 로그", use_container_width=True):
            if st.session_state.agent_logs:
                st.json(st.session_state.agent_logs[-5:])
            else:
                st.info("아직 로그가 없습니다.")

# ============================================================
# 푸터
# ============================================================
st.markdown("---")
st.markdown("""
<div class="footer-container">
    <div style="font-size: 1.5rem; margin-bottom: 10px;">💄 BeautyTrend AI <span style="font-size: 0.9rem; color: rgba(255,255,255,0.5);">v4.0</span></div>
    <div style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">Multi-Agent 기반 글로벌 뷰티 트렌드 예측 시스템</div>
    <div style="margin-top: 15px;">
        <span style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 5px 15px; border-radius: 20px; font-size: 0.8rem;">🏆 AI INNOVATION CHALLENGE 2026</span>
    </div>
</div>
""", unsafe_allow_html=True)
