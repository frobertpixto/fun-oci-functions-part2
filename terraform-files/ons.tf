# Create an OCI Notification Service Topic
resource oci_ons_notification_topic text_anomaly_topic {
  compartment_id  = var.compartment_ocid
  description     = "Topic for Text Anomaly Detection"
  name            = "text_anomaly_topic"
}

# Create an OCI Notification Service Subscription that sends an email
resource oci_ons_subscription text_anomaly_subscription {
  compartment_id  = var.compartment_ocid
  delivery_policy = <<-EOT
    {
      "backoffRetryPolicy": {
        "maxRetryDuration": 7200000,
        "policyType": "EXPONENTIAL"
      }
    }
    EOT 
#  delivery_policy = "{\"backoffRetryPolicy\":{\"maxRetryDuration\":7200000,\"policyType\":\"EXPONENTIAL\"}}"
  endpoint        = var.email_address_to_receive_notifications
  protocol        = "EMAIL"
  topic_id        = oci_ons_notification_topic.text_anomaly_topic.id
}

