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
# 럭셔리 뷰티 에디토리얼 CSS 스타일 (frontend-design skill 적용)
# ============================================================
st.markdown("""
<style>
    /* ========================================
       FONTS - Distinctive Typography
       ======================================== */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Outfit:wght@300;400;500;600;700&display=swap');

    :root {
        /* 럭셔리 뷰티 컬러 팔레트 */
        --color-cream: #FAF7F2;
        --color-champagne: #F5E6D3;
        --color-gold: #C9A962;
        --color-gold-light: #E8D5A8;
        --color-rose: #E8D5D3;
        --color-rose-deep: #D4A5A5;
        --color-burgundy: #722F37;
        --color-burgundy-light: #8B4049;
        --color-charcoal: #1A1A1A;
        --color-charcoal-soft: #2D2D2D;
        --color-warm-gray: #6B6560;
        --color-text-light: #F5F0EB;
        --color-text-muted: rgba(245, 240, 235, 0.7);

        /* 그라데이션 */
        --gradient-gold: linear-gradient(135deg, #C9A962 0%, #E8D5A8 50%, #C9A962 100%);
        --gradient-rose: linear-gradient(135deg, #E8D5D3 0%, #D4A5A5 100%);
        --gradient-dark: linear-gradient(180deg, #1A1A1A 0%, #2D2D2D 50%, #1A1A1A 100%);
        --gradient-glass: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);

        /* 타이포그래피 */
        --font-display: 'Cormorant Garamond', Georgia, serif;
        --font-body: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;

        /* 쉐도우 */
        --shadow-soft: 0 4px 24px rgba(0,0,0,0.12);
        --shadow-elevated: 0 12px 48px rgba(0,0,0,0.2);
        --shadow-glow-gold: 0 0 40px rgba(201,169,98,0.15);
    }

    /* ========================================
       GLOBAL STYLES
       ======================================== */
    .stApp {
        background: var(--gradient-dark);
        font-family: var(--font-body);
    }

    /* 노이즈 텍스처 오버레이 */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
        opacity: 0.03;
        pointer-events: none;
        z-index: 0;
    }

    /* ========================================
       MAIN HEADER - Editorial Style
       ======================================== */
    .main-header {
        font-family: var(--font-display);
        font-size: 4rem;
        font-weight: 300;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        background: var(--gradient-gold);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 30px 0 10px 0;
        animation: fadeInUp 1s ease-out;
    }

    .sub-header {
        font-family: var(--font-body);
        text-align: center;
        color: var(--color-text-muted);
        font-size: 1rem;
        font-weight: 300;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 40px;
        animation: fadeInUp 1s ease-out 0.2s backwards;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* ========================================
       METRIC CARDS - Glass Morphism
       ======================================== */
    [data-testid="stMetric"] {
        background: var(--gradient-glass);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(201,169,98,0.15);
        border-radius: 20px;
        padding: 24px;
        box-shadow: var(--shadow-soft);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.8s ease-out backwards;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-elevated), var(--shadow-glow-gold);
        border-color: rgba(201,169,98,0.3);
    }

    [data-testid="stMetricLabel"] {
        font-family: var(--font-body) !important;
        color: var(--color-text-muted) !important;
        font-size: 0.85rem !important;
        font-weight: 400 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
    }

    [data-testid="stMetricValue"] {
        font-family: var(--font-display) !important;
        color: var(--color-text-light) !important;
        font-weight: 400 !important;
        font-size: 1.8rem !important;
    }

    [data-testid="stMetricDelta"] {
        color: var(--color-gold) !important;
        font-weight: 500 !important;
    }

    /* ========================================
       INSIGHT BOXES - Elegant Cards
       ======================================== */
    .insight-box {
        background: linear-gradient(135deg, rgba(201,169,98,0.08) 0%, rgba(232,213,211,0.05) 100%);
        border-left: 3px solid var(--color-gold);
        padding: 28px 32px;
        border-radius: 0 20px 20px 0;
        margin: 20px 0;
        backdrop-filter: blur(10px);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: slideInLeft 0.8s ease-out backwards;
    }

    .insight-box:hover {
        background: linear-gradient(135deg, rgba(201,169,98,0.12) 0%, rgba(232,213,211,0.08) 100%);
        transform: translateX(8px);
    }

    .insight-box strong {
        font-family: var(--font-display);
        color: var(--color-gold-light);
        font-size: 1.25rem;
        font-weight: 500;
        letter-spacing: 0.02em;
    }

    .insight-box span {
        color: var(--color-text-muted);
        font-weight: 300;
        line-height: 1.7;
    }

    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* ========================================
       AGENT BADGES - Refined Pills
       ======================================== */
    .agent-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(201,169,98,0.2) 0%, rgba(201,169,98,0.1) 100%);
        color: var(--color-gold-light);
        padding: 10px 18px;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 500;
        letter-spacing: 0.03em;
        margin: 6px 4px;
        border: 1px solid rgba(201,169,98,0.2);
        transition: all 0.3s ease;
    }

    .agent-badge:hover {
        background: linear-gradient(135deg, rgba(201,169,98,0.3) 0%, rgba(201,169,98,0.2) 100%);
        border-color: rgba(201,169,98,0.4);
        transform: scale(1.02);
    }

    /* ========================================
       SECTION HEADERS - Editorial Typography
       ======================================== */
    .section-header {
        font-family: var(--font-display);
        color: var(--color-text-light);
        font-size: 1.8rem;
        font-weight: 400;
        letter-spacing: 0.03em;
        margin: 40px 0 24px 0;
        padding-bottom: 16px;
        border-bottom: 1px solid rgba(201,169,98,0.2);
        position: relative;
    }

    .section-header::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 60px;
        height: 2px;
        background: var(--gradient-gold);
    }

    /* ========================================
       TABS - Luxury Navigation
       ======================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(255,255,255,0.02);
        padding: 8px;
        border-radius: 16px;
        border: 1px solid rgba(201,169,98,0.1);
    }

    .stTabs [data-baseweb="tab"] {
        font-family: var(--font-body);
        background-color: transparent;
        border-radius: 12px;
        padding: 14px 28px;
        color: var(--color-text-muted);
        font-weight: 400;
        font-size: 0.9rem;
        letter-spacing: 0.02em;
        transition: all 0.3s ease;
        border: 1px solid transparent;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--color-text-light);
        background: rgba(201,169,98,0.08);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(201,169,98,0.2) 0%, rgba(201,169,98,0.1) 100%) !important;
        color: var(--color-gold-light) !important;
        border: 1px solid rgba(201,169,98,0.3) !important;
        font-weight: 500 !important;
    }

    /* ========================================
       SIDEBAR - Refined Panel
       ======================================== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1A1A 0%, #232323 100%);
        border-right: 1px solid rgba(201,169,98,0.1);
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: var(--color-text-muted);
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5 {
        font-family: var(--font-display) !important;
        color: var(--color-text-light) !important;
        letter-spacing: 0.05em !important;
    }

    /* ========================================
       BUTTONS - Luxury Interaction
       ======================================== */
    .stButton > button {
        font-family: var(--font-body);
        background: var(--gradient-gold);
        color: var(--color-charcoal);
        border: none;
        border-radius: 12px;
        padding: 14px 28px;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 16px rgba(201,169,98,0.25);
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 28px rgba(201,169,98,0.35);
        filter: brightness(1.05);
    }

    .stButton > button:active {
        transform: translateY(-1px);
    }

    /* ========================================
       FORM ELEMENTS - Refined Inputs
       ======================================== */
    /* 폼 레이블 스타일 - 가시성 향상 */
    .stSelectbox label,
    .stMultiSelect label,
    .stSlider label,
    .stTextInput label,
    .stNumberInput label,
    .stSelectSlider label,
    [data-testid="stWidgetLabel"] {
        color: #E8D5A8 !important;
        font-family: var(--font-body) !important;
        font-size: 0.9rem !important;
        font-weight: 400 !important;
        letter-spacing: 0.02em !important;
    }

    /* 슬라이더 숫자 값 */
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"],
    .stSlider div[data-testid="stThumbValue"] {
        color: #C9A962 !important;
    }

    /* 멀티셀렉트 태그/칩 스타일 */
    .stMultiSelect [data-baseweb="tag"] {
        background: linear-gradient(135deg, rgba(201,169,98,0.3) 0%, rgba(201,169,98,0.2) 100%) !important;
        border: 1px solid rgba(201,169,98,0.4) !important;
        color: #E8D5A8 !important;
    }

    .stMultiSelect [data-baseweb="tag"] span {
        color: #E8D5A8 !important;
    }

    /* Select Slider (Price Tier 등) */
    [data-testid="stTickBar"] span,
    .stSlider [data-baseweb="slider"] + div span {
        color: rgba(232, 213, 168, 0.8) !important;
    }

    /* 일반 텍스트 p 태그 */
    .stMarkdown p {
        color: rgba(245, 240, 235, 0.85);
    }

    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(201,169,98,0.2);
        border-radius: 12px;
        transition: all 0.3s ease;
    }

    .stSelectbox > div > div:hover,
    .stMultiSelect > div > div:hover {
        border-color: rgba(201,169,98,0.4);
    }

    .stTextInput > div > div > input {
        font-family: var(--font-body);
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(201,169,98,0.2);
        border-radius: 12px;
        color: var(--color-text-light);
        padding: 14px 18px;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--color-gold);
        box-shadow: 0 0 0 2px rgba(201,169,98,0.1);
    }

    .stTextInput > div > div > input::placeholder {
        color: var(--color-warm-gray);
    }

    /* ========================================
       SLIDER - Gold Accent
       ======================================== */
    .stSlider > div > div > div > div {
        background: var(--color-gold) !important;
    }

    .stSlider > div > div > div[role="slider"] {
        background: var(--color-gold) !important;
        border: 3px solid var(--color-charcoal) !important;
    }

    /* 슬라이더 min/max 텍스트 */
    .stSlider p,
    .stSlider span {
        color: rgba(232, 213, 168, 0.8) !important;
    }

    /* ========================================
       DATAFRAME - Subtle Table
       ======================================== */
    .stDataFrame {
        background: rgba(255,255,255,0.02);
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(201,169,98,0.1);
    }

    /* ========================================
       DIVIDERS
       ======================================== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(201,169,98,0.3) 50%, transparent 100%);
        margin: 40px 0;
    }

    /* ========================================
       FOOTER - Signature Style
       ======================================== */
    .footer-container {
        background: linear-gradient(135deg, rgba(201,169,98,0.08) 0%, rgba(232,213,211,0.04) 100%);
        border-radius: 24px;
        padding: 40px;
        margin-top: 60px;
        text-align: center;
        border: 1px solid rgba(201,169,98,0.15);
        backdrop-filter: blur(10px);
    }

    /* ========================================
       COLOR CARDS - Premium Display
       ======================================== */
    .color-card {
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        font-weight: 500;
        box-shadow: var(--shadow-soft);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(255,255,255,0.1);
    }

    .color-card:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: var(--shadow-elevated);
    }

    /* ========================================
       ALERTS - Refined Notifications
       ======================================== */
    .stSuccess {
        background: linear-gradient(135deg, rgba(201,169,98,0.15) 0%, rgba(201,169,98,0.08) 100%) !important;
        border: 1px solid rgba(201,169,98,0.3) !important;
        border-radius: 12px !important;
        color: var(--color-gold-light) !important;
    }

    .stInfo {
        background: linear-gradient(135deg, rgba(232,213,211,0.15) 0%, rgba(232,213,211,0.08) 100%) !important;
        border: 1px solid rgba(232,213,211,0.3) !important;
        border-radius: 12px !important;
    }

    .stWarning {
        background: linear-gradient(135deg, rgba(114,47,55,0.15) 0%, rgba(114,47,55,0.08) 100%) !important;
        border: 1px solid rgba(114,47,55,0.3) !important;
        border-radius: 12px !important;
    }

    /* ========================================
       SPINNER - Gold Animation
       ======================================== */
    .stSpinner > div {
        border-color: var(--color-gold) !important;
        border-right-color: transparent !important;
    }

    /* ========================================
       HIDE STREAMLIT BRANDING
       ======================================== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ========================================
       SCROLLBAR - Minimal Luxury
       ======================================== */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.02);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(201,169,98,0.3);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(201,169,98,0.5);
    }

    /* ========================================
       PLOTLY CHART OVERRIDES
       ======================================== */
    .js-plotly-plot .plotly .modebar {
        background: transparent !important;
    }

    .js-plotly-plot .plotly .modebar-btn {
        color: var(--color-warm-gray) !important;
    }

    /* ========================================
       STAGGER ANIMATIONS
       ======================================== */
    [data-testid="stMetric"]:nth-child(1) { animation-delay: 0.1s; }
    [data-testid="stMetric"]:nth-child(2) { animation-delay: 0.2s; }
    [data-testid="stMetric"]:nth-child(3) { animation-delay: 0.3s; }
    [data-testid="stMetric"]:nth-child(4) { animation-delay: 0.4s; }

    .insight-box:nth-of-type(1) { animation-delay: 0.5s; }
    .insight-box:nth-of-type(2) { animation-delay: 0.7s; }

    /* ========================================
       RESPONSIVE ADJUSTMENTS
       ======================================== */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
            letter-spacing: 0.05em;
        }
        .sub-header {
            font-size: 0.85rem;
        }
        .section-header {
            font-size: 1.4rem;
        }
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
# 사이드바 - 럭셔리 에디토리얼 스타일
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 30px 0 20px 0;">
        <div style="font-family: 'Cormorant Garamond', serif; font-size: 1.5rem; font-weight: 300; letter-spacing: 0.08em; background: linear-gradient(135deg, #C9A962 0%, #E8D5A8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; white-space: nowrap;">BEAUTYTREND</div>
        <div style="font-family: 'Outfit', sans-serif; font-size: 0.65rem; letter-spacing: 0.2em; color: rgba(201,169,98,0.7); text-transform: uppercase;">AI Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; letter-spacing: 0.05em; color: #E8D5A8; margin-bottom: 12px;">Multi-Agent System</div>
    """, unsafe_allow_html=True)

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
                st.markdown(f'<span class="agent-badge">◇ {name}</span>', unsafe_allow_html=True)
    else:
        agents = ["Orchestrator", "Data Fetch", "Trend Model", "Color Analysis", "Competitor"]
        for agent in agents:
            st.markdown(f'<span class="agent-badge">◇ {agent}</span>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; letter-spacing: 0.05em; color: #E8D5A8; margin-bottom: 12px;">Data Sources</div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family: 'Outfit', sans-serif; color: rgba(245,240,235,0.6); font-size: 0.8rem; line-height: 2; letter-spacing: 0.02em;">
    <span style="color: #C9A962;">◆</span> TikTok API<br>
    <span style="color: #C9A962;">◆</span> Instagram Graph API<br>
    <span style="color: #C9A962;">◆</span> YouTube Data API<br>
    <span style="color: #C9A962;">◆</span> Beauty Communities
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="text-align: center; padding: 20px 16px; background: linear-gradient(135deg, rgba(201,169,98,0.1) 0%, rgba(201,169,98,0.05) 100%); border-radius: 16px; border: 1px solid rgba(201,169,98,0.15);">
        <div style="font-family: 'Outfit', sans-serif; font-size: 0.65rem; letter-spacing: 0.2em; color: rgba(201,169,98,0.8); text-transform: uppercase; margin-bottom: 8px;">Amorepacific</div>
        <div style="font-family: 'Cormorant Garamond', serif; font-size: 1rem; letter-spacing: 0.08em; color: #E8D5A8;">AI INNOVATION</div>
        <div style="font-family: 'Outfit', sans-serif; font-size: 0.75rem; letter-spacing: 0.15em; color: rgba(201,169,98,0.6); margin-top: 4px;">CHALLENGE 2026</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 메인 헤더 - 럭셔리 에디토리얼
# ============================================================
st.markdown('<h1 class="main-header">BeautyTrend AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Multi-Agent Intelligence · Global Beauty Forecasting · 6-12 Month Predictions</p>', unsafe_allow_html=True)

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
        st.markdown('<div class="section-header">Hashtag Trends · TOP 8</div>', unsafe_allow_html=True)
        df_hashtag = pd.DataFrame(tiktok_data['hashtag_trends'])
        # 럭셔리 컬러스케일: 샴페인 → 골드 → 버건디
        luxury_colorscale = [[0, '#E8D5D3'], [0.5, '#C9A962'], [1, '#722F37']]
        fig = px.bar(
            df_hashtag,
            x='count',
            y='tag',
            orientation='h',
            color='growth',
            color_continuous_scale=luxury_colorscale,
            hover_data=['region']
        )
        fig.update_layout(
            height=420,
            yaxis={'categoryorder': 'total ascending'},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#F5F0EB', family='Outfit'),
            coloraxis_colorbar=dict(
                title=dict(text="Growth %", font=dict(color='#C9A962')),
                tickfont=dict(color='rgba(245,240,235,0.7)')
            ),
            margin=dict(l=10, r=10, t=10, b=10)
        )
        fig.update_xaxes(showgrid=True, gridcolor='rgba(201,169,98,0.1)', tickfont=dict(color='rgba(245,240,235,0.6)'))
        fig.update_yaxes(showgrid=False, tickfont=dict(color='#E8D5A8'))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Ingredient Sentiment Analysis</div>', unsafe_allow_html=True)
        df_ingredient = pd.DataFrame(tiktok_data['ingredient_mentions'])
        # 럭셔리 컬러 팔레트
        luxury_colors = ['#C9A962', '#E8D5D3', '#D4A5A5', '#722F37']
        fig = px.scatter(
            df_ingredient,
            x='count',
            y='sentiment_avg',
            size='count',
            color='category',
            hover_name='name',
            size_max=55,
            color_discrete_sequence=luxury_colors
        )
        fig.update_layout(
            height=420,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#F5F0EB', family='Outfit'),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                font=dict(color='rgba(245,240,235,0.8)')
            ),
            margin=dict(l=10, r=10, t=10, b=10)
        )
        fig.update_xaxes(title=dict(text="Mentions", font=dict(color='#C9A962')), showgrid=True, gridcolor='rgba(201,169,98,0.1)', tickfont=dict(color='rgba(245,240,235,0.6)'))
        fig.update_yaxes(title=dict(text="Sentiment", font=dict(color='#C9A962')), range=[0.65, 0.95], showgrid=True, gridcolor='rgba(201,169,98,0.1)', tickfont=dict(color='rgba(245,240,235,0.6)'))
        fig.update_traces(marker=dict(line=dict(width=1, color='rgba(26,26,26,0.5)')))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">AI Intelligence Insights</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="insight-box">
        <strong>Rising Trend Analysis</strong><br><br>
        <span>Bakuchiol is rapidly emerging as a retinol alternative. Showing
        <span style="color: #C9A962; font-weight: 500;">+312% growth</span> in the sensitive skin market,
        with particularly high interest among women aged 25-34.</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="insight-box">
        <strong>Strategic Recommendation</strong><br><br>
        <span>We recommend developing a new product line combining slow-aging trends with Bakuchiol.
        <span style="color: #E8D5A8; font-weight: 500;">Projected market size: $2.3B in 2026</span> (YoY +45%)</span>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# TAB 2: 트렌드 예측 - 럭셔리 스타일
