terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Enable Required Cloud APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "firestore.googleapis.com",
    "secretmanager.googleapis.com",
    "aiplatform.googleapis.com",
    "artifactregistry.googleapis.com"
  ])
  service            = each.key
  disable_on_destroy = false
}

# 2. Service Account for Cloud Run
resource "google_service_account" "hr_agent_sa" {
  account_id   = "hr-agent-service-sa"
  display_name = "HR Agentic Service Account"
  depends_on   = [google_project_service.apis]
}

# 3. IAM Roles for Service Account
resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.hr_agent_sa.email}"
}

resource "google_project_iam_member" "firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.hr_agent_sa.email}"
}

resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.hr_agent_sa.email}"
}

# 4. Secret Manager for MCP Token
resource "google_secret_manager_secret" "mcp_token" {
  secret_id = "hr-agent-mcp-token"
  replication {
    auto {}
  }
  depends_on = [google_project_service.apis]
}

# 5. Cloud Firestore Native Database
resource "google_firestore_database" "database" {
  name                              = "(default)"
  location_id                       = var.firestore_location
  type                              = "FIRESTORE_NATIVE"
  concurrency_mode                  = "OPTIMISTIC"
  app_engine_integration_mode      = "DISABLED"
  point_in_time_recovery_enablement = "POINT_IN_TIME_RECOVERY_ENABLED"
  delete_protection_state           = "DELETE_PROTECTION_DISABLED"
  deletion_policy                   = "ABANDON"
  depends_on                        = [google_project_service.apis]
}

# 6. Cloud Run Service (Production Hardened, Authenticated Ingress)
resource "google_cloud_run_v2_service" "hr_agent_service" {
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.hr_agent_sa.email
    timeout         = "300s"

    containers {
      image = var.image_tag

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }

      env {
        name  = "APP_ENV"
        value = "production"
      }
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = "global"
      }
      env {
        name  = "GEMINI_MODEL"
        value = var.gemini_model
      }
      env {
        name  = "GOOGLE_GENAI_USE_VERTEXAI"
        value = "true"
      }
      env {
        name  = "FIRESTORE_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "FIRESTORE_DATABASE"
        value = "(default)"
      }
      env {
        name  = "MOCK_SAAS_URL"
        value = "https://mock-saas.aishprabhat.demo.altostrat.com"
      }

      env {
        name = "MCP_TOKEN"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.mcp_token.secret_id
            version = "latest"
          }
        }
      }
    }

    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }
  }

  depends_on = [
    google_project_service.apis,
    google_firestore_database.database
  ]
}
