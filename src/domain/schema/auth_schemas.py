from pydantic import BaseModel


class RouteReqAdminLogin(BaseModel):
    email: str
    password: str

class RouteResAdminLogin(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
