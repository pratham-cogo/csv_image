from fastapi import BackgroundTasks, HTTPException, status
from services.images.models.processed_images import ProcessedImages
from services.images.apis.upload_image import upload_image
import pandas as pd
from database.db import db
from enums.image_enums import ProcessState
import uuid, re
import requests, logging
from PIL import Image
from io import BytesIO
from typing import Tuple, Union, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def process_images(file_path: str, user_id: str, background_tasks: BackgroundTasks) -> str:
    with db.atomic():
        return execute(file_path, user_id, background_tasks)

def execute(file_path: str, user_id: str, background_tasks: BackgroundTasks) -> str:
    is_valid, df_or_error = validate_csv(file_path)
    if not is_valid:
        raise ValueError(df_or_error)  

    request_id: str = uuid.uuid4()

    background_tasks.add_task(process_images_background, df_or_error, request_id, user_id)

    return request_id

def process_images_background(df: pd.DataFrame, request_id: str, user_id: str) -> None:
    logger.info(f"Starting background task for request_id: {request_id}")
    try:
        for _, row in df.iterrows():
            logger.info(f"Processing product: {row['Product Name']}")

            input_urls = row["Input Image Urls"].split(",") if isinstance(row["Input Image Urls"], str) else list(row["Input Image Urls"])

            image_request: ProcessedImages = ProcessedImages.create(
                request_id=request_id,
                user_id=user_id,
                input_image_urls=input_urls,
                product_name=row["Product Name"],
                status=ProcessState.PROCESSING.value,
            )
            logger.info(f"Created database entry for product: {row['Product Name']}")

            output_urls: list[str] = []
            for url in input_urls:
                logger.info(f"Compressing image: {url}")
                compressed_image = compress_image(url)
                if compressed_image:
                    logger.info(f"Uploading compressed image for: {url}")
                    output_url = upload_image(compressed_image)
                    if output_url:
                        output_urls.append(output_url)

            if len(output_urls) != len(input_urls):
                raise ValueError(f"Mismatch in input and output URLs for product {row['Product Name']}")

            image_request.output_image_urls = output_urls
            image_request.status = ProcessState.COMPLETED.value
            image_request.save()
            logger.info(f"Finished processing product: {row['Product Name']}")

    except Exception as e:
        logger.error(f"Error processing request_id: {request_id}. Error: {str(e)}")

        try:
            deleted_count = ProcessedImages.delete().where(ProcessedImages.request_id == request_id).execute()
            logger.info(f"Cleaned up {deleted_count} rows for request_id: {request_id}")
        except Exception as cleanup_error:
            logger.error(f"Failed to clean up after error: {str(cleanup_error)}")

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Image processing failed")

    logger.info(f"Background task completed for request_id: {request_id}")



def validate_csv(file_path: str) -> Tuple[bool, Union[pd.DataFrame, str]]:
    try:
        logger.info(f"Starting CSV validation for file: {file_path}")

        df = pd.read_csv(file_path)
        required_columns = ["S. No.", "Product Name", "Input Image Urls"]

        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            logger.error(f"CSV is missing required columns: {missing_cols}")
            return False, f"CSV is missing required columns: {missing_cols}"

        logger.info(f"All required columns are present. Validating {len(df)} rows...")

        url_pattern = re.compile(r"https?://[^\s]+")

        valid_rows = 0

        for index, row in df.iterrows():
            if not isinstance(row["Product Name"], str) or not row["Product Name"].strip():
                logger.error(f"Invalid 'Product Name' at row {index + 1}: {row['Product Name']}")
                return False, f"Invalid 'Product Name' at row {index + 1}: {row['Product Name']}"

            input_urls = row["Input Image Urls"].split(",")
            if not input_urls or not all(url_pattern.match(url.strip()) for url in input_urls):
                logger.error(f"Invalid 'Input Image Urls' at row {index + 1}: {row['Input Image Urls']}")
                return False, f"Invalid 'Input Image Urls' at row {index + 1}: {row['Input Image Urls']}"

            valid_rows += 1

        logger.info(f"CSV validation successful. {valid_rows}/{len(df)} rows passed.")
        return True, df

    except Exception as e:
        logger.exception(f"Error reading or validating CSV: {str(e)}")
        return False, f"Error reading CSV: {str(e)}"

def compress_image(image_url: str, quality: int = 50) -> Optional[BytesIO]:
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))

        output_buffer = BytesIO()
        image.save(output_buffer, format="JPEG", quality=quality)
        output_buffer.seek(0)
        return output_buffer
    except Exception as e:
        logger.warning(f"Failed to compress image: {str(e)}")
        return None
