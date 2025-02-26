import logging
from uuid import uuid4
from contextvars import ContextVar
from fastapi.requests import Request
from fastapi import Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from peewee import PostgresqlDatabase
from traceback import format_exc
from src.auth import decode_access_token

log = logging.getLogger(__name__)

REQUEST_ID_CTX_KEY = "request_id"
_request_id_ctx_var: ContextVar[str | None] = ContextVar(REQUEST_ID_CTX_KEY, default=None)

def get_request_id() -> str | None:
    """Retrieve the current request ID from the context."""
    return _request_id_ctx_var.get()

def get_current_user(request: Request):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return user

class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ):
        # Whitelist public endpoints (e.g., docs, openapi.json, health check, etc.)
        public_paths = ["/docs", "/openapi.json", "/health", "/"]
        if request.url.path in public_paths:
            return await call_next(request)
        
        ctx_token = None
        try:
            request_id = str(uuid4())
            ctx_token = _request_id_ctx_var.set(request_id)

            # Authenticate the request
            token = request.headers.get("Authorization")
            if not token or not token.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization token missing",
                )

            token = token.split(" ")[1]
            user_info = decode_access_token(token)
            if not user_info:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                )

            request.state.user = user_info

            request.state.db = PostgresqlDatabase.get_instance()
            if request.state.db.is_closed():
                request.state.db.connect(reuse_if_open=True)

            response = await call_next(request)

            if response.status_code >= 400:
                request.state.db.rollback()
            else:
                request.state.db.commit()

        except HTTPException as e:
            log.error(f"HTTPException: {str(e)}")
            return JSONResponse(
                status_code=e.status_code,
                content={"success": False, "error": str(e.detail)},
            )
        except Exception as e:
            log.error(f"Unhandled Exception: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"success": False, "error": str(e), "traceback": format_exc()},
            )
        finally:
            if hasattr(request.state, "db") and not request.state.db.is_closed():
                request.state.db.close()

            if ctx_token:
                _request_id_ctx_var.reset(ctx_token)

        return response
