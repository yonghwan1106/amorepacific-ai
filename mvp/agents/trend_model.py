# -*- coding: utf-8 -*-
"""
Trend Model Agent - 트렌드 예측 에이전트
"""

import random
import time
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from .base import BaseAgent, AgentResponse, AgentStatus


class TrendModelAgent(BaseAgent):
    """
    트렌드 예측 에이전트
    - 시계열 예측 (ARIMA/Prophet 시뮬레이션)
    - 성분/키워드 트렌드 분석
    - 6~12개월 선행 예측
    """

    def __init__(self):
        super().__init__(
            name="Trend Model Agent",
            description="AI 기반 시계열 예측 및 트렌드 모델링"
        )
        self.prediction_models = ["ARIMA", "Prophet", "Transformer"]
        self.confidence_threshold = 0.85

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """트렌드 예측 작업 실행"""
        self.status = AgentStatus.RUNNING
        start_time = time.time()

        try:
            context = context or {}

            if "성분" in task or "ingredient" in task.lower():
                ingredient = context.get("ingredient", "바쿠치올")
                period = context.get("period", 6)
                data = self._predict_ingredient_trend(ingredient, period)
                message = self._format_ingredient_prediction(ingredient, data)

            elif "해시태그" in task or "키워드" in task:
                keyword = context.get("keyword", "#글래스스킨")
                data = self._predict_keyword_trend(keyword)
                message = self._format_keyword_prediction(keyword, data)

            elif "종합" in task or "전체" in task:
                data = self._generate_comprehensive_forecast()
                message = self._format_comprehensive_report(data)

            else:
                # 기본: 2026 트렌드 예측
                data = self._predict_2026_trends()
                message = self._format_2026_trends(data)

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
                message=f"트렌드 예측 중 오류 발생: {str(e)}",
                execution_time=execution_time
            )

    def _predict_ingredient_trend(self, ingredient: str, months: int = 6) -> Dict:
        """성분 트렌드 예측"""
        # 기본 데이터 (실제로는 DB에서 가져옴)
        ingredient_base = {
            "바쿠치올": {"current": 28000, "growth_rate": 0.25, "confidence": 0.88},
            "세라마이드": {"current": 45000, "growth_rate": 0.12, "confidence": 0.91},
            "펩타이드": {"current": 38000, "growth_rate": 0.18, "confidence": 0.85},
            "나이아신아마이드": {"current": 62000, "growth_rate": 0.05, "confidence": 0.92},
            "레티놀": {"current": 51000, "growth_rate": -0.08, "confidence": 0.89},
            "프로바이오틱스": {"current": 15000, "growth_rate": 0.35, "confidence": 0.82},
            "아젤라익애시드": {"current": 18000, "growth_rate": 0.28, "confidence": 0.84}
        }

        base = ingredient_base.get(ingredient, {"current": 30000, "growth_rate": 0.10, "confidence": 0.80})

        # 시계열 예측 시뮬레이션
        current_value = base["current"]
        monthly_growth = base["growth_rate"] / 12
        predictions = []
        dates = []

        for i in range(1, months + 1):
            date = datetime.now() + timedelta(days=30 * i)
            dates.append(date.strftime("%Y-%m"))

            # 계절성 + 트렌드 + 노이즈
            seasonal = np.sin(2 * np.pi * i / 12) * 0.1
            noise = random.uniform(-0.05, 0.05)
            growth_factor = 1 + monthly_growth + seasonal + noise

            predicted = current_value * (growth_factor ** i)
            predictions.append(int(predicted))

        # 신뢰구간 계산
        std_error = current_value * 0.15
        lower_bound = [max(0, p - 1.96 * std_error) for p in predictions]
        upper_bound = [p + 1.96 * std_error for p in predictions]

        return {
            "ingredient": ingredient,
            "current_value": current_value,
            "predictions": predictions,
            "dates": dates,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "growth_rate": base["growth_rate"],
            "confidence": base["confidence"],
            "model_used": random.choice(self.prediction_models),
            "insight": self._generate_ingredient_insight(ingredient, base["growth_rate"])
        }

    def _predict_keyword_trend(self, keyword: str) -> Dict:
        """키워드 트렌드 예측"""
        # 키워드별 특성
        keyword_base = {
            "#글래스스킨": {"peak_month": 4, "trend": "seasonal_up"},
            "#슬로우에이징": {"peak_month": 0, "trend": "steady_up"},
            "#비건뷰티": {"peak_month": 0, "trend": "steady_up"},
            "#스킨미니멀리즘": {"peak_month": 6, "trend": "seasonal_stable"}
        }

        base = keyword_base.get(keyword, {"peak_month": 0, "trend": "stable"})

        # 6개월 예측
        predictions = []
        for i in range(6):
            if base["trend"] == "seasonal_up":
                value = 100 + 20 * np.sin(2 * np.pi * (i - base["peak_month"]) / 12) + 5 * i
            elif base["trend"] == "steady_up":
                value = 100 + 8 * i + random.uniform(-5, 5)
            else:
                value = 100 + random.uniform(-10, 10)
            predictions.append(round(value, 1))

        return {
            "keyword": keyword,
            "predictions": predictions,
            "trend_type": base["trend"],
            "peak_season": self._get_peak_season(base["peak_month"]),
            "recommendation": self._get_keyword_recommendation(keyword, base["trend"])
        }

    def _predict_2026_trends(self) -> Dict:
        """2026년 뷰티 트렌드 종합 예측"""
        return {
            "mega_trends": [
                {
                    "name": "슬로우에이징 2.0",
                    "confidence": 0.92,
                    "description": "자연스러운 노화 관리, 레티놀 대체 성분 선호",
                    "key_ingredients": ["바쿠치올", "펩타이드", "성장인자"],
                    "target_age": "25-45세"
                },
                {
                    "name": "피부 마이크로바이옴",
                    "confidence": 0.88,
                    "description": "피부 미생물 균형 중심의 스킨케어",
                    "key_ingredients": ["프로바이오틱스", "프리바이오틱스", "포스트바이오틱스"],
                    "target_age": "전연령"
                },
                {
                    "name": "하이브리드 뷰티",
                    "confidence": 0.85,
                    "description": "스킨케어 + 메이크업 경계 융합",
                    "key_ingredients": ["톤업 성분", "SPF", "보습 성분"],
                    "target_age": "20-35세"
                },
                {
                    "name": "뉴로코스메틱",
                    "confidence": 0.78,
                    "description": "스트레스-피부 연결 케어",
                    "key_ingredients": ["아답토젠", "CBD(해외)", "마그네슘"],
                    "target_age": "30-50세"
                }
            ],
            "declining_trends": [
                {"name": "강한 필링", "reason": "피부장벽 손상 우려 증가"},
                {"name": "복잡한 루틴", "reason": "스킨미니멀리즘 확산"},
                {"name": "동물실험 브랜드", "reason": "비건 가치 소비 증가"}
            ],
            "regional_insights": {
                "Korea": "더마코스메틱 + K-뷰티 융합",
                "US": "클린뷰티 + 인디 브랜드 강세",
                "China": "자국 브랜드 성장 + 성분 중심 소비",
                "Europe": "지속가능성 + 럭셔리 클린뷰티"
            }
        }

    def _generate_comprehensive_forecast(self) -> Dict:
        """종합 예측 리포트"""
        ingredient_forecasts = {}
        key_ingredients = ["바쿠치올", "펩타이드", "세라마이드", "프로바이오틱스"]

        for ing in key_ingredients:
            ingredient_forecasts[ing] = self._predict_ingredient_trend(ing, 6)

        return {
            "ingredient_forecasts": ingredient_forecasts,
            "market_outlook": {
                "growth_rate": "연 7.2% 성장 예상",
                "market_size_2026": "$420B (글로벌)",
                "korea_share": "약 3.5%"
            },
            "strategic_recommendations": [
                "바쿠치올 기반 안티에이징 라인 Q1 2026 출시",
                "프로바이오틱스 스킨케어 R&D 가속화",
                "비건 인증 확대로 글로벌 시장 공략",
                "멀티 기능성 제품으로 스킨미니멀리즘 대응"
            ]
        }

    def _generate_ingredient_insight(self, ingredient: str, growth_rate: float) -> str:
        """성분별 인사이트 생성"""
        insights = {
            "바쿠치올": f"레티놀의 자연 유래 대안으로 주목받고 있습니다. 연간 {growth_rate*100:.0f}% 성장률을 보이며, 민감성 피부 시장에서 특히 강세입니다.",
            "펩타이드": f"안티에이징 시장의 핵심 성분으로, 콜라겐 합성 촉진 효과가 입증되어 프리미엄 라인에 필수 성분입니다.",
            "세라마이드": f"피부장벽 강화 트렌드의 중심 성분입니다. 더마코스메틱 시장 확대와 함께 꾸준한 성장세를 유지합니다.",
            "프로바이오틱스": f"피부 마이크로바이옴 트렌드의 핵심입니다. 아직 초기 단계이나 {growth_rate*100:.0f}%의 높은 성장률을 보이며 차세대 트렌드로 급부상 중입니다."
        }
        return insights.get(ingredient, f"현재 {growth_rate*100:.0f}% 성장률을 보이는 성분입니다.")

    def _get_peak_season(self, peak_month: int) -> str:
        """피크 시즌 반환"""
        if peak_month in [3, 4, 5]:
            return "봄 (S/S)"
        elif peak_month in [6, 7, 8]:
            return "여름"
        elif peak_month in [9, 10, 11]:
            return "가을 (F/W)"
        else:
            return "연중 상시"

    def _get_keyword_recommendation(self, keyword: str, trend: str) -> str:
        """키워드별 추천"""
        recommendations = {
            "seasonal_up": "시즌에 맞춘 캠페인 집중 추천",
            "steady_up": "장기 브랜딩 및 지속적 투자 권장",
            "seasonal_stable": "시즌별 적정 투자 유지",
            "stable": "현 수준 유지, 모니터링 지속"
        }
        return recommendations.get(trend, "모니터링 지속")

    def _format_ingredient_prediction(self, ingredient: str, data: Dict) -> str:
        """성분 예측 리포트 포맷팅"""
        report = f"## 🔮 {ingredient} 트렌드 예측 분석\n\n"
        report += f"**예측 모델**: {data['model_used']}\n"
        report += f"**신뢰도**: {data['confidence']*100:.0f}%\n"
        report += f"**예상 성장률**: {data['growth_rate']*100:+.1f}%/년\n\n"

        report += "### 월별 예측\n"
        report += "| 월 | 예측 언급량 | 신뢰구간 |\n"
        report += "|-----|------------|----------|\n"
        for i, (date, pred, low, high) in enumerate(zip(
            data['dates'], data['predictions'],
            data['lower_bound'], data['upper_bound']
        )):
            report += f"| {date} | {pred:,} | {int(low):,} ~ {int(high):,} |\n"

        report += f"\n### 💡 인사이트\n{data['insight']}\n"
        return report

    def _format_keyword_prediction(self, keyword: str, data: Dict) -> str:
        """키워드 예측 리포트"""
        report = f"## 📈 {keyword} 키워드 트렌드 분석\n\n"
        report += f"**트렌드 유형**: {data['trend_type']}\n"
        report += f"**피크 시즌**: {data['peak_season']}\n"
        report += f"**추천**: {data['recommendation']}\n"
        return report

    def _format_2026_trends(self, data: Dict) -> str:
        """2026 트렌드 리포트"""
        report = "## 🚀 2026 뷰티 메가 트렌드 예측\n\n"

        report += "### 상승 트렌드\n\n"
        for trend in data['mega_trends']:
            report += f"**{trend['name']}** (신뢰도: {trend['confidence']*100:.0f}%)\n"
            report += f"- {trend['description']}\n"
            report += f"- 핵심 성분: {', '.join(trend['key_ingredients'])}\n"
            report += f"- 타겟: {trend['target_age']}\n\n"

        report += "### 하락 트렌드\n"
        for trend in data['declining_trends']:
            report += f"- **{trend['name']}**: {trend['reason']}\n"

        report += "\n### 지역별 인사이트\n"
        for region, insight in data['regional_insights'].items():
            report += f"- **{region}**: {insight}\n"

        return report

    def _format_comprehensive_report(self, data: Dict) -> str:
        """종합 리포트"""
        report = "## 📊 종합 트렌드 예측 리포트\n\n"
        report += f"### 시장 전망\n"
        report += f"- 성장률: {data['market_outlook']['growth_rate']}\n"
        report += f"- 2026 시장 규모: {data['market_outlook']['market_size_2026']}\n\n"

        report += "### 전략 추천\n"
        for i, rec in enumerate(data['strategic_recommendations'], 1):
            report += f"{i}. {rec}\n"

        return report
