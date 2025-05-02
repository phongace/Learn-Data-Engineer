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

# Tạo Cloud Storage bucket cho data lake
resource "google_storage_bucket" "raw_data" {
  name          = "${var.project_id}-raw-data"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 90 # Chuyển data sau 90 ngày
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
}

# Tạo BigQuery Dataset
resource "google_bigquery_dataset" "analytics" {
  dataset_id  = "analytics_raw"
  description = "Dataset for raw data analysis"
  location    = var.region

  default_table_expiration_ms = 7776000000 # 90 days

  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }

  access {
    role          = "READER"
    special_group = "projectReaders"
  }
}

# Tạo VPC Network
resource "google_compute_network" "vpc_network" {
  name                    = "data-processing-vpc"
  auto_create_subnetworks = false
}

# Tạo Subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "data-processing-subnet"
  ip_cidr_range = "10.0.0.0/24"
  network       = google_compute_network.vpc_network.id
  region        = var.region
}

# Tạo Compute Engine Instance
resource "google_compute_instance" "vm_instance" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network    = google_compute_network.vpc_network.name
    subnetwork = google_compute_subnetwork.subnet.name

    access_config {
      # Ephemeral public IP
    }
  }

  tags = var.instance_tags

  metadata = {
    ssh-keys = "debian:${file("~/.ssh/id_rsa.pub")}"
  }

  metadata_startup_script = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y python3-pip
              EOF
}