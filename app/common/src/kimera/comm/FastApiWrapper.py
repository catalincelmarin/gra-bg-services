import asyncio
import importlib
import json
import os

import socketio
import yaml
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles

from kimera.comm.BaseAuth import BaseAuth
from kimera.helpers.Helpers import Helpers

from kimera.store.StoreFactory import StoreFactory
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            print("An error occurred:", e)
            raise HTTPException(status_code=500, detail="An error occurred")


class FastAPIWrapper:
    def __init__(self):
        self._api = None
        self._sio = None
        self._sio_app = None
        self._auth: BaseAuth | None = None
        self._verbose = False

    @property
    def sio(self):
        return self._sio

    @property
    def app(self):
        return self._api

    async def socket(self, message, room, event="message", head=None, final=False, ):
        await asyncio.create_task(
            self.sio.emit(event=event, data={"body": message, "head": head, "final": final}, room=room))

    def runApi(self,auth: BaseAuth = None, verbose: bool = False):

        origins = os.getenv("ORIGINS", "").split(",")
        root_path = os.getenv("APP_PATH", None)
        if not root_path:
            raise Exception("Must add APP_PATH to .env")

        self._verbose = bool(verbose)
        folder_paths = [f"{root_path}/app/"]
        self._log("LOADING:", "EXT PATHS")

        self._append_extension_paths(root_path, folder_paths)


        self._api = FastAPI(docs_url=None, redoc_url=None)
        self._auth: BaseAuth = auth
        self._setup_middlewares(origins)
        self._setup_socket_io(origins)
        self._log("LOADING:", "APIs")
        self._setup_routes_from_yaml(folder_paths)

        self._log("LOADING:", "MCPs")
        self._setup_mcp_from_yaml(folder_paths=folder_paths)
        self._setup_custom_docs()
        self.setup_public_static("public/")

        return self

    @property
    def auth(self):
        return self._auth

    @auth.setter
    def auth(self, auth: BaseAuth):
        # optionally validate or transform before assignment
        self._auth = auth

    def _append_extension_paths(self, root_path, folder_paths):
        """Append paths from the 'ext' directory if it contains relevant route files."""
        self._log("APPENDING_TO", f"LOADING {root_path}")
        ext_path = os.path.join(f"{root_path}/app", "ext")

        if os.path.exists(ext_path):
            for dir_path, _, filenames in os.walk(ext_path):

                if any((f.startswith('routes.') or f.startswith('mcp.')) and f.endswith('.yaml') for f in filenames):
                    folder_paths.append(dir_path + "/")

        ext_path = os.path.join(f"{root_path}/app", "src")

        if os.path.exists(ext_path):
            for dir_path, _, filenames in os.walk(ext_path):
                if any((f.startswith('routes.') or f.startswith('mcp.')) and f.endswith('.yaml') for f in filenames):
                    folder_paths.append(dir_path + "/")


    def _setup_socket_io(self, origins):
        """Initialize and configure Socket.IO server."""
        sio = socketio.AsyncServer(async_mode="asgi", allow_credentials=True, cors_allowed_origins=origins)
        self._sio = sio
        sio_app = socketio.ASGIApp(socketio_server=sio, socketio_path="/socket.io/")
        self._api.mount("/socket.io/", sio_app)

        @sio.on("connect")
        async def connect(sid, env, auth):
            try:
                await self._auth.socket_auth(auth["token"])
            except ConnectionRefusedError:
                await sio.emit("message", "failed", sid)

        @sio.on("join_room")
        async def join_room(sid, rooms):
            """
            Join one or more rooms dynamically after connection.
            `data` should contain a `rooms` list or a single `room`.
            """

            try:
                if isinstance(rooms, str):
                    rooms = [rooms]

                for room in rooms:
                    await sio.enter_room(sid, room)

                await sio.emit("joined", {"rooms": rooms}, to=sid)

            except Exception as e:
                await sio.emit("error", {"error": str(e)}, to=sid)

        @sio.on("disconnect")
        async def disconnect(sid):
            await sio.emit("message", "disconnected")

    def _setup_routes_from_yaml(self, folder_paths):
        """Load and configure routes from YAML files."""
        for folder_path in folder_paths:

            files = [f for f in os.listdir(folder_path) if f.endswith(".yaml") and f.startswith("routes.")]

            for file in files:
                if file.startswith("routes."):
                    self._process_route_file(os.path.join(folder_path, file), self._api)
    @staticmethod
    def _resolve_dir(current_yaml_path: str, tools_value: str | None) -> dict | None:
        if not tools_value:
            return None
        base_dir = os.path.dirname(current_yaml_path)
        abs_dir = os.path.normpath(os.path.join(base_dir, tools_value))
        return {"dir": abs_dir}

    def _setup_mcp_from_yaml(self, folder_paths):
        """Load and configure routes from YAML files."""
        # Helpers.print("FOLDER PATHS", folder_paths)
        for folder_path in folder_paths:

            files = [f for f in os.listdir(folder_path) if f.startswith("mcp.") and f.endswith(".yaml")]

            for file in files:
                self._process_mcp_file(os.path.join(folder_path, file), self._api)

    def _process_mcp_file(self, file_path, app):
        """Load individual YAML configuration and setup associated routes and sockets."""
        if not os.path.exists(file_path):
            raise Exception(f"{file_path} does not exist")

        with open(file_path, "r") as yaml_file:
            config_data = yaml.safe_load(yaml_file)
        # Helpers.print(config_data)
        mcp_path = config_data.get("mcp")
        g_auth = config_data.get("auth", False)

        if mcp_path:
            module = importlib.import_module(mcp_path)
            class_name = mcp_path.split(".")[-1]
            tools_cfg = FastAPIWrapper._resolve_dir(file_path, config_data.get("tools"))
            prompts_cfg = FastAPIWrapper._resolve_dir(file_path, config_data.get("prompts"))
            resources_cfg = FastAPIWrapper._resolve_dir(file_path, config_data.get("resources"))
            instance = getattr(module, class_name)(server_config=config_data,
                                                   tools_config=tools_cfg,
                                                   prompts_config=prompts_cfg,
                                                   resources_config=resources_cfg
                                                   )

            # Mount MCP default routes with raw-body passthrough
            for route in getattr(instance, "default_routes", []):
                action_name = route["action"]
                handle_request = getattr(instance, action_name)
                requires_auth = route.get("auth", g_auth)
                dependencies = []
                if requires_auth:
                    dependencies.append(Depends(self._auth.get_auth))



                self._api.add_api_route(
                    instance.path + route["path"],
                    handle_request,
                    methods=[route["method"]],
                    dependencies=dependencies
                )
        else:
            raise Exception(f"Missing mcp path in {file_path}")
            # No sockets for MCP
            return

    def _log(self, subject, info=""):
        if self._verbose:
            Helpers.sysPrint(subject, info)



    def _process_route_file(self, file_path, app):
        """Load individual YAML configuration and setup associated routes and sockets."""
        with open(file_path, "r") as yaml_file:
            config_data = yaml.safe_load(yaml_file)

        dxs_path = config_data.get("dxs")
        g_auth = config_data.get("auth",False)
        if not dxs_path:
            raise ValueError(f"{file_path} is missing the 'dxs' key")

        module = importlib.import_module(dxs_path)
        class_name = dxs_path.split(".")[-1]
        instance = getattr(module, class_name)(config_data)

        for route in instance.routes[::-1]:
            handle_request = getattr(instance, route["action"])
            requires_auth = route.get("auth",g_auth)
            dependencies = []
            if requires_auth:
                dependencies.append(Depends(self._auth.get_auth))

            app.add_api_route(
                instance.path + route["path"],
                handle_request,
                methods=[route["method"]],
                dependencies=dependencies
            )

        self._setup_socket_routes(config_data.get("sockets", []), instance)

    def _setup_socket_routes(self, socket_routes, instance):
        """Configure socket routes as defined in the YAML configuration."""
        for socket_route in socket_routes:
            socket_name = socket_route["name"]
            action_handler = getattr(instance, socket_route["action"])

            async def socket_handler(sid, data, action=action_handler, socket=socket_name):
                try:
                    parsed_data = json.loads(data) if isinstance(data, str) else data
                    await action({"sid": sid, **parsed_data})

                except json.JSONDecodeError:
                    await action({"sid": sid, "data": data})

            self._sio.on(socket_name)(socket_handler)

    def _setup_custom_docs(self):
        """Configure custom API documentation routes."""
        app = self._api

        @app.get("/docs", include_in_schema=False)
        async def custom_swagger_ui_html():
            return get_swagger_ui_html(
                openapi_url=app.openapi_url,
                title=f"{app.title} - Swagger UI",
                oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
                swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
                swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
            )

        @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
        async def swagger_ui_redirect():
            return get_swagger_ui_oauth2_redirect_html()

        @app.get("/redoc", include_in_schema=False)
        async def redoc_html():
            return get_redoc_html(
                openapi_url=app.openapi_url,
                title=f"{app.title} - ReDoc",
                redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
            )

    def setup_public_static(self,route="",path="",html=False):
        """Serve static files from a public directory."""
        public_path = StoreFactory.get_fstore("_public").path(path)
        self._api.mount(f"/{route}", StaticFiles(directory=public_path,html=html), name="public")




    def _setup_middlewares(self, origins):
        """Configure application-level middlewares."""
        self._api.add_middleware(
            CORSMiddleware,
            allow_headers="*",
            allow_methods="*",
            allow_origins=origins
        )


        @self._api.middleware("http")
        async def checkRoute(request: Request, call_next):
            """Custom middleware to rewrite headers and manage authentication tokens."""
            api_key = None
            request.state.token = None
            authorization_header = request.headers.get("Authorization")
            if authorization_header and authorization_header.startswith("Bearer "):
                api_key = authorization_header.split("Bearer ")[1].strip()
                request.state.token = api_key

            response = await call_next(request)

            # Apply custom CORS headers if path is /socket.io
            if request.url.path.startswith("/socket.io/"):
                del response.headers["Access-Control-Allow-Origin"]

            return response

        # self._api.add_middleware(ExceptionMiddleware)

    # def _setup_socket_io(self, origins):
    #     """Initialize and configure Socket.IO server."""
    #     sio = socketio.AsyncServer(async_mode="asgi", allow_credentials=True, cors_allowed_origins=origins)
    #     self._sio = sio
    #     sio_app = socketio.ASGIApp(socketio_server=sio, socketio_path="/socket.io/")
    #     self._api.mount("/socket.io/", sio_app)
    #
    #     @sio.on("connect")
    #     async def connect(sid, env, auth):
    #         try:
    #             await self._auth.socket_auth(auth["token"])
    #         except ConnectionRefusedError:
    #             await sio.emit("message", "failed", sid)
    #
    #     @sio.on("join_room")
    #     async def join_room(sid, rooms):
    #         """
    #         Join one or more rooms dynamically after connection.
    #         `data` should contain a `rooms` list or a single `room`.
    #         """
    #
    #         try:
    #             if isinstance(rooms, str):
    #                 rooms = [rooms]
    #
    #             for room in rooms:
    #                 await sio.enter_room(sid, room)
    #
    #             await sio.emit("joined", {"rooms": rooms}, to=sid)
    #
    #         except Exception as e:
    #             await sio.emit("error", {"error": str(e)}, to=sid)
    #
    #     @sio.on("disconnect")
    #     async def disconnect(sid):
    #         await sio.emit("message", "disconnected")




    # def _setup_socket_routes(self, socket_routes, instance):
    #     """Configure socket routes as defined in the YAML configuration."""
    #     for socket_route in socket_routes:
    #         socket_name = socket_route["name"]
    #         action_handler = getattr(instance, socket_route["action"])
    #
    #         async def socket_handler(sid, data, action=action_handler, socket=socket_name):
    #             try:
    #                 parsed_data = json.loads(data) if isinstance(data, str) else data
    #                 await action({"sid": sid, **parsed_data})
    #
    #             except json.JSONDecodeError:
    #                 await action({"sid": sid, "data": data})
    #
    #         self._sio.on(socket_name)(socket_handler)
    #
    # def _setup_custom_docs(self):
    #     """Configure custom API documentation routes."""
    #     app = self._api
    #
    #     @app.get("/docs", include_in_schema=False)
    #     async def custom_swagger_ui_html():
    #         return get_swagger_ui_html(
    #             openapi_url=app.openapi_url,
    #             title=f"{app.title} - Swagger UI",
    #             oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
    #             swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
    #             swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
    #         )
    #
    #     @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    #     async def swagger_ui_redirect():
    #         return get_swagger_ui_oauth2_redirect_html()
    #
    #     @app.get("/redoc", include_in_schema=False)
    #     async def redoc_html():
    #         return get_redoc_html(
    #             openapi_url=app.openapi_url,
    #             title=f"{app.title} - ReDoc",
    #             redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
    #         )
    #
    # def setup_public_static(self,route="",path="",html=False):
    #     """Serve static files from a public directory."""
    #     public_path = StoreFactory.get_fstore("_public").path(path)
    #     self._api.mount(f"/{route}", StaticFiles(directory=public_path,html=html), name="public")
