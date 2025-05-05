from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.models.expert_type import ExpertType

class BaseExpert(ABC):
    def __init__(self, expert_type: ExpertType):
        self.expert_type = expert_type
        self.system_prompt = self._get_system_prompt()
        self.tools = self._get_tools()

    @abstractmethod
    def _get_system_prompt(self) -> str:
        """전문가별 시스템 프롬프트를 반환합니다."""
        pass

    @abstractmethod
    def _get_tools(self) -> List[Dict[str, Any]]:
        """전문가별 도구 목록을 반환합니다."""
        pass

    @abstractmethod
    async def process_query(self, query: str) -> Dict[str, Any]:
        """사용자 쿼리를 처리하고 응답을 반환합니다."""
        pass

    def get_expert_info(self) -> Dict[str, Any]:
        """전문가 정보를 반환합니다."""
        return {
            "id": self.expert_type.value,
            "title": self.expert_type.value,
            "expert_type": self.expert_type.value,
            "description": self._get_description(),
            "icon": self._get_icon()
        }

    @abstractmethod
    def _get_description(self) -> str:
        """전문가 설명을 반환합니다."""
        pass

    @abstractmethod
    def _get_icon(self) -> str:
        """전문가 아이콘을 반환합니다."""
        pass 