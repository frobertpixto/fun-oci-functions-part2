import io
import json
import logging

from fdk import response


def handler(ctx, data: str):
    """
    Handles incoming OCI event by looging its content

    Args:
        ctx: The context object provided by OCI Functions, containing metadata and configurations.
        data (str): The JSON string payload containing details about the OCI event and the image to process.
    """    
    logging.getLogger().setLevel(logging.INFO)
    try:
        event = json.load(data)
        logging.info(f"Received event: {json.dumps(event)}")  # Single-line log

        # Additional processing can be added here if needed
        return "Event logged successfully"
    except Exception as e:
        logging.error(f"Error processing event: {str(e)}")
        return "Error logging event"     
