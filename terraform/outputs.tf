output "cloud_run_url" {
  description = "The URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.hr_agent_service.uri
}

output "service_account_email" {
  description = "Service account email running the agent"
  value       = google_service_account.hr_agent_sa.email
}

output "firestore_database_name" {
  description = "Firestore Native database name"
  value       = google_firestore_database.database.name
}

output "secret_manager_mcp_token" {
  description = "Secret Manager secret ID for MCP token"
  value       = google_secret_manager_secret.mcp_token.secret_id
}
