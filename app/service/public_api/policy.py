import os
import logging
from app.service.public_api.base_client import BaseApiClient

logger = logging.getLogger(__name__)

class PolicyApiClient(BaseApiClient):
    """정책 정보 API 클라이언트"""
    
    def __init__(self):
        # 환경 변수에서 API 키 가져오기 (없으면 빈 문자열)
        service_key = os.getenv("POLICY_API_KEY", "")
        base_url = "https://www.gov.kr/api"
        super().__init__(base_url, service_key)
    
    async def get_disability_policies(self, keywords=None, policy_type=None, target=None, page=1, size=10):
        """장애인 관련 정책 정보 조회"""
        endpoint = "v1/policies/disabilities"
        params = {
            'pageNo': page,
            'numOfRows': size,
            'type': 'json'
        }
        
        if keywords:
            params['keyword'] = ' '.join(keywords) if isinstance(keywords, list) else keywords
        if policy_type:
            params['policyType'] = policy_type
        if target:
            params['target'] = target
            
        return await self.get(endpoint, params)
    
    async def get_disability_laws(self, keywords=None, law_type=None, page=1, size=10):
        """장애인 관련 법률 정보 조회"""
        endpoint = "v1/laws/disabilities"
        params = {
            'pageNo': page,
            'numOfRows': size,
            'type': 'json'
        }
        
        if keywords:
            params['keyword'] = ' '.join(keywords) if isinstance(keywords, list) else keywords
        if law_type:
            params['lawType'] = law_type
            
        return await self.get(endpoint, params)
    
    async def get_disability_rights(self, keywords=None, right_type=None, page=1, size=10):
        """장애인 권리 정보 조회"""
        endpoint = "v1/rights/disabilities"
        params = {
            'pageNo': page,
            'numOfRows': size,
            'type': 'json'
        }
        
        if keywords:
            params['keyword'] = ' '.join(keywords) if isinstance(keywords, list) else keywords
        if right_type:
            params['rightType'] = right_type
            
        return await self.get(endpoint, params)
    
    def format_policy_to_card(self, policy):
        """정책 정보를 카드 형식으로 변환"""
        return {
            "id": f"policy-{policy.get('policyId', '')}",
            "title": policy.get('policyName', '장애인 정책'),
            "subtitle": policy.get('policyType', '정책'),
            "summary": policy.get('summary', '장애인 관련 정책 정보'),
            "type": "policy",
            "details": (
                f"정책명: {policy.get('policyName', '정보 없음')}\n"
                f"정책유형: {policy.get('policyType', '정보 없음')}\n"
                f"지원대상: {policy.get('target', '정보 없음')}\n"
                f"내용: {policy.get('content', '정보 없음')}\n"
                f"신청방법: {policy.get('howToApply', '정보 없음')}\n"
                f"담당부처: {policy.get('ministry', '정보 없음')}\n"
                f"관련법률: {policy.get('relatedLaw', '정보 없음')}"
            ),
            "source": {
                "url": policy.get('detailUrl', 'https://www.gov.kr'),
                "name": policy.get('ministry', '정부24'),
                "phone": policy.get('contactTel', '1588-2188')
            },
            "buttons": [
                {"type": "link", "label": "자세히 보기", "value": policy.get('detailUrl', 'https://www.gov.kr')},
                {"type": "tel", "label": "문의 전화", "value": policy.get('contactTel', '1588-2188')}
            ]
        }
    
    def format_law_to_card(self, law):
        """법률 정보를 카드 형식으로 변환"""
        return {
            "id": f"law-{law.get('lawId', '')}",
            "title": law.get('lawName', '장애인 관련 법률'),
            "subtitle": law.get('lawType', '법률'),
            "summary": law.get('summary', '장애인 관련 법률 정보'),
            "type": "policy",
            "details": (
                f"법률명: {law.get('lawName', '정보 없음')}\n"
                f"법률유형: {law.get('lawType', '정보 없음')}\n"
                f"주요내용: {law.get('content', '정보 없음')}\n"
                f"제정일: {law.get('enactmentDate', '정보 없음')}\n"
                f"최근 개정일: {law.get('amendmentDate', '정보 없음')}\n"
                f"소관부처: {law.get('ministry', '정보 없음')}"
            ),
            "source": {
                "url": law.get('detailUrl', 'https://www.law.go.kr'),
                "name": "국가법령정보센터",
                "phone": "044-414-2114"
            },
            "buttons": [
                {"type": "link", "label": "자세히 보기", "value": law.get('detailUrl', 'https://www.law.go.kr')},
                {"type": "tel", "label": "법제처", "value": "044-414-2114"}
            ]
        }
    
    def format_right_to_card(self, right):
        """권리 정보를 카드 형식으로 변환"""
        return {
            "id": f"right-{right.get('rightId', '')}",
            "title": right.get('rightName', '장애인 권리'),
            "subtitle": right.get('rightType', '권리'),
            "summary": right.get('summary', '장애인 권리 정보'),
            "type": "policy",
            "details": (
                f"권리명: {right.get('rightName', '정보 없음')}\n"
                f"권리유형: {right.get('rightType', '정보 없음')}\n"
                f"내용: {right.get('content', '정보 없음')}\n"
                f"법적근거: {right.get('legalBasis', '정보 없음')}\n"
                f"구제방법: {right.get('remedy', '정보 없음')}\n"
                f"관련기관: {right.get('relatedOrganization', '정보 없음')}"
            ),
            "source": {
                "url": right.get('detailUrl', 'https://www.humanrights.go.kr'),
                "name": "국가인권위원회",
                "phone": "1331"
            },
            "buttons": [
                {"type": "link", "label": "자세히 보기", "value": right.get('detailUrl', 'https://www.humanrights.go.kr')},
                {"type": "tel", "label": "인권상담전화", "value": "1331"}
            ]
        } 