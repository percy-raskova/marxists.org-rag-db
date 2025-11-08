# Terraform Infrastructure as Code Guide

## Overview

This document provides complete Terraform configurations for deploying the 200GB MIA RAG system infrastructure across GCP (primary), AWS, and Azure. The infrastructure is modular, environment-aware, and optimized for parallel development with 6+ Claude instances.

## Directory Structure

```
terraform/
├── README.md                      # Getting started guide
├── Makefile                       # Common commands
├── .terraform-version             # Terraform version lock
├── backend.tf                     # State backend configuration
├── variables.tf                   # Global variables
├── versions.tf                    # Provider versions
│
├── modules/                       # Reusable modules
│   ├── storage/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── compute/
│   ├── weaviate/
│   ├── networking/
│   ├── monitoring/
│   └── security/
│
├── environments/                  # Environment-specific configs
│   ├── dev/
│   │   ├── main.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   └── prod/
│
└── providers/                     # Cloud-specific implementations
    ├── gcp/
    ├── aws/
    └── azure/
```

## Quick Start

```bash
# Install Terraform
brew install terraform  # macOS
# or
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-get update && sudo apt-get install terraform

# Initialize backend
cd terraform/environments/dev
terraform init

# Plan changes
terraform plan -out=tfplan

# Apply infrastructure
terraform apply tfplan

# Destroy (when needed)
terraform destroy
```

## Module Specifications

### 1. Storage Module

**Purpose**: Manages all storage buckets with appropriate lifecycle policies

```hcl
# modules/storage/main.tf

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Raw torrent storage (Archive tier)
resource "google_storage_bucket" "raw_torrent" {
  name          = "${var.project_id}-raw-torrent-${var.environment}"
  location      = var.region
  storage_class = "ARCHIVE"

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 2555 # 7 years retention
    }
  }

  versioning {
    enabled = false # No need for versioning on raw data
  }

  labels = {
    environment = var.environment
    purpose     = "raw-torrent"
    managed_by  = "terraform"
  }
}

# Processed markdown storage (Standard → Nearline)
resource "google_storage_bucket" "processed_markdown" {
  name          = "${var.project_id}-markdown-${var.environment}"
  location      = var.region
  storage_class = "STANDARD"

  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
    condition {
      age = 30
    }
  }

  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "ARCHIVE"
    }
    condition {
      age = 365
    }
  }

  versioning {
    enabled = true # Keep versions for processed data
  }

  labels = {
    environment = var.environment
    purpose     = "processed-markdown"
    managed_by  = "terraform"
  }
}

# Embeddings storage (Standard)
resource "google_storage_bucket" "embeddings" {
  name          = "${var.project_id}-embeddings-${var.environment}"
  location      = var.region
  storage_class = "STANDARD"

  versioning {
    enabled = true
  }

  # Retention policy to prevent accidental deletion
  retention_policy {
    retention_period = 604800 # 7 days in seconds
  }

  labels = {
    environment = var.environment
    purpose     = "embeddings"
    managed_by  = "terraform"
  }
}

# Backup storage (Nearline)
resource "google_storage_bucket" "backups" {
  name          = "${var.project_id}-backups-${var.environment}"
  location      = var.region
  storage_class = "NEARLINE"

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 90 # Keep backups for 90 days
    }
  }

  versioning {
    enabled = true
  }

  labels = {
    environment = var.environment
    purpose     = "backups"
    managed_by  = "terraform"
  }
}

# Per-developer isolated buckets
resource "google_storage_bucket" "dev_instances" {
  for_each = toset(var.dev_instances)

  name          = "${var.project_id}-dev-${each.key}-${var.environment}"
  location      = var.region
  storage_class = "STANDARD"

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30 # Auto-cleanup dev data after 30 days
    }
  }

  labels = {
    environment = var.environment
    purpose     = "development"
    instance    = each.key
    managed_by  = "terraform"
  }
}

# modules/storage/variables.tf
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (dev/staging/prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "dev_instances" {
  description = "List of developer instance names"
  type        = list(string)
  default     = ["instance1", "instance2", "instance3", "instance4", "instance5", "instance6"]
}

# modules/storage/outputs.tf
output "raw_torrent_bucket" {
  value = google_storage_bucket.raw_torrent.name
}

output "markdown_bucket" {
  value = google_storage_bucket.processed_markdown.name
}

output "embeddings_bucket" {
  value = google_storage_bucket.embeddings.name
}

output "dev_instance_buckets" {
  value = {
    for k, v in google_storage_bucket.dev_instances : k => v.name
  }
}
```

