terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "project-elevate-ai-503306"
  region  = "us-central1"
}

resource "random_id" "bucket_prefix" {
  byte_length = 4
}

resource "google_storage_bucket" "test_bucket" {
  name                        = "elevate-test-bucket-${random_id.bucket_prefix.hex}"
  location                    = "US"
  force_destroy               = true
  uniform_bucket_level_access = true
}

output "deployed_bucket_name" {
  value = google_storage_bucket.test_bucket.name
}
