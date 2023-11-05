import logging
from app.core.logger.custom_logging import CustomizeLogger
from pathlib import Path
from contextlib import asynccontextmanager
import shutil
import sentry_sdk
from debug_toolbar.middleware import DebugToolbarMiddleware
from fastapi import FastAPI
from mangum import Mangum
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
import os

# from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from starlette.middleware.cors import CORSMiddleware

# from app.api.endpoints import auth, query
from app.api.endpoints import query
from app.core.config import settings
from app.core.llama_index_funcs import initialize_index
from app.core.key_valut import load_secrets_to_env_var


class NoParsingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not record.getMessage().find("/docs") >= 0


# define lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # when start up
    ## Run the initial loading of secrets if it is online
    load_secrets_to_env_var()
    ## prepare the temp folders for LlamaIndex
    folders = ["documents", "vector_store"]
    for folder in folders:
        if not os.path.exists(folder):
            os.mkdir("documents")
            os.mkdir("vector_store")
    with open(f"{folders[0]}/place_holder.txt", "w") as f:
        f.write("placeholder")
    ## Run the initialization of Llama
    initialize_index()

    yield

    # when shut down
    ## delete the temp folders
    shutil.rmtree("documents")
    shutil.rmtree("vector_store")


# initialize FastAPI instance
def create_app() -> FastAPI:
    # define the app instance
    app = FastAPI(
        title=f"[{settings.ENV}]{settings.TITLE}",
        version=settings.VERSION,
        debug=settings.DEBUG or False,
        lifespan=lifespan
        # root_path=f"{settings.API_GATEWAY_STAGE_PATH}/",
    )
    # Set up custom logging
    config_path = Path(__file__).with_name("logging_config.json")
    app.logger = CustomizeLogger.make_logger(config_path)
    return app


app = create_app()

if settings.SENTRY_SDK_DNS:
    sentry_sdk.init(
        dsn=settings.SENTRY_SDK_DNS,
        # integrations=[SqlalchemyIntegration()],
        environment=settings.ENV,
    )


app.add_middleware(SentryAsgiMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_origin_regex=r"^https?:\/\/([\w\-\_]{1,}\.|)example\.com",
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["info"])
def get_info() -> dict[str, str]:
    return {"title": settings.TITLE, "version": settings.VERSION}


# app.include_router(auth.router, tags=["Auth"], prefix="/auth")
app.include_router(query.router, tags=["Query"], prefix="/query")

if settings.DEBUG:
    app.add_middleware(
        DebugToolbarMiddleware,
        panels=["debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel"],
    )


if settings.IS_API_GATEWAY:
    handler = Mangum(app)