### 2. Weaviate Module

**Purpose**: Deploys Weaviate vector database on GKE

```hcl
# modules/weaviate/main.tf

# GKE Cluster for Weaviate
resource "google_container_cluster" "weaviate" {
  name     = "weaviate-${var.environment}"
  location = var.zone

  # Minimal initial node pool
  initial_node_count       = 1
  remove_default_node_pool = true

  # Network configuration
  network    = var.vpc_id
  subnetwork = var.subnet_id

  # Security
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "10.10.0.0/28"
  }

  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Resource labels
  resource_labels = {
    environment = var.environment
    purpose     = "weaviate"
    managed_by  = "terraform"
  }
}

# Node pool for Weaviate
resource "google_container_node_pool" "weaviate_nodes" {
  name       = "weaviate-pool-${var.environment}"
  cluster    = google_container_cluster.weaviate.id
  node_count = var.environment == "prod" ? 3 : 1

  node_config {
    preemptible  = var.environment != "prod"
    machine_type = var.machine_type

    disk_size_gb = 100
    disk_type    = "pd-ssd"

    # Service account for nodes
    service_account = google_service_account.weaviate_nodes.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = {
      environment = var.environment
      purpose     = "weaviate"
    }

    tags = ["weaviate-node"]

    # Workload Identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }

  autoscaling {
    min_node_count = var.environment == "prod" ? 3 : 1
    max_node_count = var.environment == "prod" ? 10 : 3
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# Service account for Weaviate nodes
resource "google_service_account" "weaviate_nodes" {
  account_id   = "weaviate-nodes-${var.environment}"
  display_name = "Weaviate Nodes Service Account"
}

# IAM binding for storage access
resource "google_storage_bucket_iam_member" "weaviate_embeddings_reader" {
  bucket = var.embeddings_bucket
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.weaviate_nodes.email}"
}

# Kubernetes namespace for Weaviate
resource "kubernetes_namespace" "weaviate" {
  metadata {
    name = "weaviate-${var.environment}"

    labels = {
      environment = var.environment
      purpose     = "weaviate"
    }
  }

  depends_on = [google_container_cluster.weaviate]
}

# Weaviate Helm deployment
resource "helm_release" "weaviate" {
  name       = "weaviate"
  namespace  = kubernetes_namespace.weaviate.metadata[0].name
  repository = "https://weaviate.github.io/weaviate-helm"
  chart      = "weaviate"
  version    = "16.8.0"

  values = [
    templatefile("${path.module}/weaviate-values.yaml", {
      environment    = var.environment
      replicas       = var.environment == "prod" ? 3 : 1
      storage_class  = "pd-ssd"
      storage_size   = "100Gi"
      cpu_request    = var.environment == "prod" ? "2" : "1"
      memory_request = var.environment == "prod" ? "8Gi" : "4Gi"
    })
  ]

  depends_on = [
    google_container_node_pool.weaviate_nodes,
    kubernetes_namespace.weaviate
  ]
}

# modules/weaviate/weaviate-values.yaml
replicas: ${replicas}

resources:
  requests:
    cpu: ${cpu_request}
    memory: ${memory_request}
  limits:
    cpu: "4"
    memory: "16Gi"

persistence:
  enabled: true
  storageClass: ${storage_class}
  size: ${storage_size}

authentication:
  anonymous_access:
    enabled: ${environment == "dev" ? true : false}
  apikey:
    enabled: ${environment != "dev" ? true : false}

monitoring:
  enabled: true
  prometheus:
    enabled: true
    port: 2112

backup:
  enabled: true
  schedule: "0 */6 * * *"  # Every 6 hours
  retention: 7  # Keep 7 days of backups
```

