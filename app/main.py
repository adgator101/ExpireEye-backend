from fastapi import FastAPI, Request
from app.routes.auth import router as auth_router
from app.routes.product import router as product_router
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from app.utils.jwt import decode_access_token

app = FastAPI(root_path="/api", root_path_in_servers="/api")


@app.middleware("http")
async def access_token_middleware(request: Request, call_next):
    public_paths = ["/api/auth/login", "/api/auth/signup", "/api/status"]

    # Skip access token check for public paths
    if request.url.path in public_paths:
        return await call_next(request)

    access_token = request.cookies.get("access_token")
    if not access_token:
        return JSONResponse(
            status_code=401,
            content={"detail": "Access token is missing or invalid."},
        )
    try:
        payload = decode_access_token(access_token)
        request.state.user = payload  # Store user info in request state

    except Exception as e:
        return JSONResponse(
            status_code=401,
            content={"detail": "Access token is invalid."},
        )

    response = await call_next(request)
    return response


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    errors = exc.errors()
    custom_errors = [
        {
            "field": err["loc"][-1],
            "message": (
                "This field is required."
                if err["msg"] == "field required"
                else err["msg"]
            ),
        }
        for err in errors
    ]
    return JSONResponse(status_code=422, content={"errors": custom_errors})


@app.get("/status")
def status():
    return {"status": "OK", "message": "Server Is Running"}


app.include_router(auth_router, prefix="/auth")
app.include_router(product_router, prefix="/product")