# ============================================================
with tab2:
    st.markdown('<div class="section-header">AI-Powered Trend Forecasting</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("""<div style="font-family: 'Cormorant Garamond', serif; font-size: 1.2rem; color: #E8D5A8; margin-bottom: 16px;">Analysis Settings</div>""", unsafe_allow_html=True)
        ingredient = st.selectbox("Select Ingredient", list(historical_data['ingredient_trends'].keys()))
        forecast_period = st.slider("Forecast Period (months)", 3, 12, 6)

        st.markdown("---")
        st.markdown("""<div style="font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; color: #E8D5A8; margin-bottom: 12px;">Analysis Info</div>""", unsafe_allow_html=True)
        st.markdown(f"<span style='color: rgba(245,240,235,0.7);'>Selected: </span><span style='color: #C9A962;'>{ingredient}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color: rgba(245,240,235,0.7);'>Period: </span><span style='color: #C9A962;'>{forecast_period} months</span>", unsafe_allow_html=True)

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
            mode='lines+markers', name='Historical Data',
            line=dict(color='#C9A962', width=3),
            marker=dict(size=9, symbol='circle', line=dict(width=2, color='#1A1A1A'))
        ))
        fig.add_trace(go.Scatter(
            x=future_dates, y=predictions,
            mode='lines+markers', name='AI Prediction',
            line=dict(color='#E8D5D3', width=3, dash='dash'),
            marker=dict(size=9, symbol='diamond', line=dict(width=2, color='#1A1A1A'))
        ))
        fig.add_trace(go.Scatter(
            x=future_dates + future_dates[::-1],
            y=list(upper) + list(lower[::-1]),
            fill='toself', fillcolor='rgba(201,169,98,0.1)',
            line=dict(color='rgba(255,255,255,0)'),
            name='95% Confidence'
        ))
        fig.update_layout(
            height=480,
            title=dict(
                text=f"{ingredient} Trend Forecast",
                font=dict(family='Cormorant Garamond', size=24, color='#E8D5A8')
            ),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#F5F0EB', family='Outfit'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color='rgba(245,240,235,0.8)')),
            hovermode='x unified',
            margin=dict(l=10, r=10, t=60, b=10)
        )
        fig.update_xaxes(showgrid=True, gridcolor='rgba(201,169,98,0.1)', tickfont=dict(color='rgba(245,240,235,0.6)'))
        fig.update_yaxes(showgrid=True, gridcolor='rgba(201,169,98,0.1)', tickfont=dict(color='rgba(245,240,235,0.6)'))
        st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Mentions", f"{int(current_value):,}")
    with col2:
        st.metric(f"{forecast_period}M Forecast", f"{int(predicted_value):,}", f"{growth:+.1f}%")
    with col3:
        if growth > 50:
            st.success("◆ **High Investment Priority**")
        elif growth > 20:
            st.info("◇ **Monitor Closely**")
        else:
            st.warning("○ **Market Watch**")

