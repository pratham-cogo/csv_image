from services.images.models.processed_images import ProcessedImages
from fastapi import HTTPException, status
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def webhook(request_id: str):
    try:
        image_request: ProcessedImages = ProcessedImages.get(ProcessedImages.request_id == request_id)
        if image_request.status == 'completed':
            print(f"Processing complete for request {request_id}")
        else:
            raise HTTPException(status_code=400, detail="Processing not completed yet")

    except:
        logger.warning("Request not found in webhook")
        raise HTTPException(status_code=404, detail="Request not found")