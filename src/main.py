from fastapi import FastAPI
from routes import base, data, nlp
from helpers.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient  # pyright: ignore[reportMissingImports]
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderInterface import VectorDBProviderInterface
from stores.llm.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine ,AsyncSession
from sqlalchemy.orm import sessionmaker

app = FastAPI()


# -----------------------------
# Startup event
# -----------------------------
@app.on_event("startup")
async def startup_span():
    settings = get_settings()

    # MongoDB connection
    # app.mongo_conn = AsyncIOMotorClient(settings.MONGO_URL)
    # app.db_client = app.mongo_conn[settings.MONGO_DB_NAME]

    # Postgres connection
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    app.db_engine = create_async_engine(postgres_conn)
    app.db_client = sessionmaker(
        app.db_engine , class_=AsyncSession , expire_on_commit=False
    )

    # Factories
    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderInterface(settings)

    # Generation client
    app.generation_client = llm_provider_factory.create(
        provider=settings.GENERATION_BACKEND
    )
    app.generation_client.set_generation_model(
        model_id=settings.GENERATION_MODEL_ID
    )

    # Embedding client
    app.embedding_client = llm_provider_factory.create(
        provider=settings.EMBEDDING_BACKEND
    )
    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_MODEL_SIZE,
    )

    # Vector DB client
    app.vectordb_client = vectordb_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND
    )
    app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG
    )


# -----------------------------
# Shutdown event
# -----------------------------
@app.on_event("shutdown")
async def shutdown_span():
    # app.mongo_conn.close()
    app.db_engine.dispose()
    app.vectordb_client.disconnect()


# -----------------------------
# Routers
# -----------------------------
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
