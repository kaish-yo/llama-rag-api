# import app.core.logger
import os
from fastapi import APIRouter, UploadFile, Request, Response, status
from app.core.llama_index_funcs import add_documents, query_index
from app.schemas.queries import QARequest
import logging
from llama_index import SimpleDirectoryReader

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
        result = query_index(question.query)
        return {"success": True, "answer": result}
    except Exception as e:
        logger.exception(f"querying the document failed with the following error:\n{result}")
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"success": False}


@router.post("/document")
def upload_document(file: UploadFile, request: Request, response: Response):
    """
    # 概要
    文書検索の元データとなるドキュメントをアップロードする
    """
    logger = request.app.logger
    # Make sure document folder is ready
    doc_dir = "documents"
    if not os.path.exists(doc_dir):
        os.makedirs(doc_dir)

    # Save the uploaded file to the local directory.
    with open(f"{doc_dir}/{file.filename}", "wb+") as f:
        f.write(file.file.read())
    add_documents(file.filename)
    logger.info("New documents added to vector store.")
    return {"filename": file.filename}


# @router.delete("/document", status_code=status.HTTP_200_OK)
# def delete_document(filename: str, request: Request, response: Response):
#     """
#     # 概要
#     アップロードしたファイルを削除する
#     """
#     logger = request.app.logger  # load the logger instance
#     doc_dir = "documents"
#     try:
#         os.remove(f"{doc_dir}/{filename}")
#     except Exception as e:
#         response.status_code = status.HTTP_400_BAD_REQUEST
#         # request.app.logger.exception(f"Failed to the file named:{filename}\nThe original error is:\n{e}")
#         logger.exception(f"Failed to the file named:{filename}\nThe original error is:\n{e}")
#         return {"success": False, "message": "Failed to delete the file."}
#     return {"success": False, "message": f"Successfully deleted the file: {filename}"}
