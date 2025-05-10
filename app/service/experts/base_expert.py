from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.models.expert_type import ExpertType
import re

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

    def validate_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        응답을 검증하고 필요한 경우 수정합니다.
        
        Args:
            response: 원본 응답 딕셔너리
            
        Returns:
            검증된 응답 딕셔너리
        """
        if "text" not in response:
            return response
            
        text = response["text"]
        
        # 1. URL이 없는 정보 문장 찾기
        info_without_source = re.findall(r'(?<![\w\d])(?:에 따르면|에 의하면|자료에 의하면|보고서는|통계에 따르면)(?![^.]*?https?://\S+)[^.]*\.', text)
        for info in info_without_source:
            text = text.replace(info, "")  # 출처가 없는 정보는 제거
            
        # 2. 전화번호 형식 검증 및 수정
        phone_numbers = re.finditer(r'(\d{2,4}[-\s]?\d{3,4}[-\s]?\d{4})(?!\s*\([^)]+\))', text)
        for match in phone_numbers:
            phone = match.group(1)
            text = text.replace(phone, f"{phone} (출처 필요)")
            
        # 3. URL 형식 검증
        urls = re.findall(r'https?://\S+', text)
        for url in urls:
            if not url.endswith(('.kr', '.com', '.go.kr', '.or.kr')):  # 신뢰할 수 있는 도메인 확인
                text = text.replace(url, "")
                
        response["text"] = text
        return response

    @abstractmethod
    async def process_query(self, query: str, keywords: Optional[List[str]] = None, conversation_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        사용자 쿼리를 처리하고 응답을 반환합니다.
        구현 시 반드시 validate_response를 호출하여 응답을 검증해야 합니다.
        
        Example:
            response = await self._generate_response(query)
            return self.validate_response(response)
        """
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