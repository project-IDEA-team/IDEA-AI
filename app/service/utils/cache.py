from typing import Dict, Any, Optional, Callable
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class SimpleCache:
    """
    간단한 메모리 캐시 구현
    """
    
    def __init__(self, ttl: int = 3600):
        """
        Args:
            ttl: 캐시 유효 시간(초), 기본 1시간
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """
        캐시에서 값을 가져옵니다.
        
        Args:
            key: 캐시 키
            
        Returns:
            캐시된 값 또는 None (캐시 미스 시)
        """
        if key not in self.cache:
            return None
        
        cache_item = self.cache[key]
        if time.time() > cache_item["expires"]:
            # 캐시 만료
            del self.cache[key]
            return None
        
        return cache_item["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        캐시에 값을 저장합니다.
        
        Args:
            key: 캐시 키
            value: 저장할 값
            ttl: 캐시 유효 시간(초), None이면 기본값 사용
        """
        expires = time.time() + (ttl if ttl is not None else self.ttl)
        self.cache[key] = {
            "value": value,
            "expires": expires
        }
    
    def delete(self, key: str) -> None:
        """
        캐시에서 값을 삭제합니다.
        
        Args:
            key: 캐시 키
        """
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        """캐시를 모두 비웁니다."""
        self.cache.clear()

# 글로벌 캐시 인스턴스
global_cache = SimpleCache()

def cached(ttl: Optional[int] = None):
    """
    함수 결과를 캐싱하는 데코레이터
    
    Args:
        ttl: 캐시 유효 시간(초), None이면 기본값 사용
        
    Returns:
        캐싱된 함수
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 캐시 확인
            cached_result = global_cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"캐시 적중: {cache_key}")
                return cached_result
            
            # 함수 실행
            result = await func(*args, **kwargs)
            
            # 결과 캐싱
            global_cache.set(cache_key, result, ttl)
            logger.debug(f"캐시 저장: {cache_key}")
            
            return result
        return wrapper
    return decorator 