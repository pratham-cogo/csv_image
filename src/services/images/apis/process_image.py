from fastapi import BackgroundTasks
from services.images.models.processed_images import ProcessedImages
from services.images.apis.upload_image import upload_image
import pandas as pd
from database.db import db
import uuid, requests, logging
from PIL import Image
from io import BytesIO

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def process_images(file_path, user_id, background_tasks: BackgroundTasks):
    with db.atomic():
        execute(file_path, user_id, background_tasks)

def execute(file_path, user_id, background_tasks: BackgroundTasks):
    is_valid, df_or_error = validate_csv(file_path)
    if not is_valid:
        raise ValueError(df_or_error)

    request_id = uuid.uuid4()

    for item in df_or_error:
        image_request = ProcessedImages.create(
            request_id=request_id,
            user=user_id,
            input_image_urls=item["Input Image Urls"].tolist(),
            product_name=item["Product Name"],
            status="processing",
        )

        background_tasks.add_task(process_images_background, item, image_request)

    return request_id

def process_images_background(df, image_request: ProcessedImages):
    output_urls = []
    input_urls = df["Input Image Urls"].split(",")
    for url in input_urls:
        compressed_image = compress_image(url)

        if compressed_image:
            output_url = upload_image(compressed_image)

            if output_url:
                output_urls.append(output_url)
                image_request.processed_count += 1
                image_request.save()

    # Update the ImageRequest entry
    image_request.output_image_urls = ",".join(output_urls)
    image_request.status = "completed"
    image_request.save()

    # Trigger webhook on completion
    # trigger_webhook(image_request.request_id)


def validate_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        required_columns = ["S. No.", "Product Name", "Input Image Urls"]
        if not all(col in df.columns for col in required_columns):
            return False, "CSV is missing required columns."
        return True, df
    except Exception as e:
        return False, f"Error reading CSV: {str(e)}"
    
def compress_image(image_url, quality=50):
    try:
        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))

        # Compress the image
        output_buffer = BytesIO()
        image.save(output_buffer, format="JPEG", quality=quality)
        output_buffer.seek(0)

        return output_buffer
    except Exception as e:
        logger.warning(f"Failed to compress image: {str(e)}")
        return None