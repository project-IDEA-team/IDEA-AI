import os
import logging
from app.service.public_api.base_client import BaseApiClient

logger = logging.getLogger(__name__)

class KeadApiClient(BaseApiClient):
    """한국장애인고용공단 API 클라이언트"""
    
    def __init__(self):
        # 환경 변수에서 API 키 가져오기 (인코딩된 키 우선, 없으면 디코딩된 키 사용)
        service_key = os.getenv("ODCLOUD_SERVICE_KEY_ENC", "") or os.getenv("ODCLOUD_SERVICE_KEY", "")
        if not service_key:
            service_key = os.getenv("KEAD_API_KEY", "")  # 기존 키도 fallback으로 유지
            
        logger.info(f"한국장애인고용공단 API 클라이언트 초기화 (키 존재: {bool(service_key)})")
        
        # 공공데이터포털 API URL로 변경
        base_url = "https://api.odcloud.kr/api"
        super().__init__(base_url, service_key)
    
    async def get_support_agencies(self, region=None, page=1, size=10):
        """근로지원인 수행기관 정보 조회"""
        endpoint = "v1/supportAgency"
        params = {
            'pageNo': page,
            'numOfRows': size,
            'type': 'json'
        }
        
        if region:
            params['region'] = region
            
        return await self.get(endpoint, params)
    
    async def get_standard_workplaces(self, company_name=None, region=None, page=1, size=10):
        """장애인 표준사업장 정보 조회"""
        endpoint = "v1/standardWorkplace"
        params = {
            'pageNo': page,
            'numOfRows': size,
            'type': 'json'
        }
        
        if company_name:
            params['companyName'] = company_name
        if region:
            params['region'] = region
            
        return await self.get(endpoint, params)
    
    async def get_job_opportunities(self, keywords=None, region=None, job_type=None, page=1, size=10):
        """장애인 구인 정보 조회"""
        endpoint = "v1/jobOpportunity"
        params = {
            'pageNo': page,
            'numOfRows': size,
            'type': 'json'
        }
        
        if keywords:
            params['keyword'] = ' '.join(keywords) if isinstance(keywords, list) else keywords
        if region:
            params['region'] = region
        if job_type:
            params['jobType'] = job_type
            
        return await self.get(endpoint, params)
    
    async def get_vocational_training(self, keywords=None, region=None, training_type=None, page=1, size=10):
        """장애인 직업훈련 정보 조회"""
        endpoint = "v1/vocationalTraining"
        params = {
            'pageNo': page,
            'numOfRows': size,
            'type': 'json'
        }
        
        if keywords:
            params['keyword'] = ' '.join(keywords) if isinstance(keywords, list) else keywords
        if region:
            params['region'] = region
        if training_type:
            params['trainingType'] = training_type
            
        return await self.get(endpoint, params)
    
    async def get_job_list(self, disk_no=None, bsns_spcm_cd=None, bsns_cond_cd=None, page=1, size=10):
        """한국장애인고용공단_장애인 구인 실시간 현황 (구인정보)"""
        # 공공데이터포털 API 엔드포인트로 변경
        endpoint = "15117692/v1/uddi:8ea5e58e-b565-404a-96d9-12a2aa2657ac"
        params = {
            'page': page,
            'perPage': size,
            'serviceKey': self.api_key,
            'returnType': 'JSON'
        }
        
        if disk_no:
            params['diskNo'] = disk_no  # 장애코드
        if bsns_spcm_cd:
            params['bsnsSpcmCd'] = bsns_spcm_cd  # 업종코드
        if bsns_cond_cd:
            params['bsnsCondCd'] = bsns_cond_cd  # 근무조건코드
            
        return await self.get(endpoint, params)
    
    async def get_job_list_env(self, disk_no=None, reg_date=None, clos_date=None, page=1, size=10):
        """한국장애인고용공단_장애인 구인 실시간 현황 (환경정보)"""
        # 공공데이터포털 API 엔드포인트로 변경
        endpoint = "15117692/v1/uddi:7947eb38-a527-40db-aa80-d373dae01574"
        params = {
            'page': page,
            'perPage': size,
            'serviceKey': self.api_key,
            'returnType': 'JSON'
        }
        
        if disk_no:
            params['diskNo'] = disk_no  # 장애코드
        if reg_date:
            params['regDate'] = reg_date  # 구인등록일
        if clos_date:
            params['closDate'] = clos_date  # 마감일
            
        return await self.get(endpoint, params)
    
    async def get_job_detail(self, wantedAuthNo):
        """한국장애인고용공단_장애인 구인 상세 정보 조회"""
        # 공공데이터포털 API 엔드포인트로 변경
        endpoint = "15117692/v1/uddi:0afcc7c9-5403-46a7-a084-db2b7644ae64"
        params = {
            'serviceKey': self.api_key,
            'returnType': 'JSON',
            'wantedAuthNo': wantedAuthNo  # 구인인증번호
        }
            
        return await self.get(endpoint, params)
    
    def format_support_agency_to_card(self, agency):
        """근로지원인 수행기관 정보를 카드 형식으로 변환"""
        return {
            "id": f"agency-{agency.get('agencyId', '')}",
            "title": agency.get('agencyName', '근로지원인 수행기관'),
            "subtitle": "근로지원 서비스",
            "summary": f"{agency.get('region', '')} 지역 근로지원인 수행기관",
            "type": "policy",
            "details": (
                f"기관명: {agency.get('agencyName', '정보 없음')}\n"
                f"지역: {agency.get('region', '정보 없음')}\n"
                f"주소: {agency.get('address', '정보 없음')}\n"
                f"연락처: {agency.get('tel', '정보 없음')}\n"
                f"지원내용: 장애인 근로자의 업무 수행을 지원하는 근로지원 서비스 제공"
            ),
            "source": {
                "url": "https://www.kead.or.kr",
                "name": "한국장애인고용공단",
                "phone": agency.get('tel', '')
            },
            "buttons": [
                {"type": "link", "label": "자세히 보기", "value": "https://www.kead.or.kr/contents/sub_main/main.html"},
                {"type": "tel", "label": "전화 문의", "value": agency.get('tel', '')}
            ]
        }
    
    def format_workplace_to_card(self, workplace):
        """장애인 표준사업장 정보를 카드 형식으로 변환"""
        return {
            "id": f"workplace-{workplace.get('standardId', '')}",
            "title": workplace.get('companyName', '장애인 표준사업장'),
            "subtitle": "장애인 표준사업장",
            "summary": f"{workplace.get('region', '')} 소재 장애인 표준사업장",
            "type": "employment",
            "details": (
                f"회사명: {workplace.get('companyName', '정보 없음')}\n"
                f"인증일: {workplace.get('certificationDate', '정보 없음')}\n"
                f"주소: {workplace.get('address', '정보 없음')}\n"
                f"연락처: {workplace.get('tel', '정보 없음')}\n"
                f"업종: {workplace.get('industry', '정보 없음')}\n"
                f"장애인 고용인원: {workplace.get('disabledEmployees', '정보 없음')}명"
            ),
            "source": {
                "url": "https://www.kead.or.kr",
                "name": "한국장애인고용공단",
                "phone": workplace.get('tel', '')
            },
            "buttons": [
                {"type": "link", "label": "자세히 보기", "value": "https://www.kead.or.kr/contents/standard/standard.html"},
                {"type": "tel", "label": "전화 문의", "value": workplace.get('tel', '')}
            ]
        }
    
    def format_job_to_card(self, job):
        """장애인 구인 정보를 카드 형식으로 변환"""
        return {
            "id": f"job-{job.get('jobId', '')}",
            "title": job.get('jobTitle', '장애인 채용 정보'),
            "subtitle": job.get('companyName', '구인 기업'),
            "summary": f"{job.get('region', '')} 지역 {job.get('jobType', '')} 채용",
            "type": "employment",
            "details": (
                f"회사명: {job.get('companyName', '정보 없음')}\n"
                f"채용직종: {job.get('jobType', '정보 없음')}\n"
                f"근무지역: {job.get('region', '정보 없음')}\n"
                f"급여: {job.get('salary', '정보 없음')}\n"
                f"근무시간: {job.get('workHours', '정보 없음')}\n"
                f"마감일: {job.get('deadline', '정보 없음')}\n"
                f"우대사항: {job.get('preferences', '정보 없음')}"
            ),
            "source": {
                "url": "https://www.kead.or.kr",
                "name": "한국장애인고용공단",
                "phone": job.get('contactTel', '')
            },
            "buttons": [
                {"type": "link", "label": "자세히 보기", "value": "https://www.work.go.kr/seekWantedMain.do"},
                {"type": "tel", "label": "문의 전화", "value": job.get('contactTel', '')}
            ]
        }
    
    def format_training_to_card(self, training):
        """장애인 직업훈련 정보를 카드 형식으로 변환"""
        return {
            "id": f"training-{training.get('trainingId', '')}",
            "title": training.get('trainingTitle', '장애인 직업훈련'),
            "subtitle": training.get('institution', '훈련기관'),
            "summary": f"{training.get('trainingType', '')} 분야 직업훈련",
            "type": "training",
            "details": (
                f"훈련과정명: {training.get('trainingTitle', '정보 없음')}\n"
                f"훈련기관: {training.get('institution', '정보 없음')}\n"
                f"훈련기간: {training.get('period', '정보 없음')}\n"
                f"훈련지역: {training.get('region', '정보 없음')}\n"
                f"훈련분야: {training.get('trainingType', '정보 없음')}\n"
                f"신청방법: {training.get('applyMethod', '정보 없음')}\n"
                f"지원내용: {training.get('support', '정보 없음')}"
            ),
            "source": {
                "url": "https://www.kead.or.kr",
                "name": "한국장애인고용공단",
                "phone": training.get('contactTel', '')
            },
            "buttons": [
                {"type": "link", "label": "자세히 보기", "value": "https://www.kead.or.kr/contents/history/history.html"},
                {"type": "tel", "label": "문의 전화", "value": training.get('contactTel', '')}
            ]
        }
    
    def format_job_list_to_card(self, job):
        """한국장애인고용공단 구인 현황 정보를 카드 형식으로 변환"""
        return {
            "id": f"job-{job.get('wantedAuthNo', '')}",
            "title": job.get('wantedTitle', '장애인 채용 정보'),
            "subtitle": job.get('corpNm', '구인 기업'),
            "summary": f"{job.get('bsnsAreaNm', '')} 지역 {job.get('jobsCd', '')} 채용",
            "type": "employment",
            "details": (
                f"회사명: {job.get('corpNm', '정보 없음')}\n"
                f"채용직종: {job.get('jobsCd', '정보 없음')}\n"
                f"근무지역: {job.get('bsnsAreaNm', '정보 없음')}\n"
                f"급여: {job.get('sal', '정보 없음')}\n"
                f"근무시간: {job.get('workTimeNm', '정보 없음') if 'workTimeNm' in job else '정보 없음'}\n"
                f"임금형태: {job.get('salTpNm', '정보 없음')}\n"
                f"마감일: {job.get('closDt', '정보 없음')}\n"
                f"경력: {job.get('careerNm', '정보 없음')}\n"
                f"학력: {job.get('emplEduNm', '정보 없음')}\n"
                f"모집인원: {job.get('collectPsncnt', '정보 없음')}\n"
                f"전화번호: {job.get('telNo', '정보 없음')}"
            ),
            "source": {
                "url": "https://www.kead.or.kr",
                "name": "한국장애인고용공단",
                "phone": job.get('telNo', '')
            },
            "buttons": [
                {"type": "link", "label": "자세히 보기", "value": f"https://www.work.go.kr/seekWantedDetail.do?wantedAuthNo={job.get('wantedAuthNo', '')}"},
                {"type": "tel", "label": "문의 전화", "value": job.get('telNo', '')}
            ]
        } 