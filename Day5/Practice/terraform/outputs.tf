output "vm_ip" {
  value = google_compute_instance.vm_instance.network_interface[0].access_config[0].nat_ip
}

output "bucket_name" {
  value = google_storage_bucket.etl_bucket.name
}