import logging
from typing import List, Dict, Any, Optional
from app.service.public_api.kead import KeadApiClient
from app.service.public_api.welfare import WelfareApiClient
from app.service.public_api.policy import PolicyApiClient

logger = logging.getLogger(__name__)

class ApiManager:
    """공공데이터 API 관리자 클래스"""
    
    def __init__(self):
        """API 클라이언트 초기화"""
        self.kead_client = KeadApiClient()
        self.welfare_client = WelfareApiClient()
        self.policy_client = PolicyApiClient()
    
    async def search_by_keywords(self, keywords: List[str], expert_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """키워드 기반 통합 검색"""
        results = []
        
        try:
            # 검색 키워드 문자열 생성
            keyword_str = " ".join(keywords) if isinstance(keywords, list) else keywords
            
            # 정책 전문가 관련 검색
            if expert_type in [None, "정책", "장애인 정책"]:
                # 권리 정보 검색 (키워드에 '권리', '차별금지', '보장' 등이 포함된 경우)
                if any(kw in ["권리", "차별", "차별금지", "보장", "법률", "인권"] for kw in keywords):
                    rights_response = await self.policy_client.get_disability_rights(keywords)
                    if rights_response and not "error" in rights_response:
                        items = self._extract_items(rights_response)
                        for item in items:
                            results.append(self.policy_client.format_right_to_card(item))
                
                # 일반 정책 정보 검색
                policies_response = await self.policy_client.get_disability_policies(keywords)
                if policies_response and not "error" in policies_response:
                    items = self._extract_items(policies_response)
                    for item in items:
                        results.append(self.policy_client.format_policy_to_card(item))
                
                # 법률 정보 검색
                laws_response = await self.policy_client.get_disability_laws(keywords)
                if laws_response and not "error" in laws_response:
                    items = self._extract_items(laws_response)
                    for item in items:
                        results.append(self.policy_client.format_law_to_card(item))
            
            # 취업 전문가 관련 검색
            if expert_type in [None, "취업", "장애인 취업"]:
                # 구인 실시간 현황 정보 검색 (API 추가)
                try:
                    job_list_response = await self.kead_client.get_job_list()
                    if job_list_response and not "error" in job_list_response:
                        items = self._extract_items(job_list_response)
                        for item in items:
                            try:
                                results.append(self.kead_client.format_job_list_to_card(item))
                            except Exception as e:
                                logger.error(f"구인 실시간 현황 정보 카드 생성 오류: {e}")
                except Exception as e:
                    logger.error(f"구인 실시간 현황 API 호출 오류: {e}")
                
                # 구인 정보 검색 (기존)
                jobs_response = await self.kead_client.get_job_opportunities(keywords)
                if jobs_response and not "error" in jobs_response:
                    items = self._extract_items(jobs_response)
                    for item in items:
                        results.append(self.kead_client.format_job_to_card(item))
                
                # 표준사업장 정보 검색
                if any(kw in ["표준사업장", "사업장", "회사", "기업"] for kw in keywords):
                    workplaces_response = await self.kead_client.get_standard_workplaces()
                    if workplaces_response and not "error" in workplaces_response:
                        items = self._extract_items(workplaces_response)
                        for item in items:
                            results.append(self.kead_client.format_workplace_to_card(item))
                
                # 직업훈련 정보 검색
                if any(kw in ["훈련", "교육", "직업훈련", "취업교육"] for kw in keywords):
                    training_response = await self.kead_client.get_vocational_training(keywords)
                    if training_response and not "error" in training_response:
                        items = self._extract_items(training_response)
                        for item in items:
                            results.append(self.kead_client.format_training_to_card(item))
            
            # 복지 전문가 관련 검색
            if expert_type in [None, "복지", "장애인 복지"]:
                # 복지 서비스 정보 검색
                welfare_response = await self.welfare_client.get_welfare_services(keywords)
                if welfare_response and not "error" in welfare_response:
                    items = self._extract_items(welfare_response)
                    for item in items:
                        results.append(self.welfare_client.format_welfare_to_card(item))
                
                # 감면혜택 정보 검색
                if any(kw in ["감면", "할인", "혜택", "요금", "감면혜택"] for kw in keywords):
                    discount_response = await self.welfare_client.get_discount_benefits(keywords)
                    if discount_response and not "error" in discount_response:
                        items = self._extract_items(discount_response)
                        for item in items:
                            results.append(self.welfare_client.format_discount_to_card(item))
                
                # 활동지원 서비스 정보 검색
                if any(kw in ["활동", "지원", "활동지원", "돌봄"] for kw in keywords):
                    activity_response = await self.welfare_client.get_activity_support(keywords)
                    if activity_response and not "error" in activity_response:
                        items = self._extract_items(activity_response)
                        for item in items:
                            results.append(self.welfare_client.format_activity_to_card(item))
            
            # 검색 결과가 없으면 빈 리스트 반환
            return results[:10]  # 최대 10개 결과로 제한
            
        except Exception as e:
            logger.error(f"API 검색 중 오류 발생: {e}")
            return []
    
    async def get_job_list_by_condition(self, disk_no=None, bsns_spcm_cd=None, bsns_cond_cd=None, page=1, size=10) -> List[Dict[str, Any]]:
        """장애인 구인 실시간 현황 정보 검색 (조건별)"""
        try:
            job_list_response = await self.kead_client.get_job_list(
                disk_no=disk_no, 
                bsns_spcm_cd=bsns_spcm_cd, 
                bsns_cond_cd=bsns_cond_cd, 
                page=page, 
                size=size
            )
            
            if job_list_response and not "error" in job_list_response:
                items = self._extract_items(job_list_response)
                results = []
                for item in items:
                    try:
                        results.append(self.kead_client.format_job_list_to_card(item))
                    except Exception as e:
                        logger.error(f"구인 실시간 현황 정보 카드 생성 오류: {e}")
                return results
            
            return []
                
        except Exception as e:
            logger.error(f"구인 실시간 현황 검색 중 오류 발생: {e}")
            return []
    
    async def get_job_list_by_date(self, disk_no=None, reg_date=None, clos_date=None, page=1, size=10) -> List[Dict[str, Any]]:
        """장애인 구인 실시간 현황 정보 검색 (날짜별)"""
        try:
            job_list_response = await self.kead_client.get_job_list_env(
                disk_no=disk_no, 
                reg_date=reg_date, 
                clos_date=clos_date, 
                page=page, 
                size=size
            )
            
            if job_list_response and not "error" in job_list_response:
                items = self._extract_items(job_list_response)
                logger.info(f"구인 실시간 현황(날짜별) API 결과: {len(items)}개 항목")
                results = []
                for item in items:
                    try:
                        results.append(self.kead_client.format_job_list_to_card(item))
                    except Exception as e:
                        logger.error(f"구인 실시간 현황(날짜별) 정보 카드 생성 오류: {e}")
                return results
            else:
                logger.warning(f"구인 실시간 현황(날짜별) API 오류: {job_list_response.get('error', '')}")
            
            return []
                
        except Exception as e:
            logger.error(f"구인 실시간 현황(날짜별) 검색 중 오류 발생: {e}")
            return []
    
    async def get_job_detail_by_id(self, wanted_auth_no) -> Dict[str, Any]:
        """장애인 구인 상세 정보 조회"""
        try:
            job_detail_response = await self.kead_client.get_job_detail(wanted_auth_no)
            
            if job_detail_response and not "error" in job_detail_response:
                items = self._extract_items(job_detail_response)
                if items and len(items) > 0:
                    try:
                        return self.kead_client.format_job_list_to_card(items[0])
                    except Exception as e:
                        logger.error(f"구인 상세 정보 카드 생성 오류: {e}")
            
            return {}
                
        except Exception as e:
            logger.error(f"구인 상세 정보 조회 중 오류 발생: {e}")
            return {}
    
    def _extract_items(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """API 응답에서 아이템 리스트 추출"""
        try:
            if not isinstance(response, dict):
                logger.warning(f"API 응답이 딕셔너리가 아님: {type(response)}")
                return []
                
            # 디버깅을 위한 로깅
            logger.debug(f"API 응답 구조: {list(response.keys())}")
            
            # 공공데이터포털 API 응답 형식 (data 필드 안에 있는 경우)
            if "data" in response and isinstance(response["data"], list):
                logger.info(f"공공데이터포털 API 응답 형식 (data 필드): {len(response['data'])}개 항목")
                return response["data"]
            
            # 1. response.items 구조
            if "items" in response and isinstance(response["items"], list):
                return response["items"]
                
            # 2. response.body.items 구조
            if "body" in response and isinstance(response["body"], dict):
                body = response["body"]
                if "items" in body:
                    if isinstance(body["items"], list):
                        return body["items"]
                    elif isinstance(body["items"], dict) and "item" in body["items"]:
                        if isinstance(body["items"]["item"], list):
                            return body["items"]["item"]
                        elif isinstance(body["items"]["item"], dict):
                            # 단일 항목인 경우 리스트로 감싸서 반환
                            return [body["items"]["item"]]
                elif "item" in body and isinstance(body["item"], list):
                    return body["item"]
                    
            # 3. response.response.body.items 구조
            if "response" in response and isinstance(response["response"], dict):
                resp = response["response"]
                if "body" in resp and isinstance(resp["body"], dict):
                    body = resp["body"]
                    if "items" in body:
                        if isinstance(body["items"], list):
                            return body["items"]
                        elif isinstance(body["items"], dict) and "item" in body["items"]:
                            if isinstance(body["items"]["item"], list):
                                return body["items"]["item"]
                            elif isinstance(body["items"]["item"], dict):
                                # 단일 항목인 경우 리스트로 감싸서 반환
                                return [body["items"]["item"]]
                    elif "item" in body:
                        if isinstance(body["item"], list):
                            return body["item"]
                        elif isinstance(body["item"], dict):
                            # 단일 항목인 경우 리스트로 감싸서 반환
                            return [body["item"]]
            
            logger.warning(f"API 응답에서 아이템을 찾을 수 없음: {list(response.keys())}")
            return []
        except Exception as e:
            logger.error(f"API 응답 파싱 중 오류 발생: {e}")
            return [] 