# ============================================================
# TAB 3: 컬러 트렌드 - 럭셔리 스타일
# ============================================================
with tab3:
    st.markdown('<div class="section-header">2026 Color Trend Analysis</div>', unsafe_allow_html=True)

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
                textfont=dict(color='#E8D5A8'),
                hovertemplate=f"<b>{row['color']}</b><br>Growth: +{row['growth']}%<br>Season: {row['season']}<extra></extra>",
                marker=dict(line=dict(width=1, color='rgba(26,26,26,0.3)'))
            ))
        fig.update_layout(
            height=480,
            title=dict(
                text="Color Growth Rate (%)",
                font=dict(family='Cormorant Garamond', size=22, color='#E8D5A8')
            ),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#F5F0EB', family='Outfit'),
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(l=10, r=60, t=60, b=10)
        )
        fig.update_xaxes(showgrid=True, gridcolor='rgba(201,169,98,0.1)', tickfont=dict(color='rgba(245,240,235,0.6)'))
        fig.update_yaxes(tickfont=dict(color='#E8D5A8'))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("""<div style="font-family: 'Cormorant Garamond', serif; font-size: 1.3rem; color: #E8D5A8; margin-bottom: 20px;">Top 3 Trending Colors</div>""", unsafe_allow_html=True)
        for _, row in df_color.nlargest(3, 'growth').iterrows():
            # 어두운 색상인지 확인
            text_color = '#1A1A1A' if row['hex'] in ['#FFB6C1', '#E0B0FF', '#F5DEB3', '#FF7F50', '#DCAE96'] else '#FAF7F2'
            st.markdown(f"""
            <div class="color-card" style="background: {row['hex']}; color: {text_color};">
                <div style="font-family: 'Cormorant Garamond', serif; font-size: 1.2rem; letter-spacing: 0.03em;">{row['color']}</div>
                <div style="font-family: 'Outfit', sans-serif; font-size: 0.8rem; opacity: 0.85; margin-top: 4px;">+{row['growth']}% · {row['season']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("""<div style="font-family: 'Cormorant Garamond', serif; font-size: 1.2rem; color: #E8D5A8; margin-bottom: 14px;">Product Categories</div>""", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family: 'Outfit', sans-serif; color: rgba(245,240,235,0.7); font-size: 0.9rem; line-height: 2;">
        <span style="color: #C9A962;">◆</span> Lipstick & Lip Gloss<br>
        <span style="color: #C9A962;">◆</span> Blush & Cheek<br>
        <span style="color: #C9A962;">◆</span> Eyeshadow Palette
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# TAB 4: 경쟁사 분석 - 럭셔리 스타일
# ============================================================
with tab4:
    st.markdown('<div class="section-header">Competitor Product Intelligence</div>', unsafe_allow_html=True)

    df_competitor = pd.DataFrame(competitor_data)

    # 카드 형식으로 표시
    cols = st.columns(len(df_competitor))
    for idx, (_, row) in enumerate(df_competitor.iterrows()):
        with cols[idx]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(201,169,98,0.05) 100%); border-radius: 20px; padding: 24px 16px; text-align: center; border: 1px solid rgba(201,169,98,0.15); height: 220px; transition: all 0.4s ease;">
                <div style="font-family: 'Outfit', sans-serif; font-size: 0.75rem; color: rgba(201,169,98,0.7); letter-spacing: 0.1em;">{row['launch']}</div>
                <div style="font-family: 'Cormorant Garamond', serif; font-size: 1.2rem; font-weight: 500; color: #E8D5A8; margin: 12px 0 8px 0; letter-spacing: 0.02em;">{row['brand']}</div>
                <div style="font-family: 'Outfit', sans-serif; font-size: 0.85rem; color: rgba(245,240,235,0.7); margin-bottom: 14px; line-height: 1.4;">{row['product']}</div>
                <div style="background: linear-gradient(135deg, rgba(201,169,98,0.2) 0%, rgba(201,169,98,0.1) 100%); padding: 8px 12px; border-radius: 20px; display: inline-block; font-size: 0.7rem; color: #C9A962; letter-spacing: 0.02em; border: 1px solid rgba(201,169,98,0.2);">
                    {row['category']} · {row['key_ingredient']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="insight-box">
        <strong>Competitive Analysis Insight</strong><br><br>
        <span>Estée Lauder and Shiseido are set to strengthen their premium serum lines in early 2026.
        Retinol alternatives and skin barrier-strengthening ingredients are emerging as key trends.</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="insight-box">
        <strong>Strategic Response</strong><br><br>
        <span>Market preemption opportunity with Bakuchiol-based anti-aging serum.
        We recommend accelerating development targeting Q1 2026 launch.</span>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# TAB 5: 시뮬레이션 - 럭셔리 스타일
# ============================================================
with tab5:
    st.markdown('<div class="section-header">Product Success Simulation</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("""<div style="font-family: 'Cormorant Garamond', serif; font-size: 1.2rem; color: #E8D5A8; margin-bottom: 16px;">Product Configuration</div>""", unsafe_allow_html=True)
        product_name = st.text_input("Product Name", "New Bakuchiol Serum")
        category = st.selectbox("Category", ["Serum", "Cream", "Essence", "Toner", "Mask Pack"])
        main_ingredient = st.selectbox("Key Ingredient", ["바쿠치올", "펩타이드", "세라마이드", "나이아신아마이드", "레티놀"])
        target_age = st.multiselect("Target Age", ["20s", "30s", "40s", "50s+"], default=["30s", "40s"])
        price_range = st.select_slider("Price Tier", options=["Budget", "Mid-Low", "Mid", "Mid-High", "Premium", "Luxury"], value="Mid-High")
        simulate_btn = st.button("◆ Run Simulation", use_container_width=True)

    with col2:
        if simulate_btn:
            with st.spinner("AI analyzing..."):
                import time
                time.sleep(1)

                base_score = 60
                ingredient_scores = {"바쿠치올": 25, "펩타이드": 20, "세라마이드": 18, "나이아신아마이드": 15, "레티놀": 10}
                score = base_score + ingredient_scores.get(main_ingredient, 10)
                price_adj = {"Budget": -5, "Mid-Low": 0, "Mid": 5, "Mid-High": 8, "Premium": 5, "Luxury": 0}
                score += price_adj.get(price_range, 0)
                score += random.randint(-5, 5)
                score = min(max(score, 0), 100)

                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Market Success Probability", 'font': {'family': 'Cormorant Garamond', 'color': '#E8D5A8', 'size': 22}},
                    number={'font': {'family': 'Cormorant Garamond', 'color': '#F5F0EB', 'size': 64}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': 'rgba(245,240,235,0.5)', 'tickfont': {'color': 'rgba(245,240,235,0.6)'}},
                        'bar': {'color': "#C9A962"},
                        'bgcolor': 'rgba(255,255,255,0.05)',
                        'bordercolor': 'rgba(201,169,98,0.3)',
                        'steps': [
                            {'range': [0, 40], 'color': "rgba(114,47,55,0.2)"},
                            {'range': [40, 70], 'color': "rgba(212,165,165,0.2)"},
                            {'range': [70, 100], 'color': "rgba(201,169,98,0.2)"}
                        ]
                    }
                ))
                fig.update_layout(height=380, paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#F5F0EB', family='Outfit'))
                st.plotly_chart(fig, use_container_width=True)

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("""<div style="font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; color: #C9A962; margin-bottom: 10px;">Strengths</div>""", unsafe_allow_html=True)
                    st.markdown(f"<span style='color: rgba(245,240,235,0.8);'>◆ {main_ingredient} trend rising</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color: rgba(245,240,235,0.8);'>◆ {category} market growing</span>", unsafe_allow_html=True)
                with col_b:
                    st.markdown("""<div style="font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; color: #D4A5A5; margin-bottom: 10px;">Recommendations</div>""", unsafe_allow_html=True)
                    st.markdown("<span style='color: rgba(245,240,235,0.8);'>◇ Enhance influencer marketing</span>", unsafe_allow_html=True)
                    st.markdown("<span style='color: rgba(245,240,235,0.8);'>◇ Launch sampling campaign</span>", unsafe_allow_html=True)

                st.markdown("---")
                estimated_revenue = score * 50
                st.metric("Projected Revenue (1Y)", f"₩{estimated_revenue}B", f"Market Share {score/10:.1f}%")
        else:
            st.markdown("""
            <div style="text-align: center; padding: 100px 20px;">
                <div style="font-family: 'Cormorant Garamond', serif; font-size: 3rem; color: rgba(201,169,98,0.3); margin-bottom: 24px;">◇</div>
                <div style="font-family: 'Cormorant Garamond', serif; font-size: 1.3rem; color: rgba(245,240,235,0.5); letter-spacing: 0.05em;">Configure product details<br>and run simulation</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# TAB 6: AI 챗봇 - 럭셔리 스타일
# ============================================================
with tab6:
    st.markdown('<div class="section-header">AI Trend Assistant</div>', unsafe_allow_html=True)

    # 에이전트 상태 표시
    tab6_orchestrator = get_orchestrator()
    if AGENTS_AVAILABLE and tab6_orchestrator:
        has_api = tab6_orchestrator.client is not None
        if has_api:
            st.success("◆ Claude API Connected — Real-time AI Analysis Available")
        else:
            st.info("◇ Rule-based Mode — Enable API key for advanced features")
    else:
        st.warning("○ Agent System Loading...")

    # 추천 질문 버튼
    st.markdown("""<div style="font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; color: #E8D5A8; margin: 20px 0 14px 0;">Suggested Queries</div>""", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("Bakuchiol", key="btn_bakuchiol", use_container_width=True):
            st.session_state['pending_query'] = "바쿠치올 트렌드 분석해줘"
    with col2:
        if st.button("Trends", key="btn_trend", use_container_width=True):
            st.session_state['pending_query'] = "2026년 뷰티 트렌드 전망"
    with col3:
        if st.button("Colors", key="btn_color", use_container_width=True):
            st.session_state['pending_query'] = "2026 컬러 트렌드 분석"
    with col4:
        if st.button("Competitors", key="btn_competitor", use_container_width=True):
            st.session_state['pending_query'] = "경쟁사 신제품 분석"
    with col5:
        if st.button("Full Report", key="btn_comprehensive", use_container_width=True):
            st.session_state['pending_query'] = "종합 트렌드 리포트 생성"

    st.markdown("---")

    # 대화 입력
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        pending = st.session_state.get('pending_query', '')
        user_query = st.text_input(
            "Enter your question",
            value=pending,
            placeholder="e.g., What's the market outlook for Bakuchiol?",
            key="chat_input_field"
        )
    with col_btn:
        send_btn = st.button("Send", type="primary", use_container_width=True)

    # 대화 처리
    if send_btn and user_query:
        # pending_query 초기화
        if 'pending_query' in st.session_state:
            del st.session_state['pending_query']

        # 메시지 저장
        st.session_state.chat_messages.append({"role": "user", "content": user_query})

        # 에이전트 실행
        with st.spinner("◇ AI Agent analyzing..."):
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
                    agent_response = f"An error occurred: {str(e)}"
            else:
                agent_response = """## BeautyTrend AI

The agent system is currently initializing.
Please try again in a moment.

**Supported Features:**
- Ingredient trend analysis (Bakuchiol, Peptides, etc.)
- 2026 Beauty mega trends
- Color trend analysis
- Competitor product monitoring
"""

        st.session_state.chat_messages.append({"role": "assistant", "content": agent_response})

    # 대화 히스토리 표시
    st.markdown("""<div style="font-family: 'Cormorant Garamond', serif; font-size: 1.3rem; color: #E8D5A8; margin: 24px 0 16px 0;">Conversation</div>""", unsafe_allow_html=True)
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_messages[-10:]:  # 최근 10개만 표시
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(201,169,98,0.1) 0%, rgba(201,169,98,0.05) 100%); border-radius: 16px; padding: 18px 22px; margin: 12px 0; border-left: 3px solid #C9A962;">
                    <span style="font-family: 'Outfit', sans-serif; font-size: 0.8rem; color: #C9A962; letter-spacing: 0.05em;">USER</span><br>
                    <span style="color: rgba(245,240,235,0.9);">{msg["content"]}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(232,213,211,0.05) 100%); border-radius: 16px; padding: 18px 22px; margin: 12px 0; border-left: 3px solid #E8D5D3;">
                    <span style="font-family: 'Outfit', sans-serif; font-size: 0.8rem; color: #E8D5D3; letter-spacing: 0.05em;">BEAUTYTREND AI</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(msg["content"])

    # 대화 초기화 버튼
    col_clear, col_export = st.columns(2)
    with col_clear:
        if st.button("Clear Conversation", use_container_width=True):
            st.session_state.chat_messages = []
            clear_orchestrator = get_orchestrator()
            if clear_orchestrator:
                clear_orchestrator.clear_history()
            st.rerun()

    with col_export:
        if st.button("Agent Logs", use_container_width=True):
            if st.session_state.agent_logs:
                st.json(st.session_state.agent_logs[-5:])
            else:
                st.info("No logs available yet.")

