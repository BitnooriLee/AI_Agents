from pydantic import BaseModel
from typing import Optional

class UserAccountContext(BaseModel):
    customer_id: int
    name: str 
    tier: str = "basic" 
    email: str
    reservation_code: str
    contact_information: str

class InputGuardRailOutput(BaseModel):

    is_off_topic: bool
    reason: str 

class OutputGuardRailOutput(BaseModel):

    is_off_topic: bool
    reason: str 

class HandoffData(BaseModel):

    to_agent_name: str
    issue_type: str
    issue_description: str
    reason: str
