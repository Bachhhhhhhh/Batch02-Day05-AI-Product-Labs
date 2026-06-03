import os
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
from app.api.api_router import router as api_router
from app.core.logger import system_logger

app = FastAPI(title="Long Chau OTC Finder API")

# Setup static directory relative to this file
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# Include API router
app.include_router(api_router, prefix="/api")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    system_logger.info(
        f"Path: {request.url.path} | Method: {request.method} | "
        f"Status: {response.status_code} | Time: {process_time:.2f}ms"
    )
    return response

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    system_logger.warning(f"HTTP Exception at {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "message": exc.detail}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    system_logger.error(f"Global Exception at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Đã xảy ra lỗi hệ thống nghiêm trọng. Đội ngũ kỹ thuật đã được thông báo."
        }
    )

# Serve static files
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Defaults configured in app.core.config
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