### 3. Networking Module

**Purpose**: Sets up VPC, subnets, and security configurations

```hcl
# modules/networking/main.tf

# VPC Network
resource "google_compute_network" "main" {
  name                    = "mia-rag-vpc-${var.environment}"
  auto_create_subnetworks = false
  mtu                     = 1460

  description = "VPC for MIA RAG ${var.environment} environment"
}

# Subnets
resource "google_compute_subnetwork" "processing" {
  name          = "processing-subnet-${var.environment}"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.main.id

  private_ip_google_access = true

  log_config {
    aggregation_interval = "INTERVAL_10_MIN"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

resource "google_compute_subnetwork" "weaviate" {
  name          = "weaviate-subnet-${var.environment}"
  ip_cidr_range = "10.0.2.0/24"
  region        = var.region
  network       = google_compute_network.main.id

  private_ip_google_access = true

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.4.0.0/14"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.8.0.0/20"
  }
}

resource "google_compute_subnetwork" "api" {
  name          = "api-subnet-${var.environment}"
  ip_cidr_range = "10.0.3.0/24"
  region        = var.region
  network       = google_compute_network.main.id

  private_ip_google_access = true
}

# Cloud NAT for outbound internet
resource "google_compute_router" "main" {
  name    = "mia-rag-router-${var.environment}"
  network = google_compute_network.main.id
  region  = var.region

  bgp {
    asn = 64514
  }
}

resource "google_compute_router_nat" "main" {
  name                               = "mia-rag-nat-${var.environment}"
  router                             = google_compute_router.main.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Firewall Rules
resource "google_compute_firewall" "allow_internal" {
  name    = "allow-internal-${var.environment}"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = ["10.0.0.0/16"]
  priority      = 1000
}

resource "google_compute_firewall" "allow_health_checks" {
  name    = "allow-health-checks-${var.environment}"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
  }

  source_ranges = ["35.191.0.0/16", "130.211.0.0/22"]
  target_tags   = ["health-check"]
  priority      = 1000
}

# Cloud Armor security policy
resource "google_compute_security_policy" "api_protection" {
  name        = "api-protection-${var.environment}"
  description = "API DDoS and security protection"

  rule {
    action   = "rate_based_ban"
    priority = 100

    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }

    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"

      rate_limit_threshold {
        count        = 100
        interval_sec = 60
      }

      ban_duration_sec = 600
    }
  }

  rule {
    action   = "deny(403)"
    priority = 200

    match {
      expr {
        expression = "origin.region_code == 'CN' || origin.region_code == 'RU'"
      }
    }

    description = "Block specific countries if needed"
  }

  rule {
    action   = "allow"
    priority = 2147483647

    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }

    description = "Default allow rule"
  }
}
```

### 4. Monitoring Module

**Purpose**: Sets up comprehensive monitoring and alerting

