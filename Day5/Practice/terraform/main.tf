provider "google" {
  credentials = file("../config/cgp-service-account-key.json")
  project     = var.project
  region      = var.region
}

resource "google_compute_instance" "vm_instance" {
  name         = "etl-vm"
  machine_type = "e2-micro"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }
}

resource "google_storage_bucket" "etl_bucket" {
  name     = var.bucket_name
  location = var.region
}