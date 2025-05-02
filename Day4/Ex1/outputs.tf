output "vm_name" {
  description = "Name of the VM instance"
  value       = google_compute_instance.vm_instance.name
}

output "vm_external_ip" {
  description = "External IP of the VM instance"
  value       = google_compute_instance.vm_instance.network_interface[0].access_config[0].nat_ip
}

output "vm_internal_ip" {
  description = "Internal IP of the VM instance"
  value       = google_compute_instance.vm_instance.network_interface[0].network_ip
}

output "bucket_name" {
  description = "Name of the created storage bucket"
  value       = google_storage_bucket.raw_data.name
}

output "dataset_id" {
  description = "ID of the created BigQuery dataset"
  value       = google_bigquery_dataset.analytics.dataset_id
}

output "network_name" {
  description = "Name of the VPC network"
  value       = google_compute_network.vpc_network.name
}

output "subnet_name" {
  description = "Name of the subnet"
  value       = google_compute_subnetwork.subnet.name
}