from fastapi.responses import JSONResponse
from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from app import utils, models
from app.database import engine
from app.router import authentication, client, image_base64
import log
import asyncio
import uuid


app = FastAPI()


logger = log._init_logger()

models.Base.metadata.create_all(engine)


@app.middleware("http")
async def request_middleware(request, call_next):
    end_point = request.url.path
    request_id = str(uuid.uuid4())
    with logger.contextualize(request_id=request_id, end_point=end_point):
        logger.debug('--------------start--------------')

        try:
            return await call_next(request)
        except Exception as ex:
            print(ex)
            logger.error(f"Request failed: {ex}")
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                content={"error": {"type": "UnknownError",
                                                   "message": "Unknown error found.",
                                                   "fields": None}, "status": "failed"})
        finally:
            logger.debug('---------------end---------------')


@app.exception_handler(utils.ValidationException)
async def validation_exception_handler(request: Request, exc: utils.ValidationException):
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content={"error": exc.errors_out, "status": "failed"})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_out = utils.convert_error_pydantic(exc.errors())
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content={"error": error_out, "status": "failed"})


@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=1000)
    except asyncio.TimeoutError:
        return JSONResponse(status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                            content={"error": {"type": "TimeoutError", "message": "API timed out.", "fields": None},
                                     "status": "failed"})


app.include_router(authentication.router)
app.include_router(client.router)
app.include_router(image_base64.router)


