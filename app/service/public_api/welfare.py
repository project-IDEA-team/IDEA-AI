import os
import logging
from app.service.public_api.base_client import BaseApiClient

logger = logging.getLogger(__name__)

class WelfareApiClient(BaseApiClient):
    """복지 정보 API 클라이언트"""
    
    def __init__(self):
        # 환경 변수에서 API 키 가져오기 (없으면 빈 문자열)
        service_key = os.getenv("WELFARE_API_KEY", "")
        base_url = "https://www.bokjiro.go.kr/openapi"
        super().__init__(base_url, service_key)
    
    async def get_welfare_services(self, keywords=None, target=None, category=None, page=1, size=10):
        """장애인 복지 서비스 정보 조회"""
        endpoint = "service/v1/dis"
        params = {
            'pageNo': page,
            'numOfRows': size,
            'type': 'json'
        }
        
        if keywords:
            params['keyword'] = ' '.join(keywords) if isinstance(keywords, list) else keywords
        if target:
            params['target'] = target
        if category:
            params['category'] = category
            
        return await self.get(endpoint, params)
    
    async def get_discount_benefits(self, keywords=None, discount_type=None, page=1, size=10):
        """장애인 감면혜택 정보 조회"""
        endpoint = "discount/v1/dis"
        params = {
            'pageNo': page,
            'numOfRows': size,
            'type': 'json'
        }
        
        if keywords:
            params['keyword'] = ' '.join(keywords) if isinstance(keywords, list) else keywords
        if discount_type:
            params['discountType'] = discount_type
            
        return await self.get(endpoint, params)
    
    async def get_activity_support(self, keywords=None, region=None, page=1, size=10):
        """장애인 활동지원 서비스 정보 조회"""
        endpoint = "activity/v1/dis"
        params = {
            'pageNo': page,
            'numOfRows': size,
            'type': 'json'
        }
        
        if keywords:
            params['keyword'] = ' '.join(keywords) if isinstance(keywords, list) else keywords
        if region:
            params['region'] = region
            
        return await self.get(endpoint, params)
    
    def format_welfare_to_card(self, service):
        """복지 서비스 정보를 카드 형식으로 변환"""
        return {
            "id": f"welfare-{service.get('serviceId', '')}",
            "title": service.get('serviceName', '장애인 복지 서비스'),
            "subtitle": service.get('category', '복지 서비스'),
            "summary": service.get('summary', '장애인 복지 지원 서비스'),
            "type": "welfare",
            "details": (
                f"서비스명: {service.get('serviceName', '정보 없음')}\n"
                f"지원대상: {service.get('target', '정보 없음')}\n"
                f"내용: {service.get('content', '정보 없음')}\n"
                f"신청방법: {service.get('howToApply', '정보 없음')}\n"
                f"구비서류: {service.get('documents', '정보 없음')}\n"
                f"담당기관: {service.get('organization', '정보 없음')}"
            ),
            "source": {
                "url": "https://www.bokjiro.go.kr",
                "name": "복지로",
                "phone": "129"
            },
            "buttons": [
                {"type": "link", "label": "자세히 보기", "value": service.get('detailUrl', 'https://www.bokjiro.go.kr')},
                {"type": "tel", "label": "보건복지상담센터", "value": "129"}
            ]
        }
    
    def format_discount_to_card(self, discount):
        """감면혜택 정보를 카드 형식으로 변환"""
        return {
            "id": f"discount-{discount.get('discountId', '')}",
            "title": discount.get('discountName', '장애인 감면혜택'),
            "subtitle": discount.get('discountType', '감면혜택'),
            "summary": discount.get('summary', '장애인 대상 감면 혜택'),
            "type": "discount",
            "details": (
                f"혜택명: {discount.get('discountName', '정보 없음')}\n"
                f"대상: {discount.get('target', '정보 없음')}\n"
                f"내용: {discount.get('content', '정보 없음')}\n"
                f"신청방법: {discount.get('howToApply', '정보 없음')}\n"
                f"구비서류: {discount.get('documents', '정보 없음')}\n"
                f"담당기관: {discount.get('organization', '정보 없음')}"
            ),
            "source": {
                "url": "https://www.bokjiro.go.kr",
                "name": "복지로",
                "phone": "129"
            },
            "buttons": [
                {"type": "link", "label": "자세히 보기", "value": discount.get('detailUrl', 'https://www.bokjiro.go.kr')},
                {"type": "tel", "label": "보건복지상담센터", "value": "129"}
            ]
        }
    
    def format_activity_to_card(self, activity):
        """활동지원 서비스 정보를 카드 형식으로 변환"""
        return {
            "id": f"activity-{activity.get('activityId', '')}",
            "title": activity.get('serviceName', '장애인 활동지원 서비스'),
            "subtitle": "활동지원 서비스",
            "summary": f"{activity.get('region', '')} 지역 활동지원 서비스",
            "type": "welfare",
            "details": (
                f"서비스명: {activity.get('serviceName', '정보 없음')}\n"
                f"지역: {activity.get('region', '정보 없음')}\n"
                f"신청자격: {activity.get('qualification', '정보 없음')}\n"
                f"지원내용: {activity.get('support', '정보 없음')}\n"
                f"신청방법: {activity.get('howToApply', '정보 없음')}\n"
                f"제공기관: {activity.get('provider', '정보 없음')}"
            ),
            "source": {
                "url": "https://www.bokjiro.go.kr",
                "name": "복지로",
                "phone": "129"
            },
            "buttons": [
                {"type": "link", "label": "자세히 보기", "value": activity.get('detailUrl', 'https://www.bokjiro.go.kr')},
                {"type": "tel", "label": "보건복지상담센터", "value": "129"}
            ]
        } 