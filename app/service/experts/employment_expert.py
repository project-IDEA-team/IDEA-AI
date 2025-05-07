from typing import Dict, List, Any
import logging
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.openai_client import get_client
from app.service.public_api.api_manager import ApiManager

logger = logging.getLogger(__name__)

class EmploymentExpert(BaseExpert):
    """
    취업 전문가 AI 클래스
    장애인 취업, 고용 지원, 직업 교육 등에 대한 정보를 제공합니다.
    """
    
    def __init__(self):
        super().__init__(ExpertType.EMPLOYMENT)
        self.client = get_client()
        self.api_manager = ApiManager()
    
    def _get_system_prompt(self) -> str:
        return """
        너는 장애인 취업 전문가 AI입니다. 
        장애인 취업, 고용 지원, 직업 교육 등에 대한 정확하고 유용한 정보를 제공해야 합니다.
        
        제공할 정보 범위:
        - 장애인 의무고용제도
        - 장애인 구인구직 정보
        - 장애인 표준사업장 정보
        - 장애인 직업훈련 프로그램
        - 취업 후 근로지원 서비스
        - 장애인 취업 관련 보조금 및 지원금
        - 장애인 창업 지원 정보
        
        응답 스타일:
        1. 항상 따뜻하고 격려하는 톤으로 응답하세요. 구직자의 어려움에 공감하고 희망을 주는 표현을 포함하세요.
        2. 응답 시작 부분에 짧은 공감/격려 멘트를 추가하세요. (예: "취업 준비가 쉽지 않으시죠. 함께 좋은 정보를 찾아보겠습니다.")
        3. 최신 고용 동향과 정보를 기반으로 실용적인 조언을 제공하세요.
        4. 취업 지원 제도와 프로그램에 대해 구체적으로 설명하되, 지원 자격, 신청 방법, 혜택 등을 명확히 안내하세요.
        5. 가능한 많은 취업 기회를 제공하고, 다양한 직업 영역을 탐색하도록 격려하세요.
        6. 취업 후 적응과 지속적인 근무를 위한 정보도 함께 제공하세요.
        
        정보 카드:
        1. 모든 응답에는 반드시 관련 취업 정보 카드를 포함하세요.
        2. 카드에는 구인 정보, 직업훈련 프로그램, 취업지원 서비스 등 핵심 정보를 담으세요.
        
        사용자에게 실질적인 취업 기회와 정보를 제공하면서도, 심리적 지지와 자신감을 키워주는 응답을 제공하세요.
        """
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_employment_database",
                    "description": "장애인 취업 데이터베이스에서 관련 정보를 검색합니다.",
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
                            "job_type": {
                                "type": "string",
                                "description": "직업 유형 또는 산업 분야"
                            },
                            "region": {
                                "type": "string",
                                "description": "지역 정보"
                            }
                        },
                        "required": ["keywords"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_job_list_by_condition",
                    "description": "장애인 구인 실시간 현황 정보를 조건으로 검색합니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "disk_no": {
                                "type": "string",
                                "description": "장애코드 (예: 1-시각, 2-청각, 3-신체, 4-정신, 5-발달)"
                            },
                            "bsns_spcm_cd": {
                                "type": "string",
                                "description": "업종코드"
                            },
                            "bsns_cond_cd": {
                                "type": "string",
                                "description": "근무조건코드"
                            },
                            "page": {
                                "type": "integer",
                                "description": "페이지 번호"
                            },
                            "size": {
                                "type": "integer",
                                "description": "페이지당 결과 수"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_job_list_by_date",
                    "description": "장애인 구인 실시간 현황 정보를 날짜로 검색합니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "disk_no": {
                                "type": "string",
                                "description": "장애코드 (예: 1-시각, 2-청각, 3-신체, 4-정신, 5-발달)"
                            },
                            "reg_date": {
                                "type": "string",
                                "description": "구인등록일 (YYYYMMDD 형식)"
                            },
                            "clos_date": {
                                "type": "string",
                                "description": "마감일 (YYYYMMDD 형식)"
                            },
                            "page": {
                                "type": "integer",
                                "description": "페이지 번호"
                            },
                            "size": {
                                "type": "integer",
                                "description": "페이지당 결과 수"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_job_detail",
                    "description": "장애인 구인 상세 정보를 조회합니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "wanted_auth_no": {
                                "type": "string",
                                "description": "구인인증번호"
                            }
                        },
                        "required": ["wanted_auth_no"]
                    }
                }
            }
        ]
    
    async def search_employment_database(self, keywords: List[str], job_type: str = None, region: str = None) -> List[Dict[str, Any]]:
        """
        키워드, 직업 유형, 지역 등을 기반으로 취업 정보 데이터베이스를 검색합니다.
        
        Args:
            keywords: 검색 키워드 목록
            job_type: 직업 유형 또는 산업 분야
            region: 지역 정보
            
        Returns:
            검색된 취업 정보 카드 목록
        """
        try:
            # ApiManager를 통해 공공데이터 API에서 취업 정보 검색
            job_cards = await self.api_manager.search_by_keywords(keywords, "취업")
            
            # 검색 결과가 있으면 반환
            if job_cards:
                return job_cards
                
            # 검색 결과가 없는 경우 백업 데이터 활용
            # 2차 시도: 표준사업장 관련 키워드가 있으면 표준사업장 정보 제공
            if any(kw in ["표준사업장", "사업장", "기업", "회사"] for kw in keywords):
                return [{
                    "id": "workplace-1",
                    "title": "장애인 표준사업장",
                    "subtitle": "장애인 고용 기업",
                    "summary": "장애인 표준사업장 인증을 받은 기업 정보",
                    "type": "employment",
                    "details": (
                        "장애인 표준사업장은 장애인 고용 환경과 편의시설을 갖추고 일정 수 이상의 장애인을 고용한 기업에 부여하는 인증입니다.\n\n"
                        "표준사업장 혜택:\n"
                        "- 법인세, 소득세 감면\n"
                        "- 장애인 고용장려금 지급\n"
                        "- 장애인표준사업장 생산품 우선구매 지원\n\n"
                        "인증 조건:\n"
                        "- 상시 30인 이상 근로자 고용\n"
                        "- 장애인 근로자 수가 전체의 30% 이상\n"
                        "- 중증장애인 근로자 수가 전체의 10% 이상\n"
                        "- 편의시설 설치 및 적정 근로환경 제공"
                    ),
                    "source": {
                        "url": "https://www.kead.or.kr",
                        "name": "한국장애인고용공단",
                        "phone": "1588-1519"
                    },
                    "buttons": [
                        {"type": "link", "label": "표준사업장 정보", "value": "https://www.kead.or.kr/view/service/service03_05.jsp"},
                        {"type": "tel", "label": "전화 문의", "value": "1588-1519"}
                    ]
                }]
            
            # 3차 시도: 직업훈련 관련 키워드가 있으면 직업훈련 정보 제공
            if any(kw in ["훈련", "교육", "직업훈련", "취업준비", "교육"] for kw in keywords):
                return [{
                    "id": "training-1",
                    "title": "장애인 직업능력개발훈련",
                    "subtitle": "직업훈련 프로그램",
                    "summary": "장애유형별 맞춤형 직업능력개발훈련 프로그램",
                    "type": "training",
                    "details": (
                        "한국장애인고용공단에서 제공하는 장애인 직업능력개발훈련 프로그램입니다.\n\n"
                        "훈련 유형:\n"
                        "- 공단 직업능력개발원 훈련: 전국 5개 능력개발원에서 제공하는 장기 훈련\n"
                        "- 위탁훈련: 대학, 사설기관 등과 연계한 다양한 분야 훈련\n"
                        "- 맞춤훈련: 기업 맞춤형 훈련 후 취업 연계\n"
                        "- 발달장애인 훈련: 발달장애인 특화 직무 훈련\n\n"
                        "지원 내용:\n"
                        "- 훈련비 전액 지원\n"
                        "- 훈련수당 월 30만원 지급\n"
                        "- 교통비, 식비 지원\n"
                        "- 훈련 후 취업 알선"
                    ),
                    "source": {
                        "url": "https://www.kead.or.kr",
                        "name": "한국장애인고용공단",
                        "phone": "1588-1519"
                    },
                    "buttons": [
                        {"type": "link", "label": "훈련 정보", "value": "https://www.kead.or.kr/view/service/service02_01.jsp"},
                        {"type": "tel", "label": "전화 문의", "value": "1588-1519"}
                    ]
                }]
            
            # 최후 방안: 기본 장애인 취업 지원 정보 제공
            return [{
                "id": "employment-1",
                "title": "장애인 취업 지원 서비스",
                "subtitle": "취업 지원",
                "summary": "장애인을 위한 구직 활동 및 취업 지원 서비스",
                "type": "employment",
                "details": (
                    "한국장애인고용공단에서 제공하는 취업 지원 서비스입니다.\n\n"
                    "제공 서비스:\n"
                    "- 취업 상담 및 직업평가\n"
                    "- 직업 훈련 연계\n"
                    "- 구인·구직 알선\n"
                    "- 취업 후 적응 지도\n"
                    "- 보조공학기기 지원\n"
                    "- 근로지원인 서비스\n\n"
                    "이용 방법:\n"
                    "- 전국 장애인고용공단 지사 방문\n"
                    "- 워크투게더 홈페이지에서 구직 등록\n"
                    "- 전화 상담 신청"
                ),
                "source": {
                    "url": "https://www.worktogether.or.kr",
                    "name": "워크투게더(장애인 취업통합지원시스템)",
                    "phone": "1588-1519"
                },
                "buttons": [
                    {"type": "link", "label": "취업 지원 서비스", "value": "https://www.worktogether.or.kr"},
                    {"type": "tel", "label": "전화 문의", "value": "1588-1519"}
                ]
            }]
            
        except Exception as e:
            logger.error(f"취업 정보 검색 중 오류 발생: {e}")
            # 오류 발생 시 기본 데이터 반환
            return [{
                "id": "employment-error",
                "title": "장애인 취업 정보 안내",
                "subtitle": "종합 정보",
                "summary": "장애인 취업을 위한 주요 지원 제도 안내",
                "type": "employment",
                "details": (
                    "장애인 취업을 위한 다양한 지원 제도가 있습니다:\n"
                    "- 장애인 취업성공패키지\n"
                    "- 장애인 일자리 지원사업\n"
                    "- 장애인 직업능력개발 지원\n"
                    "- 보조공학기기 지원\n"
                    "- 근로지원인 서비스\n\n"
                    "자세한 내용은 한국장애인고용공단에 문의하세요."
                ),
                "source": {
                    "url": "https://www.kead.or.kr",
                    "name": "한국장애인고용공단",
                    "phone": "1588-1519"
                },
                "buttons": [
                    {"type": "link", "label": "자세히 보기", "value": "https://www.kead.or.kr"},
                    {"type": "tel", "label": "전화 문의", "value": "1588-1519"}
                ]
            }]
    
    async def get_job_list_by_condition(self, disk_no=None, bsns_spcm_cd=None, bsns_cond_cd=None, page=1, size=10) -> List[Dict[str, Any]]:
        """장애인 구인 실시간 현황 정보를 조건으로 검색합니다."""
        try:
            return await self.api_manager.get_job_list_by_condition(
                disk_no=disk_no,
                bsns_spcm_cd=bsns_spcm_cd,
                bsns_cond_cd=bsns_cond_cd,
                page=page,
                size=size
            )
        except Exception as e:
            logger.error(f"구인 실시간 현황 조회 중 오류 발생: {e}")
            return []
    
    async def get_job_list_by_date(self, disk_no=None, reg_date=None, clos_date=None, page=1, size=10) -> List[Dict[str, Any]]:
        """장애인 구인 실시간 현황 정보를 날짜로 검색합니다."""
        try:
            return await self.api_manager.get_job_list_by_date(
                disk_no=disk_no,
                reg_date=reg_date,
                clos_date=clos_date,
                page=page,
                size=size
            )
        except Exception as e:
            logger.error(f"구인 실시간 현황(날짜별) 조회 중 오류 발생: {e}")
            return []
    
    async def get_job_detail(self, wanted_auth_no) -> Dict[str, Any]:
        """장애인 구인 상세 정보를 조회합니다."""
        try:
            return await self.api_manager.get_job_detail_by_id(wanted_auth_no)
        except Exception as e:
            logger.error(f"구인 상세 정보 조회 중 오류 발생: {e}")
            return {}
    
    async def process_query(self, query: str, keywords: List[str] = None, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        사용자 쿼리를 처리하고 응답을 반환합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 슈퍼바이저가 추출한 키워드 목록
            conversation_history: 이전 대화 내용
            
        Returns:
            응답 및 취업 정보 카드 정보
        """
        try:
            # 대화 기록이 없는 경우 기본값 설정
            if conversation_history is None:
                conversation_history = []
                
            # 키워드가 없는 경우 쿼리에서 추출
            if not keywords:
                try:
                    extraction_response = await self.client.chat.completions.create(
                        model="gpt-4.1-mini",
                        messages=[
                            {"role": "system", "content": "사용자의 질문에서 장애인 취업 정보 검색에 필요한 핵심 키워드를 5개 이내로 추출해주세요."},
                            {"role": "user", "content": query}
                        ],
                        temperature=0.3
                    )
                    
                    import json
                    # 응답이 JSON 형식이 아닐 수 있으므로 처리
                    try:
                        keywords_data = json.loads(extraction_response.choices[0].message.content)
                        keywords = keywords_data.get("keywords", [])
                    except json.JSONDecodeError:
                        # 일반 텍스트에서 키워드 추출 시도
                        content = extraction_response.choices[0].message.content
                        possible_keywords = [k.strip() for k in content.split(',')]
                        keywords = [k for k in possible_keywords if k]
                except Exception as e:
                    logger.error(f"키워드 추출 중 오류 발생: {e}")
                    # 키워드 추출 실패 시 기본 키워드 설정
                    keywords = ["취업", "장애인", "일자리"]
            
            # 빈 키워드 배열이면 기본 키워드 설정
            if not keywords:
                keywords = ["취업", "장애인", "일자리"]
                
            logger.info(f"검색 키워드: {keywords}")
            
            # 취업 정보 데이터베이스 검색
            job_cards = await self.search_employment_database(keywords)
            
            # 구인 실시간 현황 정보 검색 (오늘 마감일 기준)
            try:
                import datetime
                today = datetime.datetime.now().strftime("%Y%m%d")
                logger.info(f"오늘 날짜(마감일 기준): {today}")
                
                # 최근 3일 이내 마감되는 공고 조회 (당일, 내일, 모레)
                real_time_jobs = []
                
                # 오늘 마감 공고
                today_jobs = await self.get_job_list_by_date(clos_date=today)
                if today_jobs:
                    real_time_jobs.extend(today_jobs)
                    logger.info(f"오늘 마감 구인 정보: {len(today_jobs)}개")
                
                # 내일 마감 공고
                tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y%m%d")
                tomorrow_jobs = await self.get_job_list_by_date(clos_date=tomorrow)
                if tomorrow_jobs:
                    real_time_jobs.extend(tomorrow_jobs)
                    logger.info(f"내일 마감 구인 정보: {len(tomorrow_jobs)}개")
                
                # 실시간 구인 정보가 없으면 전체 검색 시도
                if not real_time_jobs:
                    logger.info("마감일 기준 검색 결과가 없어 전체 구인 정보 조회 시도")
                    all_jobs = await self.get_job_list_by_condition()
                    if all_jobs:
                        real_time_jobs.extend(all_jobs)
                        logger.info(f"전체 구인 정보: {len(all_jobs)}개")
                
                # 실시간 구인 정보가 있으면 앞에 추가
                if real_time_jobs:
                    logger.info(f"실시간 구인 정보 검색 결과: {len(real_time_jobs)}개")
                    # 중복 제거를 위해 기존 job_cards의 ID 목록 생성
                    existing_ids = set(card["id"] for card in job_cards if "id" in card)
                    
                    # 중복되지 않는 실시간 구인 정보만 추가
                    for job in real_time_jobs[:5]:  # 최대 5개만 추가
                        if job.get("id") not in existing_ids:
                            job_cards.insert(0, job)  # 맨 앞에 추가
                else:
                    logger.warning("실시간 구인 정보 검색 결과 없음")
                    
            except Exception as e:
                logger.error(f"실시간 구인 정보 조회 중 오류 발생: {e}", exc_info=True)
            
            # job_cards가 비어있으면 기본 정보 제공
            if not job_cards:
                logger.warning("검색 결과 없음. 기본 정보 제공")
                job_cards = [{
                    "id": "employment-default",
                    "title": "장애인 취업 지원 서비스",
                    "subtitle": "취업 지원",
                    "summary": "장애인을 위한 구직 활동 및 취업 지원 서비스",
                    "type": "employment",
                    "details": (
                        "한국장애인고용공단에서 제공하는 취업 지원 서비스입니다.\n\n"
                        "제공 서비스:\n"
                        "- 취업 상담 및 직업평가\n"
                        "- 직업 훈련 연계\n"
                        "- 구인·구직 알선\n"
                        "- 취업 후 적응 지도\n"
                        "- 보조공학기기 지원\n"
                        "- 근로지원인 서비스\n\n"
                        "이용 방법:\n"
                        "- 전국 장애인고용공단 지사 방문\n"
                        "- 워크투게더 홈페이지에서 구직 등록\n"
                        "- 전화 상담 신청"
                    ),
                    "source": {
                        "url": "https://www.worktogether.or.kr",
                        "name": "워크투게더(장애인 취업통합지원시스템)",
                        "phone": "1588-1519"
                    },
                    "buttons": [
                        {"type": "link", "label": "취업 지원 서비스", "value": "https://www.worktogether.or.kr"},
                        {"type": "tel", "label": "전화 문의", "value": "1588-1519"}
                    ]
                }]
            
            # 검색 결과 기반 응답 생성
            job_titles = ", ".join([card["title"] for card in job_cards[:3]])
            
            # 대화 이력을 LLM 메시지로 변환
            messages = [{"role": "system", "content": self._get_system_prompt()}]
            
            # 이전 대화 내용이 있으면 메시지에 추가
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if content and content.strip():  # 내용이 있는 메시지만 추가
                        messages.append({"role": role, "content": content})
            
            # 마지막 질문과 취업 정보 포함
            messages.append({
                "role": "user", 
                "content": f"다음 질문에 대해 관련 취업 정보를 제공해주세요. 관련 정보: {job_titles}\n\n질문: {query}"
            })
            
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=messages,
                    temperature=0.7
                )
                
                answer = response.choices[0].message.content
            except Exception as e:
                logger.error(f"LLM 응답 생성 중 오류 발생: {e}")
                answer = f"장애인 취업에 관련된 정보를 찾아보았습니다. {job_titles}에 대한 정보를 확인해보세요. 더 자세한 정보가 필요하시면 구체적인 질문을 해주세요."
            
            return {
                "answer": answer,
                "cards": job_cards
            }
            
        except Exception as e:
            logger.error(f"취업 전문가 응답 생성 중 오류 발생: {e}")
            return {
                "answer": "죄송합니다. 현재 취업 정보를 제공하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                "cards": []
            }
    
    def _get_description(self) -> str:
        return "취업, 직업훈련, 장애인 표준사업장 안내"
    
    def _get_icon(self) -> str:
        return "💼"

async def employment_response(query: str, keywords: List[str] = None, conversation_history=None) -> tuple:
    """
    취업 전문가 응답을 생성합니다.
    
    Args:
        query: 사용자 쿼리
        keywords: 키워드 목록
        conversation_history: 이전 대화 내용
        
    Returns:
        응답 텍스트와 취업 정보 카드 목록
    """
    expert = EmploymentExpert()
    response = await expert.process_query(query, keywords, conversation_history)
    return response["answer"], response["cards"] 