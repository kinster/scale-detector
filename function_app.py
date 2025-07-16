import os
import json
import logging
import azure.functions as func
from ScaleDetector import extract_scale

app = func.FunctionApp()

@app.function_name(name="extractscale")
@app.route(route="extractscale", auth_level=func.AuthLevel.ANONYMOUS)
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
            body=json.dumps({"scale": scale}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error: {str(e)}",
            status_code=500
        )
