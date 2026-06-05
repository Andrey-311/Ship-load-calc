import httpx
from typing import List, Dict, Optional


class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def get_projects(self) -> List[Dict]:
        response = self.client.get(self._url("/projects/"))
        response.raise_for_status()
        return response.json()

    def create_project(self, data: Dict) -> Dict:
        response = self.client.post(self._url("/projects/"), json=data)
        response.raise_for_status()
        return response.json()

    def get_ecr_list(self, project_id: int, status: Optional[str] = None) -> List[Dict]:
        url = self._url(f"/projects/{project_id}/ecr/")
        if status:
            url += f"?status_filter={status}"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def create_ecr(self, project_id: int, comment: str) -> Dict:
        response = self.client.post(
            self._url(f"/projects/{project_id}/ecr/"),
            json={"comment": comment}
        )
        response.raise_for_status()
        return response.json()

    def get_ecr(self, project_id: int, ecr_id: int) -> Dict:
        response = self.client.get(self._url(f"/projects/{project_id}/ecr/{ecr_id}"))
        response.raise_for_status()
        return response.json()

    def update_ecr_status(self, project_id: int, ecr_id: int, status: str, rejection_reason: str = None) -> Dict:
        data = {"status": status}
        if rejection_reason:
            data["rejection_reason"] = rejection_reason
        response = self.client.patch(
            self._url(f"/projects/{project_id}/ecr/{ecr_id}/status"),
            json=data
        )
        response.raise_for_status()
        return response.json()

    def get_ecr_lines(self, project_id: int, ecr_id: int) -> List[Dict]:
        response = self.client.get(self._url(f"/projects/{project_id}/ecr/{ecr_id}/lines"))
        response.raise_for_status()
        return response.json()

    def create_load_line(self, project_id: int, ecr_id: int, data: Dict) -> Dict:
        response = self.client.post(
            self._url(f"/projects/{project_id}/ecr/{ecr_id}/lines"),
            json=data
        )
        response.raise_for_status()
        return response.json()

    def update_load_line(self, project_id: int, ecr_id: int, line_id: int, data: Dict) -> Dict:
        response = self.client.put(
            self._url(f"/projects/{project_id}/ecr/{ecr_id}/lines/{line_id}"),
            json=data
        )
        response.raise_for_status()
        return response.json()

    def delete_load_line(self, project_id: int, ecr_id: int, line_id: int) -> bool:
        response = self.client.delete(
            self._url(f"/projects/{project_id}/ecr/{ecr_id}/lines/{line_id}")
        )
        return response.status_code == 204

    def get_center_of_gravity(self, project_id: int, ecr_id: int) -> Dict:
        response = self.client.get(
            self._url(f"/projects/{project_id}/ecr/{ecr_id}/center-of-gravity")
        )
        response.raise_for_status()
        return response.json()

    def get_lightweight(self, project_id: int) -> Dict:
        response = self.client.get(self._url(f"/projects/{project_id}/reports/lightweight"))
        response.raise_for_status()
        return response.json()

    def close(self):
        self.client.close()
