from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except ValueError as e:
            return JSONResponse(status_code=400, content={"detail": str(e)})
        except Exception as e:
            return JSONResponse(
                status_code=500, content={"detail": "Erro interno do servidor"}
            )