```hcl
# modules/monitoring/main.tf

# Monitoring workspace
resource "google_monitoring_workspace" "main" {
  provider = google-beta
  project  = var.project_id
}

# Create custom dashboards
resource "google_monitoring_dashboard" "operational" {
  dashboard_json = templatefile("${path.module}/dashboards/operational.json", {
    project_id  = var.project_id
    environment = var.environment
  })
}

resource "google_monitoring_dashboard" "cost" {
  dashboard_json = templatefile("${path.module}/dashboards/cost.json", {
    project_id  = var.project_id
    environment = var.environment
  })
}

# Notification channels
resource "google_monitoring_notification_channel" "email" {
  for_each = toset(var.alert_emails)

  display_name = "Email - ${each.value}"
  type         = "email"

  labels = {
    email_address = each.value
  }
}

resource "google_monitoring_notification_channel" "slack" {
  count = var.slack_webhook != "" ? 1 : 0

  display_name = "Slack - ${var.environment}"
  type         = "slack"

  labels = {
    url = var.slack_webhook
  }

  sensitive_labels {
    auth_token = var.slack_token
  }
}

# Alert policies
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "High Error Rate - ${var.environment}"
  combiner     = "OR"

  conditions {
    display_name = "API Error Rate > 5%"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"

        cross_series_reducer = "REDUCE_SUM"
        group_by_fields      = ["resource.service_name"]
      }
    }
  }

  notification_channels = [
    for nc in google_monitoring_notification_channel.email : nc.id
  ]

  alert_strategy {
    auto_close = "1800s"
  }
}

resource "google_monitoring_alert_policy" "weaviate_down" {
  display_name = "Weaviate Cluster Down - ${var.environment}"
  combiner     = "OR"

  conditions {
    display_name = "Weaviate pods < minimum"

    condition_threshold {
      filter          = "resource.type=\"k8s_cluster\" AND metric.type=\"kubernetes.io/pod/volume/available_bytes\""
      duration        = "180s"
      comparison      = "COMPARISON_LT"
      threshold_value = var.environment == "prod" ? 3 : 1

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MIN"
      }
    }
  }

  notification_channels = concat(
    [for nc in google_monitoring_notification_channel.email : nc.id],
    var.slack_webhook != "" ? [google_monitoring_notification_channel.slack[0].id] : []
  )

  alert_strategy {
    auto_close = "3600s"

    notification_rate_limit {
      period = "300s"
    }
  }

  documentation {
    content   = "Weaviate cluster has fewer than minimum required pods. Check GKE cluster health and pod logs."
    mime_type = "text/markdown"
  }
}

# Uptime checks
resource "google_monitoring_uptime_check_config" "api_health" {
  display_name = "API Health Check - ${var.environment}"
  timeout      = "10s"
  period       = "60s"

  http_check {
    path           = "/health"
    port           = 443
    use_ssl        = true
    validate_ssl   = true
    request_method = "GET"
  }

  monitored_resource {
    type = "uptime_url"

    labels = {
      project_id = var.project_id
      host       = var.api_endpoint
    }
  }
}

# Budget alerts
resource "google_billing_budget" "monthly" {
  billing_account = var.billing_account
  display_name    = "Monthly Budget - ${var.environment}"

  amount {
    specified_amount {
      currency_code = "USD"
      units         = var.monthly_budget
    }
  }

  threshold_rules {
    threshold_percent = 0.5
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 0.8
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 1.0
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 1.2
    spend_basis       = "FORECASTED_SPEND"
  }

  all_updates_rule {
    monitoring_notification_channels = [
      for nc in google_monitoring_notification_channel.email : nc.id
    ]
  }
}

# Logging
resource "google_logging_project_sink" "bigquery" {
  name        = "bigquery-sink-${var.environment}"
  destination = "bigquery.googleapis.com/projects/${var.project_id}/datasets/${google_bigquery_dataset.logs.dataset_id}"

  filter = <<-EOT
    resource.type="cloud_run_revision" OR
    resource.type="k8s_cluster" OR
    resource.type="gcs_bucket"
  EOT

  unique_writer_identity = true
}

resource "google_bigquery_dataset" "logs" {
  dataset_id  = "logs_${var.environment}"
  description = "Logs for ${var.environment} environment"
  location    = var.region

  default_table_expiration_ms = 2592000000 # 30 days

  labels = {
    environment = var.environment
    purpose     = "logging"
  }
}
```

### 5. Main Environment Configuration

**Purpose**: Ties all modules together for each environment

