variable region { 
    default = "us-ashburn-1" 
}

variable compartment_ocid {
    description  = "OCID of the compartment to use"
}

variable text_anomaly_detection_fn_ocid {
    description  = "OCID of our Text Anomaly Detection Function"
}

variable email_address_to_receive_notifications {
    description  = "Email address that will receive a Notification when Text anomalies are detected"
}

data "oci_identity_compartment" "fn_compartment" {
  id = var.compartment_ocid
}

# Output the compartment name
output "compartment_name" {
  value = data.oci_identity_compartment.fn_compartment.name
}
