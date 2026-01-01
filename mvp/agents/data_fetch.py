# -*- coding: utf-8 -*-
"""
Data Fetch Agent - 소셜 미디어 데이터 수집 에이전트
"""

import random
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from .base import BaseAgent, AgentResponse, AgentStatus


class DataFetchAgent(BaseAgent):
    """
    데이터 수집 에이전트
    - TikTok, Instagram, YouTube 등 소셜 미디어 데이터 수집
    - 해시태그 트렌드, 언급량, 감성 분석 데이터 제공
    """

    def __init__(self):
        super().__init__(
            name="Data Fetch Agent",
            description="소셜 미디어 데이터 실시간 수집 및 정제"
        )
        self.data_sources = ["TikTok", "Instagram", "YouTube", "뷰티 커뮤니티"]

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """데이터 수집 작업 실행"""
        self.status = AgentStatus.RUNNING
        start_time = time.time()

        try:
            # 작업 유형 판별
            if "해시태그" in task or "hashtag" in task.lower():
                data = self._fetch_hashtag_trends()
                message = self._format_hashtag_report(data)
            elif "성분" in task or "ingredient" in task.lower():
                data = self._fetch_ingredient_mentions()
                message = self._format_ingredient_report(data)
            elif "전체" in task or "all" in task.lower():
                hashtag_data = self._fetch_hashtag_trends()
                ingredient_data = self._fetch_ingredient_mentions()
                data = {
                    "hashtags": hashtag_data,
                    "ingredients": ingredient_data,
                    "summary": self._generate_summary(hashtag_data, ingredient_data)
                }
                message = self._format_full_report(data)
            else:
                # 기본: 전체 데이터 수집
                data = self._fetch_realtime_data()
                message = self._format_realtime_report(data)

            execution_time = time.time() - start_time
            return self._create_response(
                status=AgentStatus.SUCCESS,
                message=message,
                data=data,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return self._create_response(
                status=AgentStatus.ERROR,
                message=f"데이터 수집 중 오류 발생: {str(e)}",
                execution_time=execution_time
            )

    def _fetch_hashtag_trends(self) -> List[Dict]:
        """해시태그 트렌드 데이터 수집 (시뮬레이션)"""
        base_hashtags = [
            {"tag": "#글래스스킨", "base_count": 158000, "category": "피부결"},
            {"tag": "#스킨미니멀리즘", "base_count": 92000, "category": "트렌드"},
            {"tag": "#세라마이드", "base_count": 87000, "category": "성분"},
            {"tag": "#바쿠치올", "base_count": 65000, "category": "성분"},
            {"tag": "#펩타이드", "base_count": 54000, "category": "성분"},
            {"tag": "#슬로우에이징", "base_count": 48000, "category": "트렌드"},
            {"tag": "#비건뷰티", "base_count": 42000, "category": "가치"},
            {"tag": "#클린뷰티", "base_count": 38000, "category": "가치"},
            {"tag": "#더마코스메틱", "base_count": 35000, "category": "트렌드"},
            {"tag": "#피부장벽", "base_count": 32000, "category": "피부결"}
        ]

        # 실시간 변동 시뮬레이션
        trends = []
        for h in base_hashtags:
            variation = random.uniform(0.95, 1.15)
            growth = random.randint(80, 350)
            trends.append({
                "tag": h["tag"],
                "count": int(h["base_count"] * variation),
                "growth": growth,
                "category": h["category"],
                "region": random.choice(["Global", "Korea", "Asia", "US", "Europe"]),
                "sentiment": round(random.uniform(0.7, 0.95), 2),
                "source": random.choice(self.data_sources),
                "updated_at": datetime.now().isoformat()
            })

        return sorted(trends, key=lambda x: x["count"], reverse=True)

    def _fetch_ingredient_mentions(self) -> List[Dict]:
        """성분 언급 데이터 수집 (시뮬레이션)"""
        ingredients = [
            {"name": "바쿠치올", "base": 28000, "category": "안티에이징", "trend": "급상승"},
            {"name": "세라마이드", "base": 45000, "category": "보습", "trend": "상승"},
            {"name": "나이아신아마이드", "base": 62000, "category": "미백", "trend": "유지"},
            {"name": "펩타이드", "base": 38000, "category": "안티에이징", "trend": "상승"},
            {"name": "레티놀", "base": 51000, "category": "안티에이징", "trend": "하락"},
            {"name": "히알루론산", "base": 72000, "category": "보습", "trend": "유지"},
            {"name": "비타민C", "base": 68000, "category": "미백", "trend": "유지"},
            {"name": "스쿠알란", "base": 31000, "category": "보습", "trend": "상승"},
            {"name": "아젤라익애시드", "base": 18000, "category": "진정", "trend": "급상승"},
            {"name": "프로바이오틱스", "base": 15000, "category": "피부장벽", "trend": "급상승"}
        ]

        data = []
        for ing in ingredients:
            variation = random.uniform(0.9, 1.2)
            data.append({
                "name": ing["name"],
                "mentions": int(ing["base"] * variation),
                "category": ing["category"],
                "trend": ing["trend"],
                "sentiment_avg": round(random.uniform(0.7, 0.95), 2),
                "positive_ratio": round(random.uniform(0.65, 0.90), 2),
                "top_context": self._get_ingredient_context(ing["name"]),
                "updated_at": datetime.now().isoformat()
            })

        return sorted(data, key=lambda x: x["mentions"], reverse=True)

    def _fetch_realtime_data(self) -> Dict:
        """실시간 종합 데이터"""
        return {
            "total_posts_analyzed": random.randint(150000, 200000),
            "data_sources": self.data_sources,
            "collection_period": "최근 7일",
            "top_hashtags": self._fetch_hashtag_trends()[:5],
            "top_ingredients": self._fetch_ingredient_mentions()[:5],
            "sentiment_overview": {
                "positive": round(random.uniform(0.55, 0.70), 2),
                "neutral": round(random.uniform(0.20, 0.30), 2),
                "negative": round(random.uniform(0.05, 0.15), 2)
            }
        }

    def _get_ingredient_context(self, ingredient: str) -> List[str]:
        """성분별 언급 맥락"""
        contexts = {
            "바쿠치올": ["레티놀 대안", "민감성 피부", "자연유래", "슬로우에이징"],
            "세라마이드": ["피부장벽 강화", "건조 피부", "수분 보호", "진정"],
            "나이아신아마이드": ["모공 케어", "피지 조절", "톤업", "만능 성분"],
            "펩타이드": ["탄력 개선", "주름 케어", "콜라겐 합성", "고급 성분"],
            "레티놀": ["안티에이징", "각질 케어", "자극 주의", "야간 케어"],
            "히알루론산": ["수분 폭탄", "저분자", "고분자", "보습 필수"],
            "비타민C": ["브라이트닝", "항산화", "아침 케어", "변색 주의"],
            "스쿠알란": ["피부 유사", "밀착 보습", "가벼운 오일", "민감성"],
            "아젤라익애시드": ["트러블 케어", "피지 조절", "색소 침착", "순한 성분"],
            "프로바이오틱스": ["피부 마이크롬", "장벽 강화", "밸런스", "차세대 성분"]
        }
        return contexts.get(ingredient, ["뷰티", "스킨케어"])

    def _generate_summary(self, hashtags: List, ingredients: List) -> Dict:
        """데이터 요약 생성"""
        return {
            "key_insight": "바쿠치올과 프로바이오틱스가 차세대 트렌드 성분으로 급부상",
            "market_sentiment": "전반적으로 긍정적, 클린뷰티 가치 소비 증가",
            "recommended_focus": ["바쿠치올 기반 제품", "피부장벽 강화 라인", "비건 인증"]
        }

    def _format_hashtag_report(self, data: List[Dict]) -> str:
        """해시태그 리포트 포맷팅"""
        report = "## 📊 해시태그 트렌드 분석 결과\n\n"
        report += f"**수집 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        report += f"**데이터 소스**: {', '.join(self.data_sources)}\n\n"
        report += "### TOP 10 해시태그\n\n"
        report += "| 순위 | 해시태그 | 언급량 | 성장률 | 감성점수 |\n"
        report += "|------|----------|--------|--------|----------|\n"
        for i, h in enumerate(data[:10], 1):
            report += f"| {i} | {h['tag']} | {h['count']:,} | +{h['growth']}% | {h['sentiment']} |\n"
        return report

    def _format_ingredient_report(self, data: List[Dict]) -> str:
        """성분 리포트 포맷팅"""
        report = "## 🧪 성분 트렌드 분석 결과\n\n"
        report += f"**수집 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        report += "### 주목 성분 TOP 10\n\n"
        report += "| 성분 | 언급량 | 카테고리 | 추세 | 긍정률 |\n"
        report += "|------|--------|----------|------|--------|\n"
        for ing in data[:10]:
            trend_emoji = {"급상승": "🚀", "상승": "📈", "유지": "➡️", "하락": "📉"}.get(ing["trend"], "")
            report += f"| {ing['name']} | {ing['mentions']:,} | {ing['category']} | {trend_emoji} {ing['trend']} | {ing['positive_ratio']*100:.0f}% |\n"
        return report

    def _format_full_report(self, data: Dict) -> str:
        """전체 리포트 포맷팅"""
        report = "## 📈 종합 데이터 수집 리포트\n\n"
        report += f"### 핵심 인사이트\n{data['summary']['key_insight']}\n\n"
        report += f"### 시장 감성\n{data['summary']['market_sentiment']}\n\n"
        report += "### 추천 포커스\n"
        for item in data['summary']['recommended_focus']:
            report += f"- {item}\n"
        return report

    def _format_realtime_report(self, data: Dict) -> str:
        """실시간 리포트 포맷팅"""
        report = "## 🔄 실시간 데이터 수집 완료\n\n"
        report += f"**분석 게시물**: {data['total_posts_analyzed']:,}개\n"
        report += f"**수집 기간**: {data['collection_period']}\n"
        report += f"**데이터 소스**: {', '.join(data['data_sources'])}\n\n"
        report += "### 감성 분포\n"
        report += f"- 긍정: {data['sentiment_overview']['positive']*100:.1f}%\n"
        report += f"- 중립: {data['sentiment_overview']['neutral']*100:.1f}%\n"
        report += f"- 부정: {data['sentiment_overview']['negative']*100:.1f}%\n"
        return report
