from typing import List, Dict, Any
import json
import os

class CounselingTools:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "../../data/counseling")
        self._load_data()

    def _load_data(self):
        """상담 관련 데이터를 로드합니다."""
        self.counseling_centers = self._load_json("counseling_centers.json")
        self.emergency_contacts = self._load_json("emergency_contacts.json")

    def _load_json(self, filename: str) -> Dict[str, Any]:
        """JSON 파일을 로드합니다."""
        file_path = os.path.join(self.data_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filename} not found")
            return {}

    # async def search_counseling_centers(self, query: str) -> List[Dict[str, Any]]:
    #     """상담 센터를 검색합니다."""
    #     # TODO: 실제 검색 로직 구현
    #     return [
    #         {
    #             "id": "center1",
    #             "title": "장애인상담센터",
    #             "summary": "장애인과 가족을 위한 전문 상담 서비스",
    #             "type": "counseling",
    #             "details": "심리상담, 가족상담, 진로상담 등 제공",
    #             "source": {
    #                 "url": "http://example.com/center1",
    #                 "name": "장애인상담센터"
    #             }
    #         }
    #     ]

    async def get_emergency_contacts(self) -> List[Dict[str, Any]]:
        """긴급 상담 연락처를 제공합니다."""
        return [
            {
                "id": "emergency1",
                "title": "긴급 상담 전화",
                "summary": "24시간 운영 긴급 상담 서비스",
                "type": "emergency",
                "details": "전화: 1234-5678",
                "source": {
                    "url": "http://example.com/emergency",
                    "name": "긴급상담센터"
                }
            }
        ] 