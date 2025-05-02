output "bucket_name" {
  description = "The name of the bucket"
  value       = google_storage_bucket.data_bucket.name
}

output "bucket_url" {
  description = "The URL of the bucket"
  value       = google_storage_bucket.data_bucket.url
}

output "service_account_email" {
  description = "The email of the service account"
  value       = google_service_account.bucket_service_account.email
}

output "service_account_key" {
  description = "The service account key (base64 encoded)"
  value       = google_service_account_key.bucket_key.private_key
  sensitive   = true
} 