# -*- coding: utf-8 -*-
"""
BeautyTrend AI - MVP v2.0
아모레퍼시픽 2026 AI INNOVATION CHALLENGE
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta
from pathlib import Path
import random

# 페이지 설정
st.set_page_config(
    page_title="BeautyTrend AI",
    page_icon="💄",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .insight-box {
        background: #f8f9ff;
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 0 10px 10px 0;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# 데이터 로드
@st.cache_data
def load_data():
    base_path = Path(__file__).parent

    tiktok_data = {
        "hashtag_trends": [
            {"tag": "글래스스킨", "count": 158000, "growth": 245},
            {"tag": "스킨미니멀리즘", "count": 92000, "growth": 189},
            {"tag": "세라마이드", "count": 87000, "growth": 156},
            {"tag": "바쿠치올", "count": 65000, "growth": 312},
            {"tag": "펩타이드", "count": 54000, "growth": 178}
        ],
        "ingredient_mentions": [
            {"name": "세라마이드", "count": 45000, "sentiment_avg": 0.86},
            {"name": "나이아신아마이드", "count": 62000, "sentiment_avg": 0.82},
            {"name": "펩타이드", "count": 38000, "sentiment_avg": 0.88},
            {"name": "바쿠치올", "count": 28000, "sentiment_avg": 0.91},
            {"name": "레티놀", "count": 51000, "sentiment_avg": 0.71}
        ]
    }

    historical_data = {
        "ingredient_trends": {
            "세라마이드": [{"month": f"2024-{i:02d}", "mentions": 12000 + i*3000} for i in range(1, 13)],
            "바쿠치올": [{"month": f"2024-{i:02d}", "mentions": 2000 + i*2500} for i in range(1, 13)],
            "펩타이드": [{"month": f"2024-{i:02d}", "mentions": 8000 + i*2500} for i in range(1, 13)]
        }
    }

    return tiktok_data, historical_data

tiktok_data, historical_data = load_data()

# 사이드바
with st.sidebar:
    st.markdown("### 🎯 BeautyTrend AI")
    st.markdown("글로벌 뷰티 트렌드 예측 AI")
    st.markdown("---")
    st.markdown("##### 🤖 AI INNOVATION CHALLENGE 2026")

# 헤더
st.markdown('<h1 class="main-header">💄 BeautyTrend AI</h1>', unsafe_allow_html=True)
st.markdown("글로벌 뷰티 트렌드 예측 AI 에이전트 시스템")
st.markdown("---")

# 탭
tab1, tab2, tab3 = st.tabs(["📊 대시보드", "🔮 트렌드 예측", "💬 AI 챗봇"])

# 대시보드
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📱 분석 게시물", "158,234", "+12,543")
    with col2:
        st.metric("🔥 급상승", "글래스스킨", "+245%")
    with col3:
        st.metric("🧪 주목 성분", "바쿠치올", "+312%")
    with col4:
        st.metric("😊 감성 점수", "0.84", "+0.05")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🏷️ 해시태그 트렌드 TOP 5")
        df = pd.DataFrame(tiktok_data['hashtag_trends'])
        fig = px.bar(df, x='count', y='tag', orientation='h', color='growth',
                     color_continuous_scale='RdYlGn')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 🧪 성분별 감성 분석")
        df = pd.DataFrame(tiktok_data['ingredient_mentions'])
        fig = px.scatter(df, x='count', y='sentiment_avg', size='count',
                        color='sentiment_avg', hover_name='name',
                        color_continuous_scale='RdYlGn')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

# 트렌드 예측
with tab2:
    st.markdown("### 🔮 트렌드 예측")

    ingredient = st.selectbox("성분 선택", list(historical_data['ingredient_trends'].keys()))

    data = historical_data['ingredient_trends'][ingredient]
    df = pd.DataFrame(data)
    df['month'] = pd.to_datetime(df['month'])

    # 예측
    values = df['mentions'].values
    x = np.arange(len(values))
    z = np.polyfit(x, values, 2)
    p = np.poly1d(z)

    future_x = np.arange(len(values), len(values) + 6)
    predictions = p(future_x)
    growth = ((predictions[-1] - values[-1]) / values[-1]) * 100

    future_dates = [df['month'].max() + timedelta(days=30*(i+1)) for i in range(6)]

    col1, col2 = st.columns([3, 1])

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['month'], y=df['mentions'],
                                mode='lines+markers', name='실제'))
        fig.add_trace(go.Scatter(x=future_dates, y=predictions,
                                mode='lines+markers', name='예측',
                                line=dict(dash='dash')))
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("6개월 후 예측", f"{int(predictions[-1]):,}", f"{growth:+.1f}%")
        if growth > 50:
            st.success("🚀 적극 투자 추천")
        elif growth > 20:
            st.info("📈 관심 유지")

# AI 챗봇
with tab3:
    st.markdown("### 💬 AI 트렌드 어시스턴트")

    responses = {
        "바쿠치올": "바쿠치올은 레티놀 대안으로 급부상 중입니다. 민감성 피부 시장에서 +312% 성장했습니다.",
        "트렌드": "2026 주요 트렌드: 슬로우에이징, 스킨미니멀리즘, 글래스스킨이 주목받고 있습니다.",
        "펩타이드": "펩타이드는 콜라겐 생성 촉진 효과로 30-40대 타겟층에서 인기입니다."
    }

    user_input = st.text_input("질문을 입력하세요", placeholder="예: 바쿠치올 전망은?")

    if user_input:
        response = "안녕하세요! BeautyTrend AI입니다. 바쿠치올, 펩타이드, 트렌드에 대해 질문해주세요."
        for key, val in responses.items():
            if key in user_input:
                response = val
                break
        st.info(response)

# 푸터
st.markdown("---")
st.markdown("💄 **BeautyTrend AI** | 아모레퍼시픽 AI INNOVATION CHALLENGE 2026")
