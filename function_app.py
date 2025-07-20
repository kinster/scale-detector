import cv2
import numpy as np
import os
import json
import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient

from ScaleDetector import extract_scale

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="extractscale")
@app.route(route="extractscale", methods=["POST"])
def ExtractScale(req: func.HttpRequest) -> func.HttpResponse:
    try:

        data = req.get_json()

        base64_img = data["base64"]
        endpoint = os.environ["AZURE_VISION_ENDPOINT"]
        key = os.environ["AZURE_VISION_KEY"]
        logging.info(endpoint)
        logging.info(key)

        logging.info('Python HTTP trigger function processed a request.')

        scale = extract_scale(base64_img, endpoint, key)

        logging.info(f"Detected scale: {scale}")
        # ✅ Wrap the dict in HttpResponse
        return func.HttpResponse(
            body=json.dumps({"scaley": scale}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error: {str(e)}",
            status_code=500
        )

@app.function_name(name="blobtrigger")
@app.blob_trigger(arg_name="blob",
                  path="pdf-images/{name}",
                  connection="AzureWebJobsStorage")
def run_blob_trigger(blob: func.InputStream):
    connect_string = os.environ["AzureWebJobsStorage"]
    logging.info(f"connect_string: {connect_string}")
    logging.info(f"Blob trigger fired for: {blob.name}")
    logging.info(f"Blob size: {blob.length} bytes")
    blob_data = blob.read()
    
    # Add your processing logic here
        # Process blob data (example)
    image = cv2.imdecode(np.frombuffer(blob_data, np.uint8), cv2.IMREAD_COLOR)
    logging.info(f"Image shape: {image.shape if image is not None else 'None'}")
    if image is not None:
        logging.info(f"start drawing lines on image: {blob.name}")
        from . import Drawing  # Assuming Drawing class is in another module
        drawer = Drawing(image)
        annotated_image = drawer.draw_lines([[100, 100, 200, 200]])  # Example
        _, img_encoded = cv2.imencode('.png', annotated_image)
        # Save to output blob (e.g., 'pdf-images/annotated_{blob.name}')
        blob_service_client = BlobServiceClient.from_connection_string(connect_string)
        blob_client = blob_service_client.get_blob_client(container="pdf-images", blob=f"annotated_{blob.name}")
        blob_client.upload_blob(img_encoded.tobytes(), overwrite=True)
        logging.info(f"Annotated image saved as: annotated_{blob.name}")
    else:
        logging.error("Failed to decode image")

