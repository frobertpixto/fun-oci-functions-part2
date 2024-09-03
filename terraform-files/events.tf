# Create an OCI event
# - Triggers when a png or jpg is created in bucket: fun_oci_functions_bucket
# - Call our Text Anomaly Detection Function with an OCI Event as Payload
resource oci_events_rule image_created_in_bucket {
  actions {
    actions {
      action_type = "FAAS"
      description = "Call the Text Anomaly detection Function"
      function_id = var.text_anomaly_detection_fn_ocid
      is_enabled  = "true"
    }
  }
  compartment_id = var.compartment_ocid
  condition = <<-EOT
  {
    "eventType": ["com.oraclecloud.objectstorage.createobject"],
    "data": {
      "resourceName": ["*.png","*.jpg"],
      "additionalDetails": {
        "bucketName": ["fun_oci_functions_bucket"]
      }
    }
  }
  EOT
  description    = "Call a Function when an image is created in the bucket"
  display_name   = "create_image_in_bucket"
  is_enabled     = "true"
}

# Create an OCI event
# - Triggers when a pdf is created in bucket: fun_oci_functions_bucket
# - Call OCI Notification Services
resource oci_events_rule pdf_created_in_bucket {
  actions {
    actions {
      action_type = "ONS"
      topic_id = oci_ons_notification_topic.text_anomaly_topic.id
      is_enabled  = "true"
    }
  }
  compartment_id = var.compartment_ocid
  condition = <<-EOT
  {
    "eventType": ["com.oraclecloud.objectstorage.createobject"],
    "data": {
      "resourceName": ["*.pdf"],
      "additionalDetails": {
        "bucketName": ["fun_oci_functions_bucket"]
      }
    }
  }
  EOT
  description    = "Sends an email when a Document Generator PDF is created in a bucket"
  display_name   = "create_pdf_in_bucket"
  is_enabled     = "true"
}

