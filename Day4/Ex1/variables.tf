variable "project_id" {
  description = "The ID of the GCP project"
  type        = string
}

variable "region" {
  description = "The region to deploy resources"
  type        = string
  default     = "asia-southeast1"
}

variable "zone" {
  description = "The zone to deploy VM instance"
  type        = string
  default     = "asia-southeast1-a"
}

variable "instance_name" {
  description = "The name of the VM instance"
  type        = string
  default     = "data-processing-vm"
}

variable "machine_type" {
  description = "The machine type for the VM instance"
  type        = string
  default     = "e2-medium"
}

variable "instance_tags" {
  description = "Network tags for the VM instance"
  type        = list(string)
  default     = ["data-processing"]
}