from typing import Dict, List, Any, Optional
import re
import json
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    데이터 처리 유틸리티 클래스
    """
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
        """
        텍스트에서 키워드를 추출합니다.
        
        Args:
            text: 키워드를 추출할 텍스트
            max_keywords: 최대 키워드 수
            
        Returns:
            추출된 키워드 목록
        """
        # 실제 구현에서는 NLP 라이브러리를 사용하여 키워드 추출
        # 임시 구현: 간단한 규칙 기반 키워드 추출
        
        # 텍스트 전처리
        text = text.lower()
        
        # 불용어 정의 (실제로는 더 많은 불용어 필요)
        stopwords = [
            "안녕", "하세요", "입니다", "그리고", "그런데", "하지만", "또한", "이제", "만약", "어떻게",
            "언제", "왜", "어디", "누구", "무엇", "얼마나", "있는", "있다", "없는", "없다", "해서",
            "이런", "저런", "어떤", "제가", "나는", "너는", "우리", "당신", "그것", "좀", "많이"
        ]
        
        # 정규식으로 단어 분리 (한글, 영문, 숫자)
        words = re.findall(r'[가-힣a-zA-Z0-9]+', text)
        
        # 불용어 제거 및 길이가 1인 단어 제거
        filtered_words = [word for word in words if word not in stopwords and len(word) > 1]
        
        # 단어 빈도 계산
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 빈도순 정렬
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # 최대 개수만큼 키워드 추출
        keywords = [word for word, _ in sorted_words[:max_keywords]]
        
        return keywords
    
    @staticmethod
    def format_policy_cards(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        정책 카드 데이터를 프론트엔드에 맞는 형식으로 변환합니다.
        
        Args:
            cards: 정책 카드 데이터 목록
            
        Returns:
            변환된 정책 카드 데이터 목록
        """
        formatted_cards = []
        
        for card in cards:
            formatted_card = {
                "id": card.get("id", ""),
                "title": card.get("title", ""),
                "summary": card.get("summary", ""),
                "type": card.get("type", "policy")
            }
            
            # 선택적 필드 추가
            if "subtitle" in card:
                formatted_card["subtitle"] = card["subtitle"]
            
            if "details" in card:
                formatted_card["details"] = card["details"]
            
            if "imageUrl" in card:
                formatted_card["imageUrl"] = card["imageUrl"]
            
            if "source" in card:
                formatted_card["source"] = card["source"]
            
            if "buttons" in card:
                formatted_card["buttons"] = card["buttons"]
            
            formatted_cards.append(formatted_card)
        
        return formatted_cards
    
    @staticmethod
    def parse_json_safely(json_string: str) -> Optional[Dict[str, Any]]:
        """
        안전하게 JSON 문자열을 파싱합니다.
        
        Args:
            json_string: 파싱할 JSON 문자열
            
        Returns:
            파싱된 JSON 객체 또는 None (파싱 실패 시)
        """
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}")
            return None
    
    # @staticmethod
    # def extract_structured_data(text: str) -> Optional[Dict[str, Any]]:
    #     """
    #     텍스트에서 구조화된 데이터를 추출합니다.
    #     
    #     Args:
    #         text: 구조화된 데이터를 추출할 텍스트
    #         
    #     Returns:
    #         추출된 구조화된 데이터 또는 None (추출 실패 시)
    #     """
    #     # JSON 형식 문자열 추출 시도
    #     json_pattern = r'```json\s*([\s\S]*?)\s*```'
    #     json_match = re.search(json_pattern, text)
    #     
    #     if json_match:
    #         json_str = json_match.group(1)
    #         return DataProcessor.parse_json_safely(json_str)
    #     
    #     # 일반 텍스트에서 키-값 쌍 추출 시도
    #     result = {}
    #     
    #     # 간단한 키-값 패턴 (예: "키: 값")
    #     kv_pattern = r'([^:\n]+):\s*([^\n]+)'
    #     for match in re.finditer(kv_pattern, text):
    #         key = match.group(1).strip()
    #         value = match.group(2).strip()
    #         result[key] = value
    #     
    #     return result if result else None 