```hcl
# environments/dev/main.tf

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.10"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }

  backend "gcs" {
    bucket = "mia-rag-terraform-state"
    prefix = "dev"
  }
}

locals {
  environment = "dev"
  project_id  = "mia-rag-dev"
  region      = "us-central1"
  zone        = "us-central1-a"

  dev_instances = [
    "storage",     # Instance 1
    "embeddings",  # Instance 2
    "weaviate",    # Instance 3
    "api",         # Instance 4
    "mcp",         # Instance 5
    "monitoring"   # Instance 6
  ]
}

# Provider configuration
provider "google" {
  project = local.project_id
  region  = local.region
}

provider "kubernetes" {
  host  = "https://${module.weaviate.cluster_endpoint}"
  token = data.google_client_config.current.access_token

  cluster_ca_certificate = base64decode(
    module.weaviate.cluster_ca_certificate
  )
}

provider "helm" {
  kubernetes {
    host  = "https://${module.weaviate.cluster_endpoint}"
    token = data.google_client_config.current.access_token

    cluster_ca_certificate = base64decode(
      module.weaviate.cluster_ca_certificate
    )
  }
}

data "google_client_config" "current" {}

# Networking
module "networking" {
  source = "../../modules/networking"

  project_id  = local.project_id
  region      = local.region
  environment = local.environment
}

# Storage
module "storage" {
  source = "../../modules/storage"

  project_id    = local.project_id
  region        = local.region
  environment   = local.environment
  dev_instances = local.dev_instances
}

# Weaviate
module "weaviate" {
  source = "../../modules/weaviate"

  project_id         = local.project_id
  zone               = local.zone
  environment        = local.environment
  vpc_id             = module.networking.vpc_id
  subnet_id          = module.networking.weaviate_subnet_id
  embeddings_bucket  = module.storage.embeddings_bucket
  machine_type       = "n1-standard-4"
}

# Monitoring
module "monitoring" {
  source = "../../modules/monitoring"

  project_id       = local.project_id
  environment      = local.environment
  alert_emails     = ["alerts@example.com"]
  slack_webhook    = var.slack_webhook
  slack_token      = var.slack_token
  api_endpoint     = module.api.endpoint
  billing_account  = var.billing_account
  monthly_budget   = 100
}

# API Services (simplified for dev)
module "api" {
  source = "../../modules/api"

  project_id    = local.project_id
  region        = local.region
  environment   = local.environment
  vpc_id        = module.networking.vpc_id
  subnet_id     = module.networking.api_subnet_id
  weaviate_host = module.weaviate.internal_endpoint
}

# Output important values
output "storage_buckets" {
  value = {
    raw_torrent = module.storage.raw_torrent_bucket
    markdown    = module.storage.markdown_bucket
    embeddings  = module.storage.embeddings_bucket
    dev_buckets = module.storage.dev_instance_buckets
  }
}

output "weaviate" {
  value = {
    cluster_endpoint  = module.weaviate.cluster_endpoint
    internal_endpoint = module.weaviate.internal_endpoint
  }
}

output "api" {
  value = {
    endpoint = module.api.endpoint
  }
}

# environments/dev/terraform.tfvars
billing_account = "01234-56789-ABCDEF"
slack_webhook   = ""  # Optional
slack_token     = ""  # Optional

# environments/dev/variables.tf
variable "billing_account" {
  description = "GCP Billing Account ID"
  type        = string
}

variable "slack_webhook" {
  description = "Slack webhook URL for alerts"
  type        = string
  default     = ""
}

variable "slack_token" {
  description = "Slack token for alerts"
  type        = string
  sensitive   = true
  default     = ""
}
```

## State Management

### Backend Configuration

```hcl
# backend.tf (root level)

terraform {
  backend "gcs" {
    bucket = "mia-rag-terraform-state"
    prefix = "terraform/state"
  }
}

# Create state bucket (run once manually)
resource "google_storage_bucket" "terraform_state" {
  name          = "mia-rag-terraform-state"
  location      = "us-central1"
  storage_class = "STANDARD"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      num_newer_versions = 10
    }
  }

  labels = {
    purpose    = "terraform-state"
    managed_by = "terraform"
  }
}
```

