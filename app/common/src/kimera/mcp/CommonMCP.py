import json

from kimera.helpers.Helpers import Helpers
from typing import Any, Dict



from .BaseMCP import BaseMCP
from .MCPHelpers import MCPHelpers
from .types import MCPResponse, MCPError, MCPTextItem, MCPResource


class CommonMCP(BaseMCP):



    def __init__(self, server_config, tools_config=None, prompts_config=None, resources_config=None):
        super().__init__(server_config, tools_config=tools_config, prompts_config=prompts_config, resources_config=resources_config)


    @property
    def default_routes(self):
        return self._default_routes


    async def on_root(self,body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        method = body.get("method")
        Helpers.sysPrint("ON",method)

        if method == "initialize":
            return await self.initialize(body)
        if method == "tools/list":
            return await self.tools_list(body)
        if method == "prompts/list":
            return await self.prompts_list(body)
        if method == "resources/list":
            return await self.resources_list(body)
        if method == "tools/call":
            return await self.tools_call(body)
        if method == "prompts/get":
            return await self.prompts_call(body)
        if method == "resources/read":
            return await self.resources_read(body)
        if method == "resources/templates/list":
            return await self.resources_templates_list(body)

        return MCPError(
            code=-32600,
            message=f"method {method} unknown"
        ).model_dump()
    # ---------- Standard MCP endpoints ----------
    async def initialize(self, body: Dict[str, Any] | None = None) -> Dict[str, Any]:

        if not body or not isinstance(body, dict):
            return MCPError(
                    code=-32600,
                    message="Invalid Request"
                ).model_dump()


        request_id = body.get("id")

        templates = []

        for res in self._resources_config:
            templates.extend(res.get("templates"))

        tools = {"tools":[tool.get("definition") for tool in self._tools_config]}
        self._server_config["tools"] = tools
        self._server_config["resourceTemplates"] = templates

        return MCPResponse(
            id=request_id,
            result=self._server_config
        ).model_dump()


    async def tools_list(self, body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        request_id = body.get("id")

        return MCPResponse.success(
            req_id=request_id,
            result={"tools":[tool.get("definition") for tool in self._tools_config]}
        )

    async def prompts_list(self, body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        request_id = body.get("id")

        return MCPResponse.success(
            req_id=request_id,
            result={"prompts":[prompt.get("definition") for prompt in self._prompts_config]}
        )

    async def resources_templates_list(self, body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        request_id = body.get("id")

        templates = []

        for res in self._resources_config:
            templates.extend(res.get("templates"))

        return MCPResponse.success(
            req_id=request_id,
            result={"resourceTemplates": templates}
        )
    async def resources_list(self, body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        request_id = body.get("id")

        return MCPResponse.success(
            req_id=request_id,
            result={"resources":[res.get("definition") for res in self._resources_config]}
        )

    async def tools_call(self, body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        request_id = body.get("id")
        name = body.get("params").get("name")
        arguments = body.get("params").get("arguments")
        use_tool = self._bounded_tools.get(name,"default_call")
        test_call = getattr(self,use_tool,None)
        if test_call:
            result = await test_call(**arguments)
        else:
            result = await getattr(self,"default_call")(**arguments)
        response_item = MCPTextItem(text="N/A")

        for key,value in result.items():
            if isinstance(value,str):
                result[key] = MCPTextItem(text=value)
            if isinstance(value,dict) or isinstance(value,list):
                result[key] = MCPTextItem(text=json.dumps(value))

        return MCPResponse.success(req_id=request_id,
                                   result={"content": [result.get("content")],
                                           "output": [result.get("output")]
                                           })

    async def prompts_call(self, body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        request_id = body.get("id")
        name = body.get("params").get("name")
        stream = body.get("params").get("stream",False)
        arguments = body.get("params").get("arguments")
        use_prompt = self._bounded_tools.get(name)
        test_call = getattr(self, use_prompt, None)

        if test_call:
            result = await test_call(stream=stream,**arguments)
        else:
            raise Exception("method does not exist")

        response_item = MCPTextItem(text=result.content)

        return MCPResponse.success(req_id=request_id,
                                   result={"messages": [{"role":result.role,"content":response_item}]})

    async def resources_read(self, body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        request_id = body.get("id")
        param_uri = body.get("params").get("uri")
        splitter = param_uri.split("?")

        arguments = {}
        if len(splitter) > 1:
            arguments = MCPHelpers.querystring_to_dict(splitter[1])

        uri = splitter[0]

        # stream = body.get("params").get("stream", False)
        use_res = self._bounded_resources.get(uri.split("?")[0])

        test_call = None
        if use_res:
            test_call = getattr(self, use_res, None)

            if test_call:
                result = await test_call(**arguments)
            else:
                raise Exception("method does not exist")
        else:
            result = []
        #use_prompt = self._bounded_tools.get(name)


        return MCPResponse.success(req_id=request_id,
                                   result={
                                       "contents":[MCPResource(uri=uri,
                                                              text=json.dumps(result))
                                                   ]
                                       }
                                   )

    async def default_call(self, *args, **kwargs):
        return {"args": args, "kwargs": kwargs}