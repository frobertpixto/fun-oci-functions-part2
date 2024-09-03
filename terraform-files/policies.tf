# TextAnomalyDetection Function calls AI Service and Invokes Document Generator Function
# By default, a Function has no privileges.
# Allow TextAnomalyDetection Function to:
# - Use AI Service ai-service-vision-analyze-image
# - Get the Function endpoint
# - Call a Function (Document generator)
# - Read/Write in Object Storage

resource "oci_identity_policy" "fn_policy" {
    compartment_id = var.compartment_ocid
    description = "Allow a specific TextAnomalyDetection Function to use use AI Service and Document generator"
    name = "fun_oci_functions_policy2"
    statements = [
      "allow any-user to use ai-service-vision-analyze-image in compartment ${data.oci_identity_compartment.fn_compartment.name} where any { request.principal.id = '${var.text_anomaly_detection_fn_ocid}'}",
      "allow any-user to read fn-function in compartment ${data.oci_identity_compartment.fn_compartment.name} where any { request.principal.id = '${var.text_anomaly_detection_fn_ocid}'}",
      "allow any-user to use fn-invocation in compartment ${data.oci_identity_compartment.fn_compartment.name} where any { request.principal.id = '${var.text_anomaly_detection_fn_ocid}'}",
      "allow any-user to manage objects in compartment ${data.oci_identity_compartment.fn_compartment.name} where any { request.principal.id = '${var.text_anomaly_detection_fn_ocid}'}"
    ]
}