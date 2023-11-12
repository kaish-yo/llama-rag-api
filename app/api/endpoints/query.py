# import app.core.logger
import os
from fastapi import APIRouter, BackgroundTasks, UploadFile, Request, Response, status
from app.core.llama_index_funcs import add_documents, initialize_index, query_index
from app.schemas.queries import QARequest
import logging
from llama_index import SimpleDirectoryReader
import shutil

logger = logging.getLogger(__name__)

router = APIRouter()

index = None


@router.post("/generate", status_code=status.HTTP_200_OK)
def generate(question: QARequest, request: Request, response: Response):
    """
    # 概要
    Q&Aの本文を受け取り、検索結果を返す
    """
    logger = request.app.logger
    try:
        logger.info(f"{question=}")
        result = query_index(question.query)
        return {"success": True, "answer": result}
    except Exception as e:
        logger.exception(f"querying the document failed with the following error:\n{e}")
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"success": False}


@router.post("/document")
async def upload_document(file: UploadFile, request: Request, response: Response, background_tasks: BackgroundTasks):
    """
    # 概要
    文書検索の元データとなるドキュメントをアップロードする
    """
    logger = request.app.logger
    # Make sure document folder is ready
    doc_dir = "documents"
    if not os.path.exists(doc_dir):
        os.makedirs(doc_dir)

    # Define the background task
    def task_function():
        # Save the uploaded file to the local directory.
        with open(f"{doc_dir}/{file.filename}", "wb+") as f:
            f.write(file.file.read())
        add_documents(file.filename)
        logger.info("New documents added to vector store.")

    background_tasks.add_task(task_function)  # add the task to the background task

    return {"filename": file.filename}


@router.delete("/documents", status_code=status.HTTP_200_OK)
def reset_documents(request: Request, response: Response):
    """
    # 概要
    ドキュメントDBをリセットする
    """
    logger = request.app.logger  # load the logger instance
    try:
        shutil.rmtree("documents")
        shutil.rmtree("vector_store")

        os.mkdir("documents")
        os.mkdir("vector_store")
        with open(f"documents/place_holder.txt", "w") as f:
            f.write("placeholder")
        initialize_index()

    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        # request.app.logger.exception(f"Failed to the file named:{filename}\nThe original error is:\n{e}")
        logger.exception(e)
        return {"success": False, "message": "Failed to reset the document database."}
    return {"success": False, "message": "Document database has been reset."}
