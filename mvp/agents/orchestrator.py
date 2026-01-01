# -*- coding: utf-8 -*-
"""
Orchestrator Agent - 중앙 조정 에이전트
Claude API를 활용한 지능형 대화 및 에이전트 조정
"""

import os
import time
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from .base import BaseAgent, AgentResponse, AgentStatus


class OrchestratorAgent(BaseAgent):
    """
    오케스트레이터 에이전트
    - 사용자 질의 분석 및 적절한 에이전트 라우팅
    - Claude API 기반 자연어 처리
    - 에이전트 결과 종합 및 인사이트 생성
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="Orchestrator Agent",
            description="Multi-Agent 시스템 중앙 조정 및 AI 대화"
        )
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        self.sub_agents: Dict[str, BaseAgent] = {}
        self.conversation_history: List[Dict] = []
        self._initialize_client()

    def _initialize_client(self):
        """Claude API 클라이언트 초기화"""
        if self.api_key:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
            except ImportError:
                print("Warning: anthropic package not installed")
            except Exception as e:
                print(f"Warning: Could not initialize Anthropic client: {e}")

    def register_agent(self, agent_type: str, agent: BaseAgent):
        """서브 에이전트 등록"""
        self.sub_agents[agent_type] = agent

    def get_agent_statuses(self) -> Dict[str, str]:
        """모든 에이전트 상태 조회"""
        statuses = {"orchestrator": self.status.value}
        for name, agent in self.sub_agents.items():
            statuses[name] = agent.status.value
        return statuses

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """작업 실행 - 질의 분석 및 적절한 에이전트 라우팅"""
        self.status = AgentStatus.RUNNING
        start_time = time.time()

        try:
            context = context or {}

            # 1. 질의 의도 분석
            intent = self._analyze_intent(task)

            # 2. Claude API 사용 가능 여부에 따른 처리
            if self.client and context.get("use_llm", True):
                response_text = await self._generate_llm_response(task, intent, context)
            else:
                response_text = await self._generate_rule_based_response(task, intent, context)

            execution_time = time.time() - start_time

            return self._create_response(
                status=AgentStatus.SUCCESS,
                message=response_text,
                data={
                    "intent": intent,
                    "agents_used": intent.get("agents", []),
                    "has_llm": self.client is not None
                },
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return self._create_response(
                status=AgentStatus.ERROR,
                message=f"처리 중 오류가 발생했습니다: {str(e)}",
                execution_time=execution_time
            )

    def _analyze_intent(self, query: str) -> Dict:
        """질의 의도 분석"""
        query_lower = query.lower()

        intent = {
            "type": "general",
            "agents": [],
            "keywords": [],
            "entities": []
        }

        # 키워드 기반 의도 분류
        if any(kw in query for kw in ["트렌드", "예측", "전망", "미래"]):
            intent["type"] = "trend_prediction"
            intent["agents"].append("trend_model")

        if any(kw in query for kw in ["해시태그", "소셜", "틱톡", "인스타", "유튜브", "데이터"]):
            intent["type"] = "data_analysis"
            intent["agents"].append("data_fetch")

        if any(kw in query for kw in ["컬러", "색상", "색", "팔레트"]):
            intent["type"] = "color_analysis"
            intent["agents"].append("color_analysis")

        if any(kw in query for kw in ["경쟁사", "브랜드", "에스티로더", "로레알", "시세이도", "신제품"]):
            intent["type"] = "competitor_analysis"
            intent["agents"].append("competitor")

        # 성분 관련
        ingredients = ["바쿠치올", "펩타이드", "세라마이드", "레티놀", "나이아신아마이드",
                      "히알루론산", "비타민", "프로바이오틱스"]
        for ing in ingredients:
            if ing in query:
                intent["entities"].append({"type": "ingredient", "value": ing})
                if "trend_model" not in intent["agents"]:
                    intent["agents"].append("trend_model")

        # 복합 질의 처리
        if any(kw in query for kw in ["종합", "전체", "리포트", "분석"]):
            intent["type"] = "comprehensive"
            intent["agents"] = ["data_fetch", "trend_model", "color_analysis", "competitor"]

        return intent

    async def _generate_llm_response(self, query: str, intent: Dict, context: Dict) -> str:
        """Claude API를 사용한 응답 생성"""

        # 컨텍스트 수집
        agent_data = {}
        for agent_type in intent.get("agents", []):
            if agent_type in self.sub_agents:
                agent = self.sub_agents[agent_type]
                # 에이전트 실행
                agent_response = await agent.execute(query, context)
                agent_data[agent_type] = {
                    "message": agent_response.message,
                    "data": agent_response.data
                }

        # 시스템 프롬프트 구성
        system_prompt = self._build_system_prompt(agent_data)

        # 대화 히스토리에 추가
        self.conversation_history.append({"role": "user", "content": query})

        try:
            # Claude API 호출
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=system_prompt,
                messages=self.conversation_history[-10:]  # 최근 10개 메시지만
            )

            assistant_message = response.content[0].text
            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            return assistant_message

        except Exception as e:
            # API 오류 시 규칙 기반 응답으로 폴백
            return await self._generate_rule_based_response(query, intent, context)

    async def _generate_rule_based_response(self, query: str, intent: Dict, context: Dict) -> str:
        """규칙 기반 응답 생성 (LLM 미사용 시)"""

        responses = []

        # 에이전트 실행 및 결과 수집
        for agent_type in intent.get("agents", []):
            if agent_type in self.sub_agents:
                agent = self.sub_agents[agent_type]
                agent_response = await agent.execute(query, context)
                responses.append(agent_response.message)

        if responses:
            combined = "\n\n---\n\n".join(responses)
            return f"## 🤖 BeautyTrend AI 분석 결과\n\n{combined}"

        # 기본 응답
        return self._get_default_response(query, intent)

    def _build_system_prompt(self, agent_data: Dict) -> str:
        """시스템 프롬프트 구성"""
        prompt = """당신은 BeautyTrend AI의 핵심 AI 어시스턴트입니다.
