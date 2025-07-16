import base64
import io
import time
import re
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials


def extract_scale(base64_image, endpoint, key):

    if "," in base64_image:
        base64_image = base64_image.split(",")[1]
    image_bytes = base64.b64decode(base64_image)
    image_stream = io.BytesIO(image_bytes)

    client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

    # Start OCR process
    read_response = client.read_in_stream(image_stream, raw=True)
    operation_location = read_response.headers["Operation-Location"]
    operation_id = operation_location.split("/")[-1]

  # Wait for completion
    while True:
        read_result = client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # Find "Scale" line
    scale_line = None
    all_lines = []

    for page in read_result.analyze_result.read_results:
        for line in page.lines:
            all_lines.append(line)
            if "scale" in line.text.lower():
                scale_line = line

    if not scale_line:
        return "Scale label not found"

    # Find nearby lines
    def is_nearby(line1, line2, threshold=50):
        x1 = sum(line1.bounding_box[::2]) / 4
        y1 = sum(line1.bounding_box[1::2]) / 4
        x2 = sum(line2.bounding_box[::2]) / 4
        y2 = sum(line2.bounding_box[1::2]) / 4
        return abs(y2 - y1) < threshold and abs(x2 - x1) < 200 and line2 != line1

    possible_matches = [
        line for line in all_lines
        if is_nearby(scale_line, line) and "scale" not in line.text.lower()
    ]

    # Try extracting from matches
    for match in possible_matches:
        m = re.search(r"\d+\s*[:/]\s*\d+", match.text)
        if m:
            return m.group(0)

    return "Scale value not found"