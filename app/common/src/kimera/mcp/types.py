from __future__ import annotations
from typing import Any, Optional, Union, Dict, List
from pydantic import BaseModel, Field


class MCPError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


class MCPTextItem(BaseModel):
    type: str = Field(default="text")
    text: str

class MCPResource(BaseModel):
    uri: str
    text: str
    mimeType: str = Field(default="application/json")


class MCPResponse(BaseModel):
    jsonrpc: str = Field(default="2.0")
    id: Optional[Union[int, str]] = None
    result: Optional[Dict[str, Any]|List] = None

    @classmethod
    def success(cls, req_id: Any, result: Dict[str, Any]) -> Dict[str,Any]:
        return MCPResponse(id=req_id,result=result).model_dump()

    @classmethod
    def failure(cls, req_id: Any, code: int, message: str, data: Any | None = None) -> Dict[str,Any]:
        return MCPError(code=code, message=message, data=data).model_dump()

    def to_json(self) -> str:
        return self.model_dump_json()
