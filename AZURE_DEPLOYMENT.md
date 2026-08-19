# Azure deployment

Recommended production setup:

- Azure SQL Database for data
- Azure Container Registry (ACR) for the API image
- Azure App Service for Linux to run the container
- Azure Key Vault for database credentials
- Managed identity from App Service to Key Vault

Azure App Service supports Flask, FastAPI, and Django applications, including REST APIs. This project uses the GitHub continuous deployment option: every push to `main` triggers GitHub Actions, which builds the container and deploys the latest commit to App Service.

## 1. Create Azure resources

Run these commands in Azure Cloud Shell or PowerShell. Replace the names and choose a region.

```powershell
$group = "pushpthreads-rg"
$location = "centralindia"
$acr = "pushpthreadsacr"
$app = "pushpthreads-api"
$appPlan = "pushpthreads-plan"
$keyVault = "pushpthreads-kv"
$sqlServer = "pushpthread"
$sqlDatabase = "PushpThread"

az group create --name $group --location $location
az acr create --resource-group $group --name $acr --sku Basic
az appservice plan create --resource-group $group --name $appPlan --is-linux --sku B1
az webapp create --resource-group $group --plan $appPlan --name $app --runtime "PYTHON:3.12"
az keyvault create --resource-group $group --name $keyVault --location $location
```

Create Azure SQL separately if it does not exist. The SQL server firewall must allow the App Service outbound IPs, or use private endpoints/VNet integration for production.

## 2. Build and push the API image

From the repository root:

```powershell
az acr build --registry $acr --image "pushpthreads-api:1.0.0" .

az webapp config container set \
  --resource-group $group \
  --name $app \
  --docker-custom-image-name "$acr.azurecr.io/pushpthreads-api:1.0.0" \
  --docker-registry-server-url "https://$acr.azurecr.io"

az webapp config appsettings set --resource-group $group --name $app --settings WEBSITES_PORT=8000
```

Configure ACR authentication with a managed identity rather than storing an ACR admin password when moving beyond a first deployment.

## 3. Store database credentials in Key Vault

Do not commit `.env` or put the password in source control. Store each setting as a Key Vault secret. Key Vault secret names use hyphens, so the API setting `DB_PASSWORD` becomes `Db--Password` in an App Service Key Vault reference.

```powershell
az keyvault secret set --vault-name $keyVault --name Db--Server --value "pushpthread.database.windows.net"
az keyvault secret set --vault-name $keyVault --name Db--Name --value "PushpThread"
az keyvault secret set --vault-name $keyVault --name Db--Driver --value "ODBC Driver 18 for SQL Server"
az keyvault secret set --vault-name $keyVault --name Db--Encrypt --value "true"
az keyvault secret set --vault-name $keyVault --name Db--Trust--Server--Certificate --value "false"
az keyvault secret set --vault-name $keyVault --name Db--Trusted--Connection --value "false"
az keyvault secret set --vault-name $keyVault --name Db--User --value "<sql-login>"
az keyvault secret set --vault-name $keyVault --name Db--Password --value "<sql-password>"
```

Use a user-assigned or system-assigned managed identity for App Service, grant it Key Vault secret read access, and configure App Service application settings with Key Vault references:

```powershell
az webapp identity assign --resource-group $group --name $app
# Grant the returned principal access to Key Vault secrets using Azure RBAC or an access policy.
az webapp config appsettings set --resource-group $group --name $app --settings `
  APP_NAME=PushpThreadsAPI `
  API_PREFIX=/api/v1 `
  DB_PORT=1433 `
  DB_SERVER="@Microsoft.KeyVault(VaultName=$keyVault;SecretName=Db--Server)" `
  DB_NAME="@Microsoft.KeyVault(VaultName=$keyVault;SecretName=Db--Name)" `
  DB_DRIVER="@Microsoft.KeyVault(VaultName=$keyVault;SecretName=Db--Driver)" `
  DB_ENCRYPT="@Microsoft.KeyVault(VaultName=$keyVault;SecretName=Db--Encrypt)" `
  DB_TRUST_SERVER_CERTIFICATE="@Microsoft.KeyVault(VaultName=$keyVault;SecretName=Db--Trust--Server--Certificate)" `
  DB_TRUSTED_CONNECTION="@Microsoft.KeyVault(VaultName=$keyVault;SecretName=Db--Trusted--Connection)" `
  DB_USER="@Microsoft.KeyVault(VaultName=$keyVault;SecretName=Db--User)" `
  DB_PASSWORD="@Microsoft.KeyVault(VaultName=$keyVault;SecretName=Db--Password)"
```

The application code already reads these values as environment variables. Restart App Service after changing settings.

## 4. Create the database schema

Run [database/schema.sql](database/schema.sql) once against the target Azure SQL database. For an existing database, run [database/migration_customer_order.sql](database/migration_customer_order.sql). Do this through Azure Query Editor, SSMS, or `sqlcmd`.

## 5. Verify deployment

```powershell
curl "https://$app.azurewebsites.net/health"
```

Then open `https://$app.azurewebsites.net/docs` for Swagger UI.

## 6. Deploy automatically through GitHub

This repository includes [`.github/workflows/azure-deploy.yml`](.github/workflows/azure-deploy.yml). It deploys automatically whenever code is pushed to `main`.

The deployment flow is:

```text
GitHub push to main -> GitHub Actions -> Azure Container Registry -> Azure App Service
```

You can also connect the GitHub repository from **Azure Portal -> App Service -> Deployment Center -> Source: GitHub**. For this project, keep the included workflow because it installs the required SQL Server ODBC driver through the Dockerfile and gives each deployment an immutable commit-based image tag.

Create an Azure service principal for GitHub Actions:

```powershell
$subscription = az account show --query id --output tsv
az ad sp create-for-rbac `
  --name "pushpthreads-github-actions" `
  --role contributor `
  --scopes "/subscriptions/$subscription/resourceGroups/$group" `
  --sdk-auth
```

Copy the complete JSON output and add it to the GitHub repository at **Settings -> Secrets and variables -> Actions -> New repository secret**:

```text
Name: AZURE_CREDENTIALS
Value: <the complete JSON output>
```

The workflow expects the Azure resource names in its `env` section to match your resources. Update `RESOURCE_GROUP`, `ACR_NAME`, and `APP_NAME` there if necessary. Then push to GitHub:

```powershell
git add .
git commit -m "Deploy API to Azure"
git push origin main
```

Monitor the deployment under the repository's **Actions** tab. The workflow builds the Docker image in ACR, points App Service to the commit-specific image, and restarts the app. Database credentials remain in Key Vault/App Service settings and are not part of Git deployment.

## Credential rules

- Keep `.env` local only; it is ignored by Git.
- Use Key Vault references for App Service settings.
- Rotate the SQL password in Azure SQL and Key Vault together.
- Restrict Azure SQL networking to App Service outbound addresses or private networking.
- Never print `database_url`, `DB_PASSWORD`, or Key Vault values in logs.
