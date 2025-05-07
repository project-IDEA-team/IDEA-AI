import aiohttp
import logging
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
import json

logger = logging.getLogger(__name__)

class BaseApiClient:
    """공공데이터 API 클라이언트 기본 클래스"""
    
    def __init__(self, base_url, service_key):
        self.base_url = base_url
        self.api_key = service_key  # service_key에서 일관성을 위해 api_key로 이름 변경
        
    async def get(self, endpoint, params=None):
        """API GET 요청 수행"""
        if params is None:
            params = {}
        
        # 서비스키 추가 (이미 있는 경우 추가하지 않음)
        if 'serviceKey' not in params and 'ServiceKey' not in params:
            params['serviceKey'] = self.api_key
        
        url = f"{self.base_url}/{endpoint}?{urlencode(params)}"
        
        # 요청 URL 로깅 (API 키는 마스킹하여 보안 유지)
        masked_url = url
        if self.api_key and len(self.api_key) > 10:
            # API 키의 일부만 표시하고 나머지는 마스킹
            masked_key = self.api_key[:5] + "..." + self.api_key[-5:]
            masked_url = url.replace(self.api_key, masked_key)
        
        logger.info(f"API 요청: {endpoint} (매개변수 수: {len(params)})")
        logger.debug(f"요청 URL: {masked_url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    logger.info(f"API 응답 상태 코드: {response.status}")
                    
                    if response.status == 200:
                        content_type = response.headers.get('Content-Type', '')
                        logger.debug(f"응답 Content-Type: {content_type}")
                        
                        if 'application/json' in content_type:
                            data = await response.json()
                            logger.debug(f"JSON 응답 수신 (크기: {len(str(data))})")
                            return data
                        elif 'application/xml' in content_type or 'text/xml' in content_type:
                            text = await response.text()
                            logger.debug(f"XML 응답 수신 (크기: {len(text)})")
                            return self._parse_xml(text)
                        else:
                            text = await response.text()
                            logger.debug(f"일반 텍스트 응답 수신 (크기: {len(text)})")
                            # JSON 응답인지 시도
                            try:
                                data = json.loads(text)
                                logger.debug("텍스트를 JSON으로 변환 성공")
                                return data
                            except json.JSONDecodeError:
                                # XML 응답인지 시도
                                try:
                                    data = self._parse_xml(text)
                                    logger.debug("텍스트를 XML로 변환 성공")
                                    return data
                                except Exception as e:
                                    logger.warning(f"알 수 없는 응답 형식: {text[:200]}...")
                                    return {"error": "알 수 없는 응답 형식", "data": text[:1000]}
                    else:
                        error_text = await response.text()
                        logger.error(f"API 요청 실패: 상태 코드 {response.status}, 응답: {error_text[:200]}...")
                        return {"error": f"API 요청 실패: {response.status}", "message": error_text}
        except Exception as e:
            logger.error(f"API 요청 예외 발생: {e}")
            return {"error": str(e)}
    
    def _parse_xml(self, xml_text):
        """XML 응답 파싱"""
        try:
            root = ET.fromstring(xml_text)
            result = self._element_to_dict(root)
            return result
        except Exception as e:
            logger.error(f"XML 파싱 오류: {e}")
            return {"error": f"XML 파싱 오류: {e}", "data": xml_text[:1000]}
    
    def _element_to_dict(self, element):
        """XML 요소를 딕셔너리로 변환"""
        result = {}
        
        # 속성 처리
        for key, value in element.attrib.items():
            result[f"@{key}"] = value
            
        # 텍스트 처리
        if element.text and element.text.strip():
            result["#text"] = element.text.strip()
            
        # 자식 요소 처리
        children = {}
        for child in element:
            child_data = self._element_to_dict(child)
            if child.tag in children:
                if isinstance(children[child.tag], list):
                    children[child.tag].append(child_data)
                else:
                    children[child.tag] = [children[child.tag], child_data]
            else:
                children[child.tag] = child_data
                
        # 자식이 있으면 결과에 추가
        if children:
            result.update(children)
            
        return result 