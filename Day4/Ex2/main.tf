terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Create a new storage bucket with lifecycle rules and security settings
resource "google_storage_bucket" "data_bucket" {
  name          = "${var.project_name}-${var.environment}-bucket"
  location      = var.bucket_location
  storage_class = var.storage_class
  force_destroy = true

  # Enable versioning
  versioning {
    enabled = true
  }

  # Enable uniform bucket-level access
  uniform_bucket_level_access = true

  # Public access prevention
  public_access_prevention = "enforced"

  # Object lifecycle management
  dynamic "lifecycle_rule" {
    for_each = var.lifecycle_rules
    content {
      action {
        type          = lifecycle_rule.value.action.type
        storage_class = lifecycle_rule.value.action.storage_class
      }
      condition {
        age                   = lifecycle_rule.value.condition.age
        created_before        = lifecycle_rule.value.condition.created_before
        with_state            = lifecycle_rule.value.condition.with_state
        matches_storage_class = lifecycle_rule.value.condition.matches_storage_class
      }
    }
  }

  # CORS configuration
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

# Create a service account for bucket access
resource "google_service_account" "bucket_service_account" {
  account_id   = "${var.project_name}-${var.environment}-sa"
  display_name = "Service Account for ${var.project_name} bucket access"
}

# Create custom role for bucket access
resource "google_project_iam_custom_role" "bucket_custom_role" {
  role_id     = "${var.project_name}_${var.environment}_bucket_role"
  title       = "${var.project_name} ${var.environment} Bucket Role"
  description = "Custom role for bucket access with specific permissions"
  permissions = [
    "storage.buckets.get",
    "storage.buckets.getIamPolicy",
    "storage.buckets.setIamPolicy",
    "storage.objects.create",
    "storage.objects.delete",
    "storage.objects.get",
    "storage.objects.list",
    "storage.objects.update"
  ]
}

# Create a key for the service account
resource "google_service_account_key" "bucket_key" {
  service_account_id = google_service_account.bucket_service_account.name
  depends_on         = [google_service_account.bucket_service_account]
}

# Grant admin permissions to the user first
resource "google_storage_bucket_iam_member" "user_admin" {
  bucket     = google_storage_bucket.data_bucket.name
  role       = "roles/storage.admin"
  member     = "user:lehongvi19x@gmail.com"
  depends_on = [google_storage_bucket.data_bucket]
}

# Grant the custom role to the service account
resource "google_project_iam_member" "custom_role_binding" {
  project = var.project_id
  role    = "projects/${var.project_id}/roles/${google_project_iam_custom_role.bucket_custom_role.role_id}"
  member  = "serviceAccount:${google_service_account.bucket_service_account.email}"
  depends_on = [
    google_service_account.bucket_service_account,
    google_project_iam_custom_role.bucket_custom_role,
    google_storage_bucket_iam_member.user_admin
  ]
}

# Create bucket IAM bindings
resource "google_storage_bucket_iam_binding" "bucket_viewer" {
  bucket = google_storage_bucket.data_bucket.name
  role   = "roles/storage.objectViewer"
  members = [
    "serviceAccount:${google_service_account.bucket_service_account.email}",
    "user:lehongvi19x@gmail.com"
  ]
  depends_on = [
    google_storage_bucket.data_bucket,
    google_service_account.bucket_service_account,
    google_storage_bucket_iam_member.user_admin
  ]
}

resource "google_storage_bucket_iam_binding" "bucket_creator" {
  bucket = google_storage_bucket.data_bucket.name
  role   = "roles/storage.objectCreator"
  members = [
    "serviceAccount:${google_service_account.bucket_service_account.email}",
    "user:lehongvi19x@gmail.com"
  ]
  depends_on = [
    google_storage_bucket.data_bucket,
    google_service_account.bucket_service_account,
    google_storage_bucket_iam_member.user_admin,
    google_storage_bucket_iam_binding.bucket_viewer
  ]
}