from src.services.client_profile.service import ClientProfileService


class ClientProfileAPI:
    """
    Thin API layer on top of ClientProfileService.

    This is a framework-agnostic stub. In a real implementation
    it would be wired into Flask/FastAPI/Django, etc.
    """

    def __init__(self, service: ClientProfileService | None = None) -> None:
        self.service = service or ClientProfileService()

    def get_client_profile(self, client_id: str) -> dict:
        """
        API-facing method. In a real HTTP handler, client_id would
        come from the route/path and the result would be serialised.
        """
        return self.service.get_client_profile(client_id)
