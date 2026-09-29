"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

import os
import mimetypes
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI, HTTPException, Request, Response, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.security import HTTPBasic, HTTPBasicCredentials
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
else:
    # Optional-dep shim: FastAPI is an optional dependency; these names are
    # types when imported and None when absent.
    try:
        from fastapi import FastAPI, HTTPException, Request, Response, Depends
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.security import HTTPBasic, HTTPBasicCredentials
        from fastapi.staticfiles import StaticFiles
        from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
    except ImportError:
        FastAPI = HTTPException = Request = Response = Depends = None
        CORSMiddleware = HTTPBasic = HTTPBasicCredentials = None
        StaticFiles = FileResponse = HTMLResponse = RedirectResponse = None

from signalwire.core.security_config import SecurityConfig
from signalwire.core.config_loader import ConfigLoader
from signalwire.core.logging_config import get_logger

logger = get_logger("web_service")


class WebService:
    """Static file serving service with HTTP API.

    Each mounted directory is served below its route, with basic auth. One
    route serves them all and looks the request path up in ``directories``
    on every request, so ``add_directory()`` and ``remove_directory()`` take
    effect at once. A path is refused if any of its components starts with a
    dot or is a blocked name, or if it resolves, symbolic links followed, to
    somewhere outside its mounted directory.
    """

    def __init__(
        self,
        port: int = 8002,
        directories: dict[str, str] | None = None,
        basic_auth: tuple[str, str] | None = None,
        config_file: str | None = None,
        enable_directory_browsing: bool = False,
        allowed_extensions: list[str] | None = None,
        blocked_extensions: list[str] | None = None,
        max_file_size: int = 100 * 1024 * 1024,  # 100MB default
        enable_cors: bool = True,
    ):
        """
        Initialize WebService

        Args:
            port: Port to bind to (default: 8002)
            directories: Dict mapping URL paths to local directories
            basic_auth: Optional tuple of (username, password)
            config_file: Optional configuration file path
            enable_directory_browsing: Allow directory listing
            allowed_extensions: List of allowed file extensions (e.g., ['.html', '.css'])
            blocked_extensions: Blocked extensions and file names (e.g.,
                ['.env', '.pem']). An entry is also refused as the name of
                any directory on the path. Whatever this holds, a path with a
                component that starts with a dot is never served.
            max_file_size: Maximum file size in bytes to serve
            enable_cors: Enable CORS support
        """
        # Load configuration first
        self._load_config(config_file)

        # Override with constructor params if provided
        self.port = port
        self.enable_directory_browsing = enable_directory_browsing
        self.max_file_size = max_file_size
        self.enable_cors = enable_cors

        if directories is not None:
            self.directories = directories

        # Set up file extension filters
        self.allowed_extensions = allowed_extensions
        self.blocked_extensions = blocked_extensions or [
            ".env",
            ".git",
            ".gitignore",
            ".key",
            ".pem",
            ".crt",
            ".pyc",
            "__pycache__",
            ".DS_Store",
            ".swp",
        ]

        # Initialize mimetypes
        mimetypes.init()
        # Add custom MIME types if needed
        mimetypes.add_type("application/javascript", ".js")
        mimetypes.add_type("text/css", ".css")
        mimetypes.add_type("application/json", ".json")

        # Load security configuration
        self.security = SecurityConfig(config_file=config_file, service_name="web")
        self.security.log_config("WebService")

        # Set up authentication. The source is reported at startup, as
        # AgentBase does, and start() refuses to run on a generated password,
        # which nothing would ever show.
        if basic_auth:
            self._basic_auth = basic_auth
            self._basic_auth_source: Any = "provided"
        else:
            self._basic_auth = self.security.get_basic_auth()
            self._basic_auth_source = self.security.basic_auth_source or "provided"

        # Set once the route that serves the mounted directories is registered
        self._files_route_registered = False

        self.app: FastAPI | None = None
        if FastAPI is not None:
            self.app = FastAPI(
                title="SignalWire Web Service",
                description="Static file serving for SignalWire Agents",
            )
            self._setup_security()
            self._setup_routes()
            self._mount_directories()
        else:
            self.app = None
            logger.warning("FastAPI not available. HTTP service will not be available.")

    def _load_config(self, config_file: str | None) -> None:
        """Load configuration from file if available"""
        # Initialize defaults
        self.directories = {}
        self.port = 8002

        # Find config file
        if not config_file:
            config_file = ConfigLoader.find_config_file("web")

        if not config_file:
            return

        # Load config
        config_loader = ConfigLoader([config_file])
        if not config_loader.has_config():
            return

        logger.info("loading_config_from_file", file=config_file)

        # Get service section
        service_config = config_loader.get_section("service")
        if service_config:
            if "port" in service_config:
                self.port = int(service_config["port"])

            if "directories" in service_config and isinstance(
                service_config["directories"], dict
            ):
                self.directories = service_config["directories"]

            if "enable_directory_browsing" in service_config:
                self.enable_directory_browsing = bool(
                    service_config["enable_directory_browsing"]
                )

            if "max_file_size" in service_config:
                self.max_file_size = int(service_config["max_file_size"])

            if "allowed_extensions" in service_config:
                self.allowed_extensions = service_config["allowed_extensions"]

            if "blocked_extensions" in service_config:
                self.blocked_extensions = service_config["blocked_extensions"]

    def _setup_security(self) -> None:
        """Setup security middleware and authentication"""
        if not self.app:
            return

        # Add CORS middleware if enabled
        if self.enable_cors and CORSMiddleware is not None:
            self.app.add_middleware(CORSMiddleware, **self.security.get_cors_config())

        # Add security headers middleware
        @self.app.middleware("http")
        async def add_security_headers(
            request: "Request",
            call_next: "Callable[[Request], Awaitable[Response]]",
        ) -> "Response":
            response = await call_next(request)

            # Add security headers
            is_https = request.url.scheme == "https"
            headers = self.security.get_security_headers(is_https)
            for header, value in headers.items():
                response.headers[header] = value

            # Add cache headers for static files
            path = request.url.path
            if path != "/health" and self._match_mount(path) is not None:
                # Cache static files for 1 hour
                response.headers["Cache-Control"] = "public, max-age=3600"

            return response

        # Add host validation middleware
        @self.app.middleware("http")
        async def validate_host(
            request: "Request",
            call_next: "Callable[[Request], Awaitable[Response]]",
        ) -> "Response":
            host = request.headers.get("host", "").split(":")[0]
            if host and not self.security.should_allow_host(host):
                return Response(content="Invalid host", status_code=400)

            return await call_next(request)

    def _get_current_username(
        self, credentials: Optional["HTTPBasicCredentials"] = None
    ) -> str | None:
        """Validate basic auth credentials"""
        if not credentials:
            return None

        correct_username, correct_password = self._basic_auth

        # Compare credentials
        import secrets

        username_correct = secrets.compare_digest(
            credentials.username, correct_username
        )
        password_correct = secrets.compare_digest(
            credentials.password, correct_password
        )

        if not (username_correct and password_correct):
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Basic"},
            )

        return credentials.username

    def _is_path_allowed(self, parts: tuple[str, ...]) -> bool:
        """Check the components of a path below a mounted directory.

        A component that starts with a dot is refused wherever it appears, so
        nothing under ``.git`` or ``.ssh`` is served and neither is a file
        such as ``.env.production``. The exception is ``.well-known``, the
        standard public location for ACME challenges and ``security.txt``.
        Directory listings hide dot entries. A component equal to a blocked
        entry is refused too, so a blocked name covers a directory as well as
        a file.
        """
        blocked = set(self.blocked_extensions)
        return not any(
            (part.startswith(".") and part != ".well-known") or part in blocked
            for part in parts
        )

    def _match_mount(self, path: str) -> tuple[str, str, str] | None:
        """The mounted directory that serves ``path``, or None.

        Returns ``(route, directory, rest)``, where ``rest`` is the part of
        the path below the route. A route matches at a path-segment boundary,
        so ``/docs`` serves ``/docs`` and ``/docs/a.html`` but not
        ``/docsx``, and the longest matching route wins. A route of ``/``
        matches every path.
        """
        best: tuple[str, str, str] | None = None
        for route, directory in list(self.directories.items()):
            prefix = "/" + route.strip("/")
            if prefix == "/":
                rest = path.lstrip("/")
            elif path == prefix or path.startswith(prefix + "/"):
                rest = path[len(prefix) :].lstrip("/")
            else:
                continue
            if best is None or len(prefix) > len(best[0]):
                best = (prefix, directory, rest)
        return best

    def _is_file_allowed(self, file_path: Path) -> bool:
        """Check if file is allowed to be served"""
        # Check file size
        try:
            if file_path.stat().st_size > self.max_file_size:
                return False
        except (OSError, FileNotFoundError):
            return False

        # Check extension and name
        ext = file_path.suffix.lower()
        name = file_path.name

        # Check blocked extensions and names
        for blocked in self.blocked_extensions:
            if blocked.startswith("."):
                # Check both as extension and as full name (for files like .env, .gitignore)
                if ext == blocked or name == blocked:
                    return False
            else:
                if name == blocked or blocked in str(file_path):
                    return False

        # If allowed_extensions is set, only allow those
        if self.allowed_extensions:
            return ext in self.allowed_extensions

        return True

    def _generate_directory_listing(self, directory: Path, url_path: str) -> str:
        """Generate HTML directory listing"""
        items = []

        # Add parent directory link if not at root
        if url_path != "/":
            items.append('<li><a href="../">../</a></li>')

        # List directories first
        for item in sorted(directory.iterdir()):
            if item.name.startswith("."):
                continue  # Skip hidden files

            if item.is_dir() and self._is_path_allowed((item.name,)):
                from html import escape

                safe_name = escape(item.name, quote=True)
                items.append(f'<li>📁 <a href="{safe_name}/">{safe_name}/</a></li>')

        # Then list files
        for item in sorted(directory.iterdir()):
            if item.name.startswith("."):
                continue

            if item.is_file() and self._is_file_allowed(item):
                size = item.stat().st_size
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size / (1024 * 1024):.1f} MB"

                from html import escape

                safe_name = escape(item.name, quote=True)
                items.append(
                    f'<li>📄 <a href="{safe_name}">{safe_name}</a> ({size_str})</li>'
                )

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Directory listing for {__import__("html").escape(url_path)}</title>
            <style>
                body {{ font-family: sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                ul {{ list-style: none; padding: 0; }}
                li {{ padding: 5px 0; }}
                a {{ text-decoration: none; color: #0066cc; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>Directory listing for {__import__("html").escape(url_path)}</h1>
            <ul>
                {"".join(items)}
            </ul>
        </body>
        </html>
        """

    def _setup_routes(self) -> None:
        """Setup FastAPI routes"""
        if not self.app:
            return

        # Create security dependency if HTTPBasic is available
        security = HTTPBasic() if HTTPBasic is not None else None

        @self.app.get("/health")
        async def health() -> dict[str, Any]:
            return {
                "status": "healthy",
                "directories": list(self.directories.keys()),
                "ssl_enabled": self.security.ssl_enabled,
                "auth_required": bool(security),
                "directory_browsing": self.enable_directory_browsing,
            }

        @self.app.get("/", response_model=None)
        async def root(request: "Request") -> "Response | dict[str, Any]":
            """Root endpoint showing available directories.

            With a directory mounted at ``/``, serves that directory instead.
            """
            if self._match_mount("/") is not None:
                credentials = await security(request) if security else None
                return self._serve_request(request, credentials, "/")

            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>SignalWire Web Service</title>
                <style>
                    body { font-family: sans-serif; margin: 40px; }
                    h1 { color: #333; }
                    ul { list-style: none; padding: 0; }
                    li { padding: 10px 0; }
                    a { text-decoration: none; color: #0066cc; font-size: 18px; }
                    a:hover { text-decoration: underline; }
                    .path { color: #666; font-size: 14px; }
                </style>
            </head>
            <body>
                <h1>SignalWire Web Service</h1>
                <h2>Available Directories:</h2>
                <ul>
            """

            for route, local_path in self.directories.items():
                html += f'<li>📁 <a href="{route}">{route}</a> <span class="path">→ {local_path}</span></li>'

            html += """
                </ul>
            </body>
            </html>
            """

            if HTMLResponse is not None:
                return HTMLResponse(content=html)
            return {"directories": list(self.directories.keys())}

    def _mount_directories(self) -> None:
        """Register the route that serves every mounted directory.

        The route reads ``directories`` on every request, so it is registered
        once; a later call only logs mounted directories that can't be
        served.
        """
        if not self.app or StaticFiles is None:
            return

        for route, directory in self.directories.items():
            dir_path = Path(directory)
            if not dir_path.exists():
                logger.warning(f"Directory does not exist: {directory}")
            elif not dir_path.is_dir():
                logger.warning(f"Path is not a directory: {directory}")
            else:
                logger.info(f"Mounting directory {directory} at route {route}")

        if self._files_route_registered:
            return
        self._files_route_registered = True

        # Create security dependency if HTTPBasic is available
        security = HTTPBasic() if HTTPBasic is not None else None

        @self.app.get("/{request_path:path}", response_model=None)
        async def serve_file(
            request_path: str,
            request: "Request",
            credentials: Optional["HTTPBasicCredentials"] = (
                None if not security else Depends(security)  # noqa: B008  # FastAPI DI: Depends() in default is the intended idiom
            ),
        ) -> "Response":
            """Serve a file from the mounted directory the path falls under"""
            return self._serve_request(request, credentials, "/" + request_path)

    def _serve_request(
        self,
        request: "Request",
        credentials: Optional["HTTPBasicCredentials"],
        path: str,
    ) -> "Response":
        """Serve ``path`` from the mounted directory it falls under.

        ``path`` is the request path as routed, without any prefix the app
        is mounted under.

        Raises:
            HTTPException: 401 for bad credentials, 403 for a refused path,
                404 when nothing is mounted there or the file doesn't exist.
        """
        if HTTPBasic is not None:
            self._get_current_username(credentials)

        match = self._match_mount(path)
        if match is None:
            raise HTTPException(status_code=404, detail="Not Found")
        _route, directory, rest = match

        # Security: refuse hidden and blocked components, then anything that
        # resolves outside the mounted directory, symbolic links followed
        if not self._is_path_allowed(Path(rest).parts):
            raise HTTPException(status_code=403, detail="Access denied")
        try:
            dir_path = Path(directory).resolve()
            full_path = (dir_path / rest).resolve()
        except Exception:
            raise HTTPException(status_code=403, detail="Invalid path") from None
        if not self._is_inside(full_path, dir_path):
            raise HTTPException(status_code=403, detail="Access denied")

        # Check if path exists
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Handle directory requests
        if full_path.is_dir():
            # Relative links in a listing or an index page need the slash
            if not path.endswith("/") and RedirectResponse is not None:
                return RedirectResponse(url=request.url.path + "/", status_code=307)
            if not self.enable_directory_browsing:
                # Try to serve index.html if it exists
                index_path = (full_path / "index.html").resolve()
                if (
                    self._is_inside(index_path, dir_path)
                    and index_path.is_file()
                    and self._is_file_allowed(index_path)
                ):
                    return FileResponse(index_path)
                raise HTTPException(
                    status_code=403, detail="Directory browsing disabled"
                )
            # Generate directory listing
            html = self._generate_directory_listing(full_path, request.url.path)
            if HTMLResponse is not None:
                return HTMLResponse(content=html)
            raise HTTPException(
                status_code=403,
                detail="Directory browsing not available",
            )

        # Check if file is allowed
        if not self._is_file_allowed(full_path):
            raise HTTPException(status_code=403, detail="File type not allowed")

        # Serve the file
        mime_type = (
            mimetypes.guess_type(str(full_path))[0] or "application/octet-stream"
        )

        if FileResponse is not None:
            return FileResponse(
                full_path,
                media_type=mime_type,
                headers={
                    "Cache-Control": "public, max-age=3600",
                    "X-Content-Type-Options": "nosniff",
                },
            )
        # Fallback if FileResponse not available
        with full_path.open("rb") as f:
            content = f.read()
        return Response(
            content=content,
            media_type=mime_type,
            headers={
                "Cache-Control": "public, max-age=3600",
                "X-Content-Type-Options": "nosniff",
            },
        )

    def _is_inside(self, path: Path, dir_path: Path) -> bool:
        """True if resolved ``path`` is resolved ``dir_path`` or below it,
        and its components below it pass :meth:`_is_path_allowed`."""
        if path != dir_path and not str(path).startswith(str(dir_path) + os.sep):
            return False
        return self._is_path_allowed(path.relative_to(dir_path).parts)

    def add_directory(self, route: str, directory: str) -> None:
        """
        Add a new directory to serve

        Takes effect at once, on a running service too. Adding a route that
        is already mounted points it at the new directory.

        Args:
            route: URL path to mount at (e.g., "/docs"), with or without its
                leading or trailing slash
            directory: Local directory path to serve
        """
        # Verify directory exists
        dir_path = Path(directory)
        if not dir_path.exists():
            raise ValueError(f"Directory does not exist: {directory}")

        if not dir_path.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        self.remove_directory(route)
        self.directories["/" + route.strip("/")] = directory
        logger.info(f"Mounting directory {directory} at route {route}")

    def remove_directory(self, route: str) -> None:
        """
        Remove a directory from being served

        Takes effect at once: the route's files stop being served with the
        next request.

        Args:
            route: URL path to remove, with or without its leading or
                trailing slash
        """
        normalized = "/" + route.strip("/")
        for existing in [
            r for r in self.directories if "/" + r.strip("/") == normalized
        ]:
            del self.directories[existing]

    def start(
        self,
        host: str = "0.0.0.0",  # noqa: S104  # intended server default: listen on all interfaces (overridable)
        port: int | None = None,
        ssl_cert: str | None = None,
        ssl_key: str | None = None,
    ) -> None:
        """
        Start the service with optional HTTPS support

        Args:
            host: Host to bind to (default: "0.0.0.0")
            port: Port to bind to (default: self.port)
            ssl_cert: Path to SSL certificate file (overrides environment)
            ssl_key: Path to SSL key file (overrides environment)
        """
        if not self.app:
            raise RuntimeError("FastAPI not available. Cannot start HTTP service.")

        port = port or self.port

        if self._basic_auth_source == "generated":
            raise RuntimeError(
                "WebService needs basic-auth credentials: set "
                "SWML_BASIC_AUTH_USER and SWML_BASIC_AUTH_PASSWORD, pass "
                "basic_auth=(user, password), or set security.auth.basic in "
                "the config file. A generated password is never shown, so "
                "every file request would be refused."
            )

        # Get SSL configuration
        ssl_kwargs: dict[str, Any] = {}
        if ssl_cert and ssl_key:
            # Use provided SSL files
            ssl_kwargs = {"ssl_certfile": ssl_cert, "ssl_keyfile": ssl_key}
        else:
            # Use security config SSL settings
            ssl_kwargs = self.security.get_ssl_context_kwargs()

        # Build startup URL
        scheme = "https" if ssl_kwargs else "http"
        startup_url = f"{scheme}://{host}:{port}"

        # Get auth credentials
        username, _password = self._basic_auth

        # Log startup information
        logger.info(
            "starting_web_service",
            url=startup_url,
            ssl_enabled=bool(ssl_kwargs),
            directories=list(self.directories.keys()),
            username=username,
        )

        # Print user-friendly startup message
        print("\nSignalWire Web Service starting...")
        print(f"URL: {startup_url}")
        print(
            f"Directories: {', '.join(self.directories.keys()) if self.directories else 'None'}"
        )
        print(
            f"Basic Auth: {username}:(credentials configured) "
            f"(source: {self._basic_auth_source})"
        )
        print(
            f"Directory Browsing: {'Enabled' if self.enable_directory_browsing else 'Disabled'}"
        )
        if ssl_kwargs:
            print("SSL: Enabled")
        print("")

        try:
            import uvicorn

            uvicorn.run(self.app, host=host, port=port, **ssl_kwargs)
        except ImportError:
            raise RuntimeError(
                "uvicorn not available. Cannot start HTTP service."
            ) from None

    def stop(self) -> None:
        """Stop the service (placeholder for cleanup)"""
        pass
