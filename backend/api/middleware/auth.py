from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def auth_middleware(request: Request, call_next):
    """Simple authentication middleware"""
    try:
        # Skip auth for health checks and docs
        if request.url.path in ["/", "/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Add your authentication logic here
        # For now, we'll just log the request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        response = await call_next(request)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Middleware error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )