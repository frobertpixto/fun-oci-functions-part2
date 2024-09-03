import oci


def invoke_function(oci_cfg, signer, fn_ocid: str, fn_payload: str):
    """
    Invokes an OCI function with the specified payload.

    This function handles the setup and invocation of an OCI function identified by its Oracle Cloud Identifier (OCID).
    It retrieves the function's details, configures the invocation client, and sends a request with the provided payload.

    Args:
        oci_cfg (dict): The OCI configuration dictionary containing necessary credentials and settings.
        signer (object): A security signer object used for authenticating requests to OCI services.
        fn_ocid (str): The OCID of the OCI function to be invoked.
        fn_payload (str): The JSON string payload to be sent to the function.

    Returns:
        bytes: The response data from the function invocation.
    """
    # Create a Functions Management Client
    fn_management_client = oci.functions.FunctionsManagementClient(oci_cfg, signer=signer)

    # Retrieve the details of the specified function using its OCID.
    fn = fn_management_client.get_function(fn_ocid).data

    # Create a Functions Invoke Client.
    # In general: Set READ timeout same as Function timeout if using more than 60 seconds of CPU
    invoke_client = oci.functions.FunctionsInvokeClient(
        oci_cfg,
        service_endpoint=fn.invoke_endpoint,  # The endpoint to which the function invocation needs to be sent.
        signer=signer,
        timeout=(10, fn.timeout_in_seconds)
    )

    # Perform the function invocation using the function ID and the provided payload.
    resp = invoke_client.invoke_function(fn.id, invoke_function_body=fn_payload)

    # Return the response data from the function invocation.
    return resp.data
