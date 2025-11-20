from fastapi import FastAPI
from routes import base, data, nlp
from helpers.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient  # pyright: ignore[reportMissingImports]
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderInterface import VectorDBProviderInterface
from stores.llm.templates.template_parser import TemplateParser

app = FastAPI()


# -----------------------------
# Startup event
# -----------------------------
@app.on_event("startup")
async def startup_span():
    settings = get_settings()

    # MongoDB connection
    app.mongo_conn = AsyncIOMotorClient(settings.MONGO_URL)
    app.db_client = app.mongo_conn[settings.MONGO_DB_NAME]

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
    app.mongo_conn.close()
    app.vectordb_client.disconnect()


# -----------------------------
# Routers
# -----------------------------
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
