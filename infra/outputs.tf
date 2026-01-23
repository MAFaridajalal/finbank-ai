output "resource_group_name" {
  description = "The name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "acr_login_server" {
  description = "Azure Container Registry login server"
  value       = azurerm_container_registry.main.login_server
}

output "acr_admin_username" {
  description = "ACR admin username"
  value       = azurerm_container_registry.main.admin_username
}

output "acr_admin_password" {
  description = "ACR admin password"
  value       = azurerm_container_registry.main.admin_password
  sensitive   = true
}

output "sql_server_fqdn" {
  description = "SQL Server fully qualified domain name"
  value       = azurerm_mssql_server.main.fully_qualified_domain_name
}

output "sql_database_name" {
  description = "SQL Database name"
  value       = azurerm_mssql_database.main.name
}

output "sql_connection_string" {
  description = "SQL Database connection string"
  value       = "mssql+pyodbc://${var.sql_admin_username}:${var.sql_admin_password}@${azurerm_mssql_server.main.fully_qualified_domain_name}:1433/${azurerm_mssql_database.main.name}?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"
  sensitive   = true
}

output "aks_cluster_name" {
  description = "AKS cluster name"
  value       = azurerm_kubernetes_cluster.main.name
}

output "aks_cluster_fqdn" {
  description = "AKS cluster FQDN"
  value       = azurerm_kubernetes_cluster.main.fqdn
}

output "aks_kube_config" {
  description = "AKS kubeconfig"
  value       = azurerm_kubernetes_cluster.main.kube_config_raw
  sensitive   = true
}

output "key_vault_uri" {
  description = "Key Vault URI"
  value       = azurerm_key_vault.main.vault_uri
}

output "deployment_instructions" {
  description = "Next steps for deployment"
  value       = <<-EOT

    === Deployment Instructions ===

    1. Get AKS credentials:
       az aks get-credentials --resource-group ${azurerm_resource_group.main.name} --name ${azurerm_kubernetes_cluster.main.name}

    2. Login to ACR:
       az acr login --name ${azurerm_container_registry.main.name}

    3. Build and push images:
       docker build -t ${azurerm_container_registry.main.login_server}/finbank-backend:latest ./backend
       docker build -t ${azurerm_container_registry.main.login_server}/finbank-frontend:latest ./frontend
       docker build -t ${azurerm_container_registry.main.login_server}/finbank-mcp:latest ./mcp-server
       docker push ${azurerm_container_registry.main.login_server}/finbank-backend:latest
       docker push ${azurerm_container_registry.main.login_server}/finbank-frontend:latest
       docker push ${azurerm_container_registry.main.login_server}/finbank-mcp:latest

    4. Apply Kubernetes manifests:
       kubectl apply -f infra/k8s/

    5. Get the external IP:
       kubectl get svc finbank-frontend

  EOT
}
