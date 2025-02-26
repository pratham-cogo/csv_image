from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from middlewares import get_current_user
from services.images.apis.get_processing_status import get_processing_status
from services.images.apis.process_image import process_images
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

image_router = APIRouter()

@image_router.post("/upload")
async def upload_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    try:
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        request_id = await process_images(file_path, user["id"], background_tasks)
        return {"request_id": request_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        import os
        if os.path.exists(file_path):
            os.remove(file_path)

@image_router.get("/status")
def get_status(request_id: str, user: dict = Depends(get_current_user)):
    return get_processing_status(request_id=request_id, user_id=user["id"])
    
# @image_router.post("/webhook")
# async def receive_webhook(file: UploadFile = File(...)):
#     content = await file.read()
#     logger.warning()