아모레퍼시픽의 뷰티 트렌드 분석을 담당하며, 다음 역할을 수행합니다:

1. 글로벌 뷰티 트렌드 분석 및 예측
2. 성분 트렌드 인사이트 제공
3. 경쟁사 동향 모니터링
4. 컬러/텍스처 트렌드 분석
5. 신제품 전략 추천

응답 시 다음 원칙을 따르세요:
- 데이터 기반의 구체적인 인사이트 제공
- 아모레퍼시픽 브랜드(설화수, 라네즈, 이니스프리 등)에 적용 가능한 전략 제안
- 마크다운 형식으로 구조화된 응답
- 한국어로 친절하고 전문적인 톤 유지

"""
        # 에이전트 데이터 추가
        if agent_data:
            prompt += "\n## 현재 분석 데이터\n\n"
            for agent_type, data in agent_data.items():
                prompt += f"### {agent_type} 에이전트 결과:\n{data['message']}\n\n"

        return prompt

    def _get_default_response(self, query: str, intent: Dict) -> str:
        """기본 응답 생성"""
        responses = {
            "바쿠치올": """## 🧪 바쿠치올 트렌드 분석

바쿠치올은 현재 뷰티 업계에서 가장 주목받는 성분입니다.

### 📊 핵심 데이터
| 지표 | 수치 |
|------|------|
| 월간 언급량 | 28,000+ |
| 성장률 (YoY) | +312% |
| 감성 점수 | 0.91 |

### 🎯 아모레퍼시픽 전략 제안
1. **설화수**: 한방 성분 + 바쿠치올 융합 안티에이징 라인
2. **라네즈**: 수분 + 바쿠치올 복합 세럼
3. **이니스프리**: 자연유래 바쿠치올 제품 라인

**💡 핵심 인사이트**: 레티놀 대안으로 민감성 피부 시장 공략 기회""",

            "트렌드": """## 📈 2026 뷰티 메가 트렌드

### TOP 4 트렌드
| 트렌드 | 성장률 | 핵심 |
|--------|--------|------|
| 슬로우에이징 | +267% | 자연스러운 노화 관리 |
| 피부 마이크로바이옴 | +189% | 피부 미생물 균형 |
| 스킨미니멀리즘 | +156% | 멀티 기능 제품 |
| 클린뷰티 2.0 | +134% | 지속가능성 강화 |

### 🎯 전략 제안
바쿠치올 기반 슬로우에이징 라인을 Q1 2026 출시 권장합니다.""",

            "컬러": """## 🎨 2026 컬러 트렌드

### TOP 3 상승 컬러
1. 🩷 **Nude Beige** (+61%) - 올시즌 스테디셀러
2. 🌸 **Dusty Rose** (+55%) - 자연스러운 뉴트럴
3. 💜 **Mauve** (+52%) - S/S 2026 키 컬러

### 제품 추천
- **립스틱**: MLBB Rose 계열
- **블러셔**: Peach Glow
- **아이섀도우**: Champagne + Dusty Rose 팔레트""",

            "경쟁사": """## 🏢 경쟁사 동향 분석

### 주요 신제품 (Q1 2026)
| 브랜드 | 제품 | 위협도 |
|--------|------|--------|
| 에스티로더 | ANR 3.0 | 🔴 높음 |
| 시세이도 | Ultimune 5.0 | 🔴 높음 |
| 로레알 | Revitalift X5 | 🟡 중간 |

### 🎯 대응 전략
설화수 자음생 라인 업그레이드 및 바쿠치올 신성분 추가 검토 필요"""
        }

        # 키워드 매칭
        for keyword, response in responses.items():
            if keyword in query:
                return response

        # 기본 안내 응답
        return """## 👋 안녕하세요! BeautyTrend AI입니다.

다음 주제에 대해 질문해 주세요:

- **성분 트렌드**: 바쿠치올, 펩타이드, 세라마이드 등
- **메가 트렌드**: 2026 뷰티 트렌드 전망
- **컬러 트렌드**: 시즌별 인기 컬러
- **경쟁사 분석**: 신제품, 브랜드 동향

예시 질문:
- "바쿠치올 시장 전망은?"
- "2026년 뷰티 트렌드 알려줘"
- "경쟁사 신제품 분석해줘"
"""

    def clear_history(self):
        """대화 히스토리 초기화"""
        self.conversation_history = []

    def get_conversation_summary(self) -> str:
        """대화 요약"""
        if not self.conversation_history:
            return "대화 내역이 없습니다."

        summary = f"총 {len(self.conversation_history)}개의 메시지\n"
        for msg in self.conversation_history[-5:]:
            role = "👤 사용자" if msg["role"] == "user" else "🤖 AI"
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            summary += f"{role}: {content}\n"
        return summary
