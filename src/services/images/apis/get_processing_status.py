from fastapi import HTTPException, status
from services.images.models.processed_images import ProcessedImages
from enums.image_enums import ProcessState
from typing import List, Dict
import logging
import uuid

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_processing_status(request_id: str, user_id: str) -> Dict[str, str]:
    try:
        image_requests : List[ProcessedImages] = list(ProcessedImages.select().where(
            ProcessedImages.request_id == uuid.UUID(request_id),
            ProcessedImages.user_id == uuid.UUID(user_id)
        ))

        if not image_requests:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
        
        completed_products = [req.product_name for req in image_requests if req.status == ProcessState.COMPLETED.value]

        return {
            "Processed_count": f"{len(completed_products)}",
            "Products_processed": completed_products,
        }

    except ValueError as e:
        logger.warning(f"Invalid UUID format for request_id: {request_id} or user_id: {user_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        logger.warning(f"Error while fetching processing status for request_id: {request_id} - {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching processing status")
