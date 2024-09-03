import io
import json
import logging
import sys
import decimal
import oci 
from fdk import response

from oci_utils.oci_ai import detect_text_from_oject_storage_image
from oci_utils.oci_functions import invoke_function
from oci_utils.oci_document_generator import prepare_document_generator_payload

# Setting the decimal context to round down, to ease the Display of fraction
decimal.getcontext().rounding = decimal.ROUND_DOWN

# Configure logging to output debug information to the standard output stream.
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


# The compartment OCID under which operations will be performed. <<<
compartment_id = "ocid1.compartment.oc1..zzz"

# The OCID of the Document Generator function. <<<
fn_ocid = "ocid1.fnfunc.oc1.iad..zzz"


fontfile_name = "part2/Monoton.zip"
template_name = "part2/TextAnomalyTemplate.docx"

# Create a signer object using the Cloud Shell Resource Principal for authenticating requests.
signer = oci.auth.signers.get_resource_principals_signer()
oci_config= {}

#
# Utility Functions
#

def all_texts_are_clear_in_the_image(detect_text_response: dict, confidence_level: float = 0.90):
    """
    Checks if all detected texts in an image meet a specified confidence level.

    Args:
        detect_text_response (dict): The response dictionary from text detection containing words and their confidence.
        confidence_level (float): The minimum confidence level required for each text to be considered clear.

    Returns:
        bool: True if all texts have a confidence level above the specified threshold, False otherwise.
    """
    words = detect_text_response.get("image_text", {}).get("words", [])
    return all(word.get("confidence", 0) >= confidence_level for word in words)


def generate_doc_gen_data_content_from_ai_response(detect_text_response: dict, bucket_name: str, namespace: str, object_name: str):
    """
    Transforms text detection response into a format suitable for generating documents with the OCI Document Generator.

    Args:
        detect_text_response (dict): The response from the text detection API.
        bucket_name (str): The name of the OCI Object Storage bucket where the image is stored.
        namespace (str): The namespace of the OCI Object Storage where the bucket resides.
        object_name (str): The name of the object (image) in the bucket for which text detection was performed.

    Returns:
        dict: A dictionary formatted to be used as payload for document generation.
    """
    words = detect_text_response.get("image_text", {}).get("words", [])
    data_content = {
        "image_with_anomalies": {
            "source": "OBJECT_STORAGE",
            "objectName": object_name,
            "namespace": namespace,
            "bucketName": bucket_name,
            "mediaType": "image/png" if object_name.endswith("png") else "image/jpeg",
            "height": "450px"
        },
        "words": [
            {
                "word": word.get("text"),
                "confidence": round(word.get("confidence", 0) * 100, 1),
                "corner1": {
                    "x": round(word.get("bounding_polygon", {}).get("normalized_vertices", [])[0].get("x", 0), 2),
                    "y": round(word.get("bounding_polygon", {}).get("normalized_vertices", [])[0].get("y", 0), 2)
                },
                "corner3": {
                    "x": round(word.get("bounding_polygon", {}).get("normalized_vertices", [])[2].get("x", 0), 2),
                    "y": round(word.get("bounding_polygon", {}).get("normalized_vertices", [])[2].get("y", 0), 2)
                }
            }
            for word in words
        ]
    }
    return data_content


def prepare_response(ctx, response_message: str):
    return response.Response(
                ctx, response_data=json.dumps(
                {"message": response_message}),
                headers={"Content-Type": "application/json"})


def handler(ctx, data: io.BytesIO = None):
    """
    Handles incoming OCI event:
    1. Processes images for text detection
    2. If some of the Texts in the Image are Unclear
      3. Generates a report based on the detected text

    Args:
        ctx: The context object provided by OCI Functions, containing metadata and configurations.
        data (io.BytesIO): The bytes of the JSON payload containing details about the OCI event and the image to process.
    """
    logging.info("Inside Python Text Anomaly Detection function")

    if data is None:
        message = "No data provided"
        logging.error(message)
        return prepare_response(ctx, message)

    try:
        #
        # Parse the event data to extract necessary details for processing.
        #
        payload = json.loads(data.getvalue())
        logging.info(f"Received event: {json.dumps(payload)}")

        image_name = payload["data"]["resourceName"]
        bucket_name = payload["data"]["additionalDetails"]["bucketName"]
        namespace = payload["data"]["additionalDetails"]["namespace"]

        logging.info(f'Processing Image: "{image_name}" from Bucket: "{bucket_name}" in Namespace: "{namespace}"')

        #
        # Detect text in the specified object storage image.
        #
        detect_text_response = detect_text_from_oject_storage_image(oci_config, signer, compartment_id, namespace, bucket_name, image_name)
        logging.debug(f"detect_text_response: {detect_text_response}")

        #
        # Do we have anomalies in some detected Words?
        #
        if all_texts_are_clear_in_the_image(detect_text_response):
            logging.info(
                f'All Words are clear in Image: "{image_name}" from Bucket: "{bucket_name}" in Namespace: "{namespace}". Processing Complete')
            # No -> Stop    
            return prepare_response(ctx, "All Words are clear in Image")
        else:
            logging.info(
                f'Anomalies found in Image: "{image_name}". Generating PDF Document')

        #
        # Generate a PDF report using the OCI Document generator PBF
        #

        # Generate the Data that will be in the report based on AI Text analysis.
        data_content = generate_doc_gen_data_content_from_ai_response(detect_text_response, bucket_name, namespace, image_name)

        # Prepare payload for the Document Generator function.
        doc_gen_fn_payload = prepare_document_generator_payload(data_content, namespace, bucket_name, image_name, fontfile_name, template_name)

        # Invoke the Document Generator function
        response = invoke_function(oci_config, signer, fn_ocid, doc_gen_fn_payload)
        document_generator_response = response.content.decode()
        logging.debug(f"DocGen Response: status code: {response.status_code}, result: {document_generator_response}")

        # Handling response and logging based on the statuses.
        if response.status_code == 200:  # This is the Function HTTP response
            document_generator_response_dict = json.loads(document_generator_response)
            app_response_code = document_generator_response_dict.get("code")

            if app_response_code == 200:  # This is the Document generation application response
                response_message = "Document generated successfully"
            else:
                response_message = f"Document generation failure: '{app_response_code}'. See Application Log"

            logging.info(response_message)
            return prepare_response(ctx, response_message)

    except Exception as ex:
        # Log any exceptions that occur during processing.
        logging.info('Error in handler: ' + str(ex))
        raise
