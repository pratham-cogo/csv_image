from fastapi.responses import StreamingResponse
import io
import csv
import logging
import uuid
from typing import List
from fastapi import HTTPException
from services.images.models.processed_images import ProcessedImages
from enums.image_enums import ProcessState

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def webhook(request_id: str):
    try:
        req_uuid = uuid.UUID(request_id)
    except Exception as e:
        logger.warning(f"Invalid request_id format: {request_id}")
        raise HTTPException(status_code=400, detail="Invalid request ID format.")
    
    records: List[ProcessedImages] = list(
        ProcessedImages.select().where(ProcessedImages.request_id == req_uuid)
    )
    
    if not records:
        raise HTTPException(status_code=404, detail="No records found for the provided request ID.")
    
    if any(record.status != ProcessState.COMPLETED.value for record in records):
        return {"detail": "Processing is not complete yet."}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["S. No.", "Product Name", "Input Image Urls", "Output Image Urls"])
    
    for idx, record in enumerate(records, start=1):
        input_urls = ", ".join(record.input_image_urls) if record.input_image_urls else ""
        output_urls = ", ".join(record.output_image_urls) if record.output_image_urls else ""
        writer.writerow([idx, record.product_name, input_urls, output_urls])
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),  # Ensuring correct encoding
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=processed_{request_id}.csv"
        }
    )
