from typing import List, Any, Optional

from pydantic import BaseModel, Field, conlist

class Mailer(BaseModel):
    from_: str = Field(..., alias="from")
    name: str

class EmailParams(BaseModel):
    from_: str = Field(..., alias="from")
    to: conlist(str, min_length=1)  # requires at least one recipient
    subject: str
    html_body:  str = Field(..., alias="html")
    attachments: list[Any] = Field(default_factory=list)