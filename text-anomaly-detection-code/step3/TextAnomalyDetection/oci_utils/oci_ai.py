import oci
from oci.ai_vision.models import AnalyzeImageDetails, ImageTextDetectionFeature, ObjectStorageImageDetails

def detect_text_from_oject_storage_image(oci_cfg, signer, compartment_id: str, namespace_name: str, bucket_name: str, object_name: str):
    """
    Detects text within an image stored in Oracle Cloud Infrastructure (OCI) Object Storage using OCI AI Vision Service.

    This function configures and sends a request to the OCI AI Vision Service to detect text in a specified image.
    It sets up the details of the image stored in Object Storage and specifies the features of text detection to be used.

    Args:
        oci_cfg (dict): The OCI configuration dictionary containing necessary credentials and settings.
        signer (object): A security signer object used for authenticating requests to OCI services.
        compartment_id (str): The OCI compartment ID where the service and storage are located.
        namespace_name (str): The namespace of the OCI Object Storage where the image is stored.
        bucket_name (str): The name of the OCI Object Storage bucket containing the image.
        object_name (str): The name of the image file to analyze for text detection.

    Returns:
        dict: A dictionary containing the analyzed image results, converted from the AI Vision service response.

    Raises:
        Exception: Any exceptions raised during the API call will propagate, indicating issues like network errors,
                   authentication problems, or misconfigurations in the request parameters.
    """
    # Create an AI Vision client
    ai_vision_client = oci.ai_vision.AIServiceVisionClient(oci_cfg, signer=signer)

    # Set up the details of the image to be analyzed.
    image_details = ObjectStorageImageDetails()
    image_details.bucket_name = bucket_name
    image_details.namespace_name = namespace_name
    image_details.object_name = object_name

    # Configure the features for text detection
    feature = ImageTextDetectionFeature()
    feature.feature_type = "TEXT_DETECTION"
    feature.language = "ENG"
    feature.max_results = 10

    # List of features to apply, could be expanded with additional features in the future.
    features = [feature]

    # Prepare the complete request with image and feature details
    analyze_image_details = AnalyzeImageDetails()
    analyze_image_details.image = image_details
    analyze_image_details.features = features
    analyze_image_details.compartment_id = compartment_id

    # Call the AI Vision service to analyze the image and return the response.
    response = ai_vision_client.analyze_image(analyze_image_details=analyze_image_details)

    # Convert the response object to a dictionary for easier handling
    return oci.util.to_dict(response.data)