# ============================================================
# 푸터 - 럭셔리 스타일
# ============================================================
st.markdown("---")
st.markdown("""
<div class="footer-container">
    <div style="font-family: 'Cormorant Garamond', serif; font-size: 2rem; letter-spacing: 0.1em; background: linear-gradient(135deg, #C9A962 0%, #E8D5A8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px;">BEAUTYTREND AI</div>
    <div style="font-family: 'Outfit', sans-serif; font-size: 0.75rem; letter-spacing: 0.2em; color: rgba(201,169,98,0.6); text-transform: uppercase;">Multi-Agent Global Beauty Trend Forecasting</div>
    <div style="margin-top: 24px;">
        <span style="font-family: 'Outfit', sans-serif; background: linear-gradient(135deg, rgba(201,169,98,0.2) 0%, rgba(201,169,98,0.1) 100%); border: 1px solid rgba(201,169,98,0.3); padding: 10px 24px; border-radius: 30px; font-size: 0.75rem; letter-spacing: 0.1em; color: #E8D5A8;">AMOREPACIFIC AI INNOVATION CHALLENGE 2026</span>
    </div>
    <div style="margin-top: 20px; font-family: 'Outfit', sans-serif; font-size: 0.7rem; color: rgba(245,240,235,0.3); letter-spacing: 0.05em;">Version 4.0 · Powered by Claude AI</div>
</div>
""", unsafe_allow_html=True)
