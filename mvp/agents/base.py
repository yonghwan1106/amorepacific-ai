# -*- coding: utf-8 -*-
"""
Base Agent Class for BeautyTrend AI Multi-Agent System
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import json


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


@dataclass
class AgentResponse:
    """에이전트 응답 데이터 클래스"""
    agent_name: str
    status: AgentStatus
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "status": self.status.value,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "execution_time": self.execution_time
        }

    def to_markdown(self) -> str:
        """마크다운 형식으로 변환"""
        md = f"### {self.agent_name}\n"
        md += f"**상태**: {self.status.value}\n\n"
        md += f"{self.message}\n"
        if self.data:
            md += f"\n**처리 시간**: {self.execution_time:.2f}초\n"
        return md


class BaseAgent(ABC):
    """베이스 에이전트 클래스"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.last_response: Optional[AgentResponse] = None
        self.history: List[AgentResponse] = []

    @abstractmethod
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """에이전트 작업 실행 (비동기)"""
        pass

    def execute_sync(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """동기 실행 래퍼"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Streamlit 환경에서는 새 이벤트 루프 사용
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(self.execute(task, context))
            else:
                return asyncio.run(self.execute(task, context))
        except RuntimeError:
            return asyncio.run(self.execute(task, context))

    def _create_response(
        self,
        status: AgentStatus,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        execution_time: float = 0.0
    ) -> AgentResponse:
        """응답 생성 헬퍼"""
        response = AgentResponse(
            agent_name=self.name,
            status=status,
            message=message,
            data=data,
            execution_time=execution_time
        )
        self.last_response = response
        self.history.append(response)
        self.status = status
        return response

    def get_status_emoji(self) -> str:
        """상태에 따른 이모지 반환"""
        status_emojis = {
            AgentStatus.IDLE: "⚪",
            AgentStatus.RUNNING: "🔄",
            AgentStatus.SUCCESS: "✅",
            AgentStatus.ERROR: "❌"
        }
        return status_emojis.get(self.status, "⚪")

    def __repr__(self):
        return f"{self.name}(status={self.status.value})"
