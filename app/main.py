from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from app.utils.jwt import decode_access_token
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.routers.warehouse import router as product_router
from app.routers.user_inventory import router as user_inventory_router

app = FastAPI(root_path="/api", root_path_in_servers="/api")

origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def access_token_middleware(request: Request, call_next):
    public_paths = [
        "/api/auth/login",
        "/api/auth/signup",
        "/api/status",
        "/docs",
        "/redoc",
        "/api/openapi.json",
    ]

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


@app.get("/status", tags=["Status"])
def status():
    return {"status": "OK", "message": "Server Is Running"}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(product_router, prefix="/product", tags=["Product Inventory"])
app.include_router(user_inventory_router, prefix="/product", tags=["User Inventory"])
