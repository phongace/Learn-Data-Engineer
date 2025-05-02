variable "project_id" {
  description = "The ID of the project"
  type        = string
  default     = "unique-axle-457602-n6"
}

variable "region" {
  description = "The region to deploy resources"
  type        = string
  default     = "asia-southeast1"
}

variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "data-processing"
}

variable "environment" {
  description = "The environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "storage_class" {
  description = "The storage class for the bucket"
  type        = string
  default     = "STANDARD"
}

variable "bucket_location" {
  description = "The location for the bucket"
  type        = string
  default     = "ASIA-SOUTHEAST1"
}

variable "kms_key_name" {
  description = "The Cloud KMS key to use for bucket encryption"
  type        = string
  default     = null
}

variable "lifecycle_rules" {
  description = "List of lifecycle rules for the bucket"
  type = list(object({
    action = object({
      type          = string
      storage_class = string
    })
    condition = object({
      age                   = number
      created_before        = string
      with_state            = string
      matches_storage_class = list(string)
    })
  }))
  default = [
    {
      action = {
        type          = "SetStorageClass"
        storage_class = "NEARLINE"
      }
      condition = {
        age                   = 30
        created_before        = null
        with_state            = null
        matches_storage_class = ["STANDARD"]
      }
    },
    {
      action = {
        type          = "SetStorageClass"
        storage_class = "COLDLINE"
      }
      condition = {
        age                   = 90
        created_before        = null
        with_state            = null
        matches_storage_class = ["NEARLINE"]
      }
    }
  ]
}