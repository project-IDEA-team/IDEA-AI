from typing import Dict, List, Any
import logging
import aiohttp
import os
import asyncio
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.openai_client import get_client
from app.service.experts.common_form.example_cards import POLICY_CARD_TEMPLATE



logger = logging.getLogger(__name__)

class PolicyExpert(BaseExpert):
    """
    정책 전문가 AI 클래스
    장애인 관련 정책, 법률, 제도 등에 대한 정보를 제공합니다.
    """
    
    def __init__(self):
        super().__init__(ExpertType.POLICY)
        self.client = get_client()

        self.model = "gpt-4.1-mini"  # 사용할 모델 지정
        # 환경 변수에서 백엔드 API URL 가져오기
        self.backend_api_url = os.getenv("BACKEND_API_URL", "http://localhost:8082/api")
        logger.info(f"백엔드 API URL: {self.backend_api_url}")
    
    def _get_system_prompt(self) -> str:
        return """
        너는 장애인 정책 전문가 AI입니다. 
        장애인 관련 법률, 제도, 정책 등에 대한 정확하고 유용한 정보를 제공해야 합니다.
        
        모든 정보 카드는 반드시 아래와 같은 JSON 형식으로 만들어 주세요.
        {
          "id": "string",
          "title": "string",
          "subtitle": "string",
          "summary": "string",
          "type": "string",
          "details": "string",
          "source": {
            "url": "string",
            "name": "string",
            "phone": "string"
          },
          "buttons": [
            {"type": "link", "label": "string", "value": "string"},
            {"type": "tel", "label": "string", "value": "string"}
          ]
        }
        
        제공할 정보 범위:
        - 장애인복지법, 장애인차별금지법 등 관련 법률
        - 장애인연금, 장애수당 등 경제적 지원 제도
        - 장애인 활동지원 서비스
        - 장애인 편의시설 관련 규정
        - 장애인 이동권, 접근권 관련 정책
        - 장애인 고용 관련 정책 및 제도
        - 장애인 교육권 보장 정책
        
        응답 스타일:
        1. 항상 따뜻하고 공감적인 톤으로 응답하세요. 사용자의 상황과 어려움에 공감하는 표현을 포함하세요.
        2. 응답 시작 부분에 짧은 공감/격려 멘트를 추가하세요. (예: "정책 정보를 찾고 계셨군요. 도움이 되는 정보를 알려드리겠습니다.")
        3. 최신 정보를 기반으로 정확한 내용을 제공하세요.
        4. 법률이나 제도의 근거를 명시하되, 전문용어는 가능한 쉽게 설명하세요.
        5. 신청 방법, 자격 요건, 지원 금액 등 실용적이고 구체적인 정보를 포함하세요.
        6. 관련 기관이나 문의처도 함께 안내하세요.
        
        정보 카드:
        1. 모든 응답에는 반드시 관련 정책 정보 카드를 포함하세요.
        2. 카드에는 정책명, 간략한 설명, 신청 방법, 문의처 등 핵심 정보를 담으세요.
        
        사용자에게 실질적인 도움이 되는 정보를 제공하면서도, 정서적 지지를 함께 전달하세요.
        """
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_policy_database",
                    "description": "장애인 정책 데이터베이스에서 관련 정보를 검색합니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keywords": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "검색 키워드 목록"
                            },
                            "policy_type": {
                                "type": "string",
                                "enum": ["경제지원", "의료지원", "교육지원", "고용지원", "주거지원", "이동지원", "문화지원", "기타"],
                                "description": "정책 유형"
                            }
                        },
                        "required": ["keywords"]
                    }
                }
            }
        ]
    
    async def search_policy_database(self, keywords: List[str], policy_type: str = None) -> List[Dict[str, Any]]:
        """
        키워드와 정책 유형을 기반으로 실제 DB에서 정책 정보를 검색합니다.
        
        Args:
            keywords: 검색 키워드 목록
            policy_type: 정책 유형
            
        Returns:
            검색된 정책 카드 목록
        """
        try:
            # 키워드가 None인 경우 빈 리스트로 초기화
            if keywords is None:
                keywords = []
            
            # 키워드가 문자열인 경우 리스트로 변환
            if isinstance(keywords, str):
                keywords = [keywords]
            
            # 키워드 필터링 (문자열만 허용)
            valid_keywords = [kw for kw in keywords if isinstance(kw, str)]
            
            if not valid_keywords:
                logger.warning("유효한 키워드가 없습니다.")
                return [POLICY_CARD_TEMPLATE]
            
            # '장애인' 키워드는 제외하고, 나머지 중 첫 번째 키워드 사용
            search_keywords = [kw for kw in valid_keywords if kw != "장애인"]
            if search_keywords:
                main_keyword = search_keywords[0]
            else:
                main_keyword = "장애인"
            
            # 백엔드 API에서 데이터 가져오기
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                try:
                    async with aiohttp.ClientSession() as session:
                        url = f"{self.backend_api_url}/public/welfare/search?keyword={main_keyword}"
                        
                        logger.info(f"백엔드 API 호출 시도 {retry_count + 1}/{max_retries}: {url}")
                        
                        async with session.get(url, timeout=10) as response:
                            if response.status == 200:
                                search_results = await response.json()
                                logger.info(f"백엔드 API 응답 데이터 수: {len(search_results) if isinstance(search_results, list) else 0}")
                                
                                if not search_results:
                                    logger.warning(f"키워드 '{main_keyword}'에 대한 검색 결과가 없습니다.")
                                    return [POLICY_CARD_TEMPLATE]
                                
                                # 검색 결과를 카드 형식으로 변환
                                policy_cards = []
                                for result in search_results:
                                    # 태그 추출 (lifeArray, intrsThemaArray 등에서)
                                    tags = []
                                    if result.get("lifeArray"):
                                        tags.extend(result["lifeArray"].split(","))
                                    if result.get("intrsThemaArray"):
                                        tags.extend(result["intrsThemaArray"].split(","))
                                    tags = list(set(tags))  # 중복 제거
                                    
                                    card = {
                                        "id": result.get("servId", ""),
                                        "title": result.get("servNm", ""),
                                        "subtitle": result.get("jurMnofNm", ""),  # 담당부처
                                        "summary": result.get("servDgst", ""),  # 서비스 요약
                                        "type": "policy",
                                        "details": (
                                            f"지원대상: {result.get('trgterIndvdlArray', '')}\n"
                                            f"지원내용: {result.get('alwServCn', '')}\n"
                                            f"신청방법: {result.get('slctCritCn', '')}\n"
                                            f"지원주기: {result.get('sprtCycNm', '')}\n"
                                            f"제공유형: {result.get('srvPvsnNm', '')}"
                                        ),
                                        "source": {
                                            "url": result.get("servDtlLink", ""),
                                            "name": result.get("jurOrgNm", ""),  # 담당기관
                                            "phone": result.get("rprsCtadr", "")  # 대표연락처
                                        },
                                        "buttons": [
                                            {
                                                "type": "link",
                                                "label": "자세히 보기",
                                                "value": result.get("servDtlLink", "")
                                            }
                                        ],
                                        "tags": tags  # 태그 정보 추가
                                    }
                                    
                                    # 연락처가 있는 경우 전화 버튼 추가
                                    if result.get("rprsCtadr"):
                                        card["buttons"].append({
                                            "type": "tel",
                                            "label": "문의하기",
                                            "value": result.get("rprsCtadr")
                                        })
                                    
                                    policy_cards.append(card)
                                
                                # 최대 3개 카드만 반환
                                return policy_cards[:3]
                            else:
                                logger.error(f"백엔드 API 호출 실패: {response.status}")
                                retry_count += 1
                                if retry_count < max_retries:
                                    await asyncio.sleep(1)  # 1초 대기 후 재시도
                                    continue
                                return [POLICY_CARD_TEMPLATE]
                except Exception as e:
                    logger.error(f"백엔드 API 호출 중 오류 발생 (시도 {retry_count + 1}/{max_retries}): {str(e)}")
                    retry_count += 1
                    if retry_count < max_retries:
                        await asyncio.sleep(1)  # 1초 대기 후 재시도
                        continue
                    return [POLICY_CARD_TEMPLATE]
            
            logger.error(f"최대 재시도 횟수({max_retries})를 초과했습니다.")
            return [POLICY_CARD_TEMPLATE]
            
        except Exception as e:
            logger.error(f"정책 데이터 검색 중 오류 발생: {str(e)}")
            return [POLICY_CARD_TEMPLATE]
    
    async def process_query(self, query: str, keywords: List[str] = None, conversation_history=None) -> Dict[str, Any]:
        """
        사용자 쿼리를 처리하고 응답을 생성합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 슈퍼바이저가 추출한 키워드 목록
            conversation_history: 대화 이력
            
        Returns:
            응답 딕셔너리 (text, cards)
        """
        try:
            # 검색 키워드 추출
            search_keywords = self._extract_search_keywords(query, keywords)
            logger.debug(f"추출된 검색 키워드: {search_keywords}")
            
            # 정책 정보 검색
            response = await self._search_policy_info(query, search_keywords)
            
            # 응답 검증 및 수정
            validated_response = self.validate_response(response)
            
            return validated_response
            
        except Exception as e:
            logger.error(f"정책 전문가 응답 생성 중 오류 발생: {e}", exc_info=True)
            return {"text": "죄송합니다. 응답을 생성하는 중 문제가 발생했습니다.", "cards": []}
    
    def _prepare_messages(self, query: str, conversation_history: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """대화 이력을 처리하여 메시지 배열을 생성합니다."""
        messages = [{"role": "system", "content": self._get_system_prompt()}]
        
        # 대화 이력이 있는 경우 추가
        if conversation_history:
            # 너무 긴 이력은 최근 5개만 사용
            recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
            for msg in recent_history:
                if msg.get("role") and msg.get("content"):
                    messages.append({"role": msg["role"], "content": msg["content"]})
        
        # 현재 쿼리 추가
        messages.append({"role": "user", "content": query})
        
        return messages
    
    def _format_card(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": data.get("id", POLICY_CARD_TEMPLATE["id"]),
            "title": data.get("title", POLICY_CARD_TEMPLATE["title"]),
            "subtitle": data.get("subtitle", POLICY_CARD_TEMPLATE["subtitle"]),
            "summary": data.get("summary", POLICY_CARD_TEMPLATE["summary"]),
            "type": data.get("type", POLICY_CARD_TEMPLATE["type"]),
            "details": data.get("details", POLICY_CARD_TEMPLATE["details"]),
            "source": data.get("source", POLICY_CARD_TEMPLATE["source"]),
            "buttons": data.get("buttons", POLICY_CARD_TEMPLATE["buttons"])
        }
    
    def _get_description(self) -> str:
        return "장애인 관련 법률, 제도, 정책 등에 대한 정보를 제공합니다."
    
    def _get_icon(self) -> str:
        return "📜"

    def _extract_search_keywords(self, query: str, keywords: List[str] = None) -> List[str]:
        """
        검색에 사용할 키워드를 추출합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 슈퍼바이저가 추출한 키워드 목록
            
        Returns:
            검색 키워드 목록
        """
        try:
            # 1. 기본 키워드 (장애인)
            base_keywords = ["장애인"]
            
            # 2. 슈퍼바이저가 제공한 키워드가 있으면 사용
            if keywords and isinstance(keywords, list):
                valid_keywords = [kw for kw in keywords if isinstance(kw, str)]
                if valid_keywords:
                    return base_keywords + valid_keywords[:3]  # 최대 3개 키워드만 사용
            
            # 3. 쿼리에서 직접 키워드 추출
            query_keywords = []
            
            # 주요 키워드 패턴
            key_patterns = [
                r"장애인\s+(\w+)",  # "장애인 이동" -> "이동"
                r"(\w+)\s+지원금",  # "이동 지원금" -> "이동"
                r"(\w+)\s+혜택",    # "이동 혜택" -> "이동"
                r"(\w+)\s+제도",    # "이동 제도" -> "이동"
                r"(\w+)\s+서비스"   # "이동 서비스" -> "이동"
            ]
            
            import re
            for pattern in key_patterns:
                matches = re.findall(pattern, query)
                query_keywords.extend(matches)
            
            # 중복 제거 및 정제
            query_keywords = list(set(query_keywords))
            query_keywords = [kw.strip() for kw in query_keywords if len(kw.strip()) > 1]
            
            # 최종 키워드 조합 (기본 키워드 + 쿼리 키워드)
            final_keywords = base_keywords + query_keywords[:3]  # 최대 3개 키워드만 사용
            
            logger.info(f"최종 검색 키워드: {final_keywords}")
            return final_keywords
            
        except Exception as e:
            logger.error(f"키워드 추출 중 오류 발생: {str(e)}")
            return ["장애인"]  # 오류 발생 시 기본 키워드만 반환

    async def _search_policy_info(self, query: str, keywords: List[str]) -> Dict[str, Any]:
        """
        정책 정보를 검색하고 응답을 생성합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 검색 키워드 목록
            
        Returns:
            응답 딕셔너리 (text, cards)
        """
        try:
            # 정책 카드 검색
            policy_cards = await self.search_policy_database(keywords)
            
            # 각 카드의 형식 수정
            formatted_cards = []
            for card in policy_cards:
                # 카드 제목은 정책명 사용
                card["title"] = card.get("title", "정책 정보")
                
                # 요약은 한 줄로 제한
                summary = card.get("summary", "")
                if len(summary) > 50:  # 요약은 50자로 제한
                    summary = summary[:47] + "..."
                card["summary"] = summary
                
                # 버튼에 실제 링크 추가
                if "source" in card and "url" in card["source"]:
                    card["buttons"] = [
                        {
                            "type": "link",
                            "label": "자세히 보기",
                            "value": card["source"]["url"]
                        }
                    ]
                    # 전화번호가 있으면 전화 버튼 추가
                    if "phone" in card["source"] and card["source"]["phone"]:
                        card["buttons"].append({
                            "type": "tel",
                            "label": "전화 문의",
                            "value": card["source"]["phone"]
                        })
                
                formatted_cards.append(card)
            
            # 응답 텍스트 생성
            response_text = "안녕하세요! 문의하신 정책 정보를 알려드리겠습니다.\n\n"
            
            # 각 카드의 핵심 정보를 텍스트에 추가
            for card in formatted_cards:
                response_text += f"• {card['title']}\n"
                response_text += f"{card['summary']}\n"
                if "source" in card and "phone" in card["source"]:
                    response_text += f"문의: {card['source']['name']} ({card['source']['phone']})\n"
                response_text += "\n"
            
            return {
                "text": response_text.strip(),
                "cards": formatted_cards
            }
            
        except Exception as e:
            logger.error(f"정책 정보 검색 중 오류 발생: {str(e)}")
            return {
                "text": "죄송합니다. 정책 정보를 검색하는 중에 문제가 발생했습니다.",
                "cards": [POLICY_CARD_TEMPLATE]
            }

async def policy_response(query: str, keywords: List[str] = None, conversation_history=None) -> tuple:
    """
    정책 전문가 AI 응답 생성 함수
    
    Args:
        query: 사용자 쿼리
        keywords: 키워드 목록
        conversation_history: 대화 이력
        
    Returns:
        (응답 텍스트, 정보 카드 목록)
    """
    expert = PolicyExpert()
    response = await expert.process_query(query, keywords, conversation_history)
    return response.get("text", ""), response.get("cards", []) 