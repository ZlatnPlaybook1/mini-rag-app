from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from .schemas.nlp import PushRequest, SearchRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models import ResponseSingnals
from controllers import NLPController
import logging
import inspect

# silence Cohere provider logs ONLY
logging.getLogger("src.stores.llm.providers.CohereProvider").setLevel(logging.CRITICAL)
logging.getLogger("src.stores.llm.providers.OpenAIProvider").setLevel(logging.CRITICAL)


logger = logging.getLogger("uvicorn.error")
nlp_router = APIRouter(prefix="/api/v1/nlp", tags=["api_v1", "nlp"])


@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request,
                        project_id: str,
                        push_request: PushRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSingnals.PROJECT_NOT_FOUND_ERROR.value}
        )

    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client
    )

    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0

    while has_records:
        page_chunks = await chunk_model.get_project_chunks(
            project_id=project.id, 
            page_no=page_no
        )

        if not page_chunks:
            has_records = False
            break

        page_no += 1
        chunk_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)

        result = nlp_controller.index_into_vector_db(
            project=project,
            chunks=page_chunks,
            do_reset=push_request.do_reset,
            chunk_ids=chunk_ids
        )

        if inspect.isawaitable(result):
            is_inserted = await result
        else:
            is_inserted = result

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSingnals.INSERT_INTO_VECTORDB_ERROR.value}
            )

        inserted_items_count += len(page_chunks)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSingnals.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }
    )

@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSingnals.PROJECT_NOT_FOUND_ERROR.value}
        )
    
    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client
    )

    collection_info = nlp_controller.get_vector_db_collection_info(project=project)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSingnals.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info
        }
    )

@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: str, search_request: SearchRequest):
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSingnals.PROJECT_NOT_FOUND_ERROR.value}
        )

    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client
    )

    try:
        results = await nlp_controller.search_vector_db_collection(
            project=project,
            text=search_request.text,
            limit=search_request.limit or 10
        )
    except Exception as exc:
        request.app.logger.exception("Vector DB search failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"signal": ResponseSingnals.VECTORDB_SEARCH_ERROR.value, "error": str(exc)}
        )

    if results is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSingnals.VECTORDB_SEARCH_ERROR.value}
        )

    return JSONResponse(
        content={
            "signal": ResponseSingnals.VECTOTDB_SEARCH_SUCCESS.value,
            "results": results
        }
    )


