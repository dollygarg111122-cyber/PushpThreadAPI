# PushpThreadsAPI

A FastAPI application for reading and writing the Pushp Threads product catalog in SQL Server.

## Data model

The API maps the supplied diagram:

- `ProductSupplier` has many `Product` records.
- `Product` has many `ProductSizeMapping` records.
- `ProductSizeMaster` has many `ProductSizeMapping` records.
- A unique constraint prevents the same product-size pair from being inserted twice.

## Run locally

1. Install Python 3.11+, a SQL Server ODBC driver, and create the `PushpThreads` database. The included template uses the `SQL Server` driver detected on the development machine; set `DB_DRIVER` to `ODBC Driver 18 for SQL Server` when that driver is installed instead.
2. Create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

3. Copy `.env.example` to `.env` and update the SQL Server settings.
   Set `APPLICATIONINSIGHTS_CONNECTION_STRING` to the Azure Application Insights connection string to enable request and error telemetry. Keep this value in environment variables or App Service settings; do not commit it.
4. Start the API:

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI.

## Azure SQL Database

Azure SQL Database is supported through the same API. In `.env`, use the Azure server name and SQL authentication:

```dotenv
DB_SERVER=your-server.database.windows.net
DB_PORT=1433
DB_NAME=PushpThreads
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_ENCRYPT=true
DB_TRUST_SERVER_CERTIFICATE=false
DB_TRUSTED_CONNECTION=false
DB_USER=your-sql-login
DB_PASSWORD=your-sql-password
```

Allow the client IP address in the Azure SQL firewall and run [database/schema.sql](database/schema.sql) against the target database before calling the product endpoints. The current configuration uses SQL authentication; Azure AD or managed identity authentication needs an additional token-based connection setup.

## Endpoints

- `GET|POST /api/v1/suppliers`
- `GET|POST /api/v1/sizes`
- `GET|POST /api/v1/products`
- `GET|POST /api/v1/product-size-mappings`
- `GET /health`

The service expects the tables shown in the diagram to already exist. Generate migrations separately when the database schema needs to be managed by the application.

For Azure App Service deployment and Key Vault credential management, see [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md).