### Workspace Management

```bash
# Create workspaces for parallel development
terraform workspace new dev-storage
terraform workspace new dev-embeddings
terraform workspace new dev-weaviate
terraform workspace new dev-api
terraform workspace new dev-mcp
terraform workspace new dev-monitoring

# Select workspace
terraform workspace select dev-storage

# List workspaces
terraform workspace list
```

## Secrets Management

### Using Google Secret Manager

```hcl
# modules/security/secrets.tf

resource "google_secret_manager_secret" "api_key" {
  secret_id = "mia-rag-api-key-${var.environment}"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "api_key" {
  secret      = google_secret_manager_secret.api_key.id
  secret_data = var.api_key
}

# Grant access to service account
resource "google_secret_manager_secret_iam_member" "api_key_reader" {
  secret_id = google_secret_manager_secret.api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.api.email}"
}

# Access in application
data "google_secret_manager_secret_version" "api_key" {
  secret = google_secret_manager_secret.api_key.id
}
```

### Environment Variables

```bash
# .env.example
export TF_VAR_project_id="mia-rag-dev"
export TF_VAR_billing_account="01234-56789-ABCDEF"
export TF_VAR_api_key="your-api-key"
export TF_VAR_slack_webhook="https://hooks.slack.com/..."
```

## Cost Controls

### Budget Limits

```hcl
# modules/cost-control/main.tf

resource "google_project_service" "budget_api" {
  project = var.project_id
  service = "billingbudgets.googleapis.com"
}

resource "google_billing_budget" "project_budget" {
  billing_account = var.billing_account
  display_name    = "Project Budget - ${var.environment}"

  budget_filter {
    projects = ["projects/${var.project_id}"]
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = var.environment == "prod" ? "200" : "50"
    }
  }

  threshold_rules {
    threshold_percent = 0.5
  }

  threshold_rules {
    threshold_percent = 0.8
  }

  threshold_rules {
    threshold_percent = 1.0
  }

  all_updates_rule {
    monitoring_notification_channels = var.notification_channels
    disable_default_iam_recipients   = false
  }
}

# Quota limits
resource "google_project_service" "quota_api" {
  project = var.project_id
  service = "serviceusage.googleapis.com"
}

resource "null_resource" "set_quotas" {
  provisioner "local-exec" {
    command = <<-EOT
      gcloud compute project-info add-metadata \
        --metadata google-compute-default-region=${var.region},google-compute-default-zone=${var.zone} \
        --project ${var.project_id}

      # Set CPU quota for dev
      %{if var.environment == "dev"}
      gcloud compute project-info update \
        --project ${var.project_id} \
        --add-quotas=CPUS=50
      %{endif}
    EOT
  }
}
```

## Deployment Automation

### Makefile

```makefile
# Makefile

.PHONY: help init plan apply destroy

ENVIRONMENT ?= dev

help:
 @echo "Available targets:"
 @echo "  init       - Initialize Terraform"
 @echo "  plan       - Create execution plan"
 @echo "  apply      - Apply infrastructure changes"
 @echo "  destroy    - Destroy infrastructure"
 @echo "  fmt        - Format Terraform files"
 @echo "  validate   - Validate configuration"

init:
 @cd environments/$(ENVIRONMENT) && terraform init -upgrade

plan:
 @cd environments/$(ENVIRONMENT) && terraform plan -out=tfplan

apply:
 @cd environments/$(ENVIRONMENT) && terraform apply tfplan

destroy:
 @cd environments/$(ENVIRONMENT) && terraform destroy

fmt:
 @terraform fmt -recursive .

validate:
 @cd environments/$(ENVIRONMENT) && terraform validate

cost:
 @cd environments/$(ENVIRONMENT) && infracost breakdown --path .

security:
 @tfsec . --format json | jq

clean:
 @find . -type f -name "*.tfplan" -delete
 @find . -type d -name ".terraform" -exec rm -rf {} +
```

