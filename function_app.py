import cv2
import numpy as np
import os
import io
import json
import logging
import base64
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

        connect_string = os.environ["AzureWebJobsStorage"]
        blob_name = "from_http_request.png"  # Or generate a unique name

        # def fix_base64_padding(b64_string):
        #     return b64_string + '=' * (-len(b64_string) % 4)

        # image_data = np.frombuffer(base64.b64decode(fix_base64_padding(base64_img)), np.uint8)

        if "," in base64_img:
            base64_img = base64_img.split(",")[1]

        scale = extract_scale(base64_img, endpoint, key)

        logging.info(f"Detected scale: {scale}")
        # ✅ Wrap the dict in HttpResponse
        return func.HttpResponse(
            body=json.dumps({"scale": scale}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error: {str(e)}",
            status_code=500
        )
