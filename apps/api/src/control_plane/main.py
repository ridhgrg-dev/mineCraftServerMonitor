import logging
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from control_plane.core.dependencies import Resources
from control_plane.core.logging import configure_logging, request_id_context
from control_plane.core.settings import Settings

logger = logging.getLogger("control_plane")


class Health(BaseModel):
    status: Literal["ok"]


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


def error_response(request: Request, status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request.state.request_id,
            }
        },
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings if settings is not None else Settings()  # type: ignore[call-arg]
    configure_logging()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        resources = Resources.create(config)
        app.state.resources = resources
        logger.info("api.started")
        try:
            yield
        finally:
            await resources.close()
            logger.info("api.stopped")

    app = FastAPI(
        title="Server operations control plane",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None if config.environment == "production" else "/docs",
        redoc_url=None,
        openapi_url=None if config.environment == "production" else "/openapi.json",
    )

    @app.middleware("http")
    async def correlation(request: Request, call_next: RequestResponseEndpoint) -> Response:
        supplied = request.headers.get("x-request-id", "")
        request.state.request_id = (
            supplied if re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", supplied) else str(uuid4())
        )
        token = request_id_context.set(request.state.request_id)
        try:
            try:
                response = await call_next(request)
            except Exception:
                logger.error("request.failed")
                response = error_response(
                    request, 500, "internal.error", "An internal error occurred."
                )
            response.headers["X-Request-ID"] = request.state.request_id
            logger.info("request.completed")
            return response
        finally:
            request_id_context.reset(token)

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
        return error_response(
            request, exc.status_code, "http.error", "The request could not be completed."
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return error_response(request, 422, "request.invalid", "The request is invalid.")

    @app.get("/health/live", response_model=Health, operation_id="get_liveness")
    async def live() -> Health:
        return Health(status="ok")

    @app.get(
        "/health/ready",
        response_model=Health,
        operation_id="get_readiness",
        responses={503: {"model": ErrorResponse}},
    )
    async def ready(request: Request) -> Health | JSONResponse:
        try:
            await request.app.state.resources.check_ready()
        except Exception:
            logger.warning("readiness.unavailable")
            return error_response(
                request, 503, "dependency.unavailable", "A required dependency is unavailable."
            )
        return Health(status="ok")

    return app