### CI/CD Pipeline

```yaml
# .github/workflows/terraform.yml

name: Terraform CI/CD

on:
  push:
    branches: [main]
    paths:
      - 'terraform/**'
  pull_request:
    branches: [main]
    paths:
      - 'terraform/**'

env:
  TF_VERSION: '1.5.7'
  TF_VAR_project_id: ${{ secrets.GCP_PROJECT_ID }}

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform Format Check
        run: terraform fmt -check -recursive

      - name: Terraform Init
        run: |
          cd terraform/environments/dev
          terraform init -backend=false

      - name: Terraform Validate
        run: |
          cd terraform/environments/dev
          terraform validate

      - name: TFSec Security Scan
        uses: aquasecurity/tfsec-action@v1.0.0
        with:
          working_directory: terraform

  plan:
    needs: validate
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'

    steps:
      - uses: actions/checkout@v3

      - uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform Plan
        run: |
          cd terraform/environments/dev
          terraform init
          terraform plan -no-color

  apply:
    needs: validate
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    steps:
      - uses: actions/checkout@v3

      - uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform Apply
        run: |
          cd terraform/environments/dev
          terraform init
          terraform apply -auto-approve
```

## AWS Alternative

### Core Differences

```hcl
# providers/aws/storage/main.tf

resource "aws_s3_bucket" "raw_torrent" {
  bucket = "${var.project_id}-raw-torrent-${var.environment}"

  lifecycle_rule {
    enabled = true

    transition {
      days          = 0
      storage_class = "DEEP_ARCHIVE"
    }

    expiration {
      days = 2555
    }
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  tags = {
    Environment = var.environment
    Purpose     = "raw-torrent"
    ManagedBy   = "terraform"
  }
}

# EKS for Weaviate
resource "aws_eks_cluster" "weaviate" {
  name     = "weaviate-${var.environment}"
  role_arn = aws_iam_role.eks_cluster.arn

  vpc_config {
    subnet_ids = var.private_subnet_ids
  }
}
```

## Azure Alternative

### Core Differences

```hcl
# providers/azure/storage/main.tf

resource "azurerm_storage_account" "main" {
  name                     = "miarag${var.environment}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  blob_properties {
    versioning_enabled = true
  }
}

resource "azurerm_storage_container" "raw_torrent" {
  name                  = "raw-torrent"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# AKS for Weaviate
resource "azurerm_kubernetes_cluster" "weaviate" {
  name                = "weaviate-${var.environment}"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "weaviate"

  default_node_pool {
    name       = "default"
    node_count = var.environment == "prod" ? 3 : 1
    vm_size    = "Standard_D4_v3"
  }

  identity {
    type = "SystemAssigned"
  }
}
```

## Troubleshooting

### Common Issues

```bash
# Issue: State lock
terraform force-unlock <lock-id>

# Issue: Provider credentials
gcloud auth application-default login

# Issue: Quota exceeded
gcloud compute project-info describe --project PROJECT_ID

# Issue: API not enabled
gcloud services enable storage.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com

# Issue: Terraform drift
terraform refresh
terraform plan -refresh-only

# Issue: Module changes not detected
terraform init -upgrade
```

## Best Practices

1. **Always use workspaces** for environment separation
2. **Never commit .tfvars** with sensitive data
3. **Use remote state** with locking
4. **Pin provider versions** for consistency
5. **Run fmt and validate** before commits
6. **Use cost estimation** before applying
7. **Tag all resources** for cost tracking
8. **Implement budget alerts** early
9. **Use preemptible instances** for dev
10. **Document all manual steps** if any

---

This Terraform infrastructure provides a complete, production-ready deployment framework with proper state management, security, and cost controls.
