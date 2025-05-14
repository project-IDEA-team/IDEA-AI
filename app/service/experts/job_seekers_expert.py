from typing import Dict, List, Any
import logging
import os
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.openai_client import get_client
from app.service.experts.common_form.example_cards import EMPLOYMENT_CARD_TEMPLATE
from motor.motor_asyncio import AsyncIOMotorClient
from app.service.embedding import get_embedding
from app.service.utils.data_processor import DataProcessor

logger = logging.getLogger(__name__)

class JobSeekersExpert(BaseExpert):
    """
    구직자 현황 전문가 AI 클래스 (기업회원용)
    기업회원에게 장애인 구직자 현황, 통계, 샘플 구직자 정보 등을 제공합니다.
    """
    def __init__(self):
        super().__init__(ExpertType.JOB_SEEKERS)
        self.client = get_client()
        self.model = "gpt-4.1-mini"
        self.mongo_uri = os.getenv("MONGO_URI")

    def _get_system_prompt(self) -> str:
        return """
        너는 기업회원 전용 장애인 구직자 현황 전문가 AI입니다.\n기업이 장애인 구직자 현황, 통계, 샘플 구직자 정보 등을 쉽게 파악할 수 있도록 안내합니다.\n\n모든 정보 카드는 반드시 아래와 같은 JSON 형식으로 만들어 주세요.\n{\n  "id": "string",\n  "title": "string",\n  "subtitle": "string",\n  "summary": "string",\n  "type": "string",\n  "details": "string",\n  "source": {\n    "url": "string",\n    "name": "string",\n    "phone": "string"\n  },\n  "buttons": [\n    {"type": "link", "label": "string", "value": "string"},\n    {"type": "tel", "label": "string", "value": "string"}\n  ]\n}\n\n제공할 정보 범위:\n- 장애인 구직자 현황 및 통계\n- 구직자 샘플 정보(직종, 지역, 장애유형, 희망임금 등)\n- 구직자 데이터 활용 방법\n- 구직자 채용 시 유의사항\n\n응답 스타일:\n1. 기업 실무자가 빠르게 현황을 파악할 수 있도록 간결하고 명확하게 안내하세요.\n2. 통계, 수치, 표 등 시각적 정보를 활용하세요.\n3. 샘플 구직자 정보는 카드 형태로 제공하세요.\n4. 응답 시작에 짧은 안내 멘트를 추가하세요. (예: "장애인 구직자 현황 정보를 안내해 드리겠습니다.")\n        """

    async def process_query(self, query: str, keywords: List[str] = None, conversation_history=None) -> Dict[str, Any]:
        # 실제 구현에서는 구직자 DB/외부 API 연동 또는 OpenAI 활용
        # 여기서는 예시로 임베딩 기반 검색 구조만 스케치
        try:
            # 샘플: 특정 키워드가 있으면 고정 샘플 카드 반환
            if any(kw in query for kw in ["장애인 구직자", "구직자 현황", "구직자 통계"]):
                cards = [
                    {
                        "id": "1",
                        "title": "사무직 (지체장애)",
                        "summary": "서울 / 중증",
                        "details": "연령: 30대, 희망임금: 월 200만원 이상, 등록일: 2023-09-15"
                    },
                    {
                        "id": "2",
                        "title": "IT/프로그래머 (시각장애)",
                        "summary": "경기 / 중증",
                        "details": "연령: 20대, 희망임금: 월 250만원 이상, 등록일: 2023-10-01"
                    },
                    {
                        "id": "3",
                        "title": "콜센터 (청각장애)",
                        "summary": "인천 / 경증",
                        "details": "연령: 40대, 희망임금: 월 180만원 이상, 등록일: 2023-10-10"
                    }
                ]
                return {
                    "text": "장애인 구직자 현황 정보입니다.",
                    "cards": cards
                }
            # 실제 DB/임베딩 검색 로직은 아래와 같이 추가 구현 가능
            user_embedding = await get_embedding(query)
            client = AsyncIOMotorClient(self.mongo_uri)
            db = client["public_data_db"]
            collection = db["disabled_job_seekers"]
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index_disabled_seekers",
                        "path": "embedding",
                        "queryVector": user_embedding,
                        "numCandidates": 100,
                        "limit": 3
                    }
                }
            ]
            cursor = collection.aggregate(pipeline)
            results = []
            async for doc in cursor:
                card = {
                    "id": doc.get("id", ""),
                    "title": doc.get("jobNm", ""),
                    "summary": f"{doc.get('region', '')} / {doc.get('disabilityType', '')}",
                    "details": f"연령: {doc.get('age', '')}, 희망임금: {doc.get('salary', '')}, 등록일: {doc.get('regDate', '')}"
                }
                results.append(card)
            if not results:
                return {
                    "text": "죄송합니다. 구직자 현황 정보를 찾지 못했습니다.",
                    "cards": [EMPLOYMENT_CARD_TEMPLATE]
                }
            response_text = "장애인 구직자 현황 정보를 안내해 드리겠습니다.\n\n"
            for card in results:
                response_text += f"• {card['title']}\n{card['summary']}\n{card['details']}\n\n"
            return {
                "text": response_text.strip(),
                "cards": results
            }
        except Exception as e:
            logger.error(f"구직자 현황 정보 검색 중 오류 발생: {str(e)}")
            return {
                "text": "죄송합니다. 구직자 현황 정보를 검색하는 중에 문제가 발생했습니다.",
                "cards": [EMPLOYMENT_CARD_TEMPLATE]
            }

    def _get_description(self) -> str:
        return "기업을 위한 장애인 구직자 현황, 통계, 샘플 구직자 정보를 제공합니다."

    def _get_icon(self) -> str:
        return "📊"
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        return []

async def job_seekers_response(query: str, keywords: List[str] = None, conversation_history=None) -> tuple:
    expert = JobSeekersExpert()
    response = await expert.process_query(query, keywords, conversation_history)
    return response.get("text", ""), response.get("cards", []) 