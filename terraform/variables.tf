variable "project_id" {
  description = "The Google Cloud Project ID"
  type        = string
  default     = "genial-union-475913-i7"
}

variable "region" {
  description = "Google Cloud region for Cloud Run and resources"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Name of the Cloud Run service"
  type        = string
  default     = "hr-agentic-service"
}

variable "image_tag" {
  description = "Container image tag to deploy"
  type        = string
  default     = "us-central1-docker.pkg.dev/genial-union-475913-i7/hr-agentic-repo/hr-agentic-service:latest"
}

variable "gemini_model" {
  description = "Vertex AI Foundation Model identifier"
  type        = string
  default     = "gemini-3.5-flash"
}

variable "firestore_location" {
  description = "Location for Firestore Native database"
  type        = string
  default     = "nam5"
}
