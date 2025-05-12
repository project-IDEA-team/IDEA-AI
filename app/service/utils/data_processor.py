from typing import Dict, List, Any, Optional
import re
import json
import logging
from konlpy.tag import Okt
from keybert import KeyBERT
import numpy as np

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    데이터 처리 유틸리티 클래스
    """
    
    def __init__(self):
        """초기화"""
        self.okt = Okt()
        self.keybert_model = KeyBERT()
        
    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """
        텍스트에서 주요 키워드를 추출합니다.
        
        Args:
            text: 입력 텍스트
            top_n: 추출할 키워드 수
            
        Returns:
            추출된 키워드 리스트
        """
        try:
            # 형태소 분석
            normalized = self.okt.normalize(text)
            tokens = self.okt.phrases(normalized)
            
            # KeyBERT를 사용한 키워드 추출
            keywords = self.keybert_model.extract_keywords(
                normalized,
                keyphrase_ngram_range=(1, 2),  # 1-2개 단어로 구성된 키워드 추출
                stop_words=self._get_korean_stop_words(),
                top_n=top_n
            )
            
            # (keyword, score) 튜플에서 keyword만 추출
            extracted_keywords = [keyword for keyword, _ in keywords]
            
            # 형태소 분석 결과와 KeyBERT 결과 결합
            combined_keywords = list(set(extracted_keywords + tokens[:top_n]))
            
            return combined_keywords[:top_n]
            
        except Exception as e:
            logger.error(f"키워드 추출 중 오류 발생: {str(e)}")
            return []
    
    def _get_korean_stop_words(self) -> List[str]:
        """한국어 불용어 목록을 반환합니다."""
        return [
            "있다", "하다", "이다", "되다", "없다", "같다", "보다", "이", "그", "저",
            "것", "수", "등", "들", "및", "에서", "그리고", "그러나", "하지만", "또는",
            "또한", "때문에", "위해", "통해", "으로", "에게", "에서", "부터", "까지"
        ]
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        두 텍스트 간의 유사도를 계산합니다.
        
        Args:
            text1: 첫 번째 텍스트
            text2: 두 번째 텍스트
            
        Returns:
            유사도 점수 (0.0 ~ 1.0)
        """
        try:
            # 각 텍스트의 키워드 추출
            keywords1 = set(self.extract_keywords(text1))
            keywords2 = set(self.extract_keywords(text2))
            
            # Jaccard 유사도 계산
            intersection = len(keywords1.intersection(keywords2))
            union = len(keywords1.union(keywords2))
            
            if union == 0:
                return 0.0
                
            return intersection / union
            
        except Exception as e:
            logger.error(f"유사도 계산 중 오류 발생: {str(e)}")
            return 0.0
    
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