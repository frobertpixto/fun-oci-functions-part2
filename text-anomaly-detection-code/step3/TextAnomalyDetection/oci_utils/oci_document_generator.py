import json


def prepare_document_generator_payload(data_content, namespace, bucket_name, image_name, fontfile_name, template_name):
    """
    Prepares the JSON payload for invoking the OCI Document Generator function.

    This function formats the necessary details into a JSON structure expected by the OCI Document Generator.
    It specifies the sources for data, templates, and fonts, and defines the output specifications.

    Args:
        data_content (dict): The content data that will be used by the Document Generator to populate the template.
        namespace (str): The OCI Object Storage namespace where the template, fonts, and output will be stored.
        bucket_name (str): The name of the OCI Object Storage bucket for accessing or storing the image, template, fonts and output file.
        image_name (str): The name of the image file stored in Object Storage in which anomalies were found.
        fontfile_name (str): The name of the font file stored in Object Storage to be used in the document generation.
        template_name (str): The name of the document template file stored in Object Storage.

    Returns:
        str: A JSON string representing the payload for the Document Generator function.

    Description of the Document generator Payload:
        - The `data` section specifies the data to be used in the document.
        - The `template` section specifies the location and type of the template file.
        - The `fonts` section defines the font file to be used in the document.
        - The `output` section defines the output specifications, including file name.
    """

    # Generate the output file name based on the template name
    output_name = image_name + ".pdf"

    # Define the payload as a dictionary.
    payload_dict = {
        "requestType": "SINGLE",  # Indicates a single document generation request.
        "tagSyntax": "DOCGEN_1_0",
        "data": {
            "source": "INLINE",  # Data source is inline, directly included in the payload.
            "content": data_content  # The actual content data to be used in the document.
        },
        "template": {
            "source": "OBJECT_STORAGE",  # Template is stored in OCI Object Storage.
            "namespace": namespace,
            "bucketName": bucket_name,
            "objectName": template_name,
            "contentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"  # MS-Word
        },
        "fonts": {
            "source": "OBJECT_STORAGE",  # Font file is stored in OCI Object Storage.
            "namespace": namespace,
            "bucketName": bucket_name,
            "objectName": fontfile_name,
            "contentType": "application/zip"  # Fonts bundle are in a zip file.
        },
        "output": {
            "target": "OBJECT_STORAGE",  # Output to be stored in OCI Object Storage.
            "namespace": namespace,
            "bucketName": bucket_name,
            "objectName": output_name,  # Final output file name.
            "contentType": "application/pdf"  # Generate a PDF
        }
    }

    # Convert the dictionary to a JSON string to be sent in the function invocation.
    payload = json.dumps(payload_dict)
    return payload