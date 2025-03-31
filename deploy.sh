#!/bin/bash

# Exit on error
set -e

# Load environment variables
if [ -f .env ]; then
    source .env
fi

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Azure CLI is not installed. Please install it first:"
    echo "https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo "Please log in to Azure first:"
    echo "az login"
    exit 1
fi

# Create resource group if it doesn't exist
echo "Creating resource group..."
az group create --name confseeker-rg --location westeurope

# Create Azure Service Bus namespace and queue
echo "Creating Azure Service Bus namespace and queue..."
az servicebus namespace create --name confseeker-sb --resource-group confseeker-rg --location westeurope
az servicebus queue create --name conference-notifications --namespace-name confseeker-sb --resource-group confseeker-rg

# Get Service Bus connection string
SERVICE_BUS_CONNECTION_STRING=$(az servicebus namespace authorization-rule keys list \
    --resource-group confseeker-rg \
    --namespace-name confseeker-sb \
    --name RootManageSharedAccessKey \
    --query primaryConnectionString \
    --output tsv)

# Create Azure Communication Services
echo "Creating Azure Communication Services..."
az communication create --name confseeker-comm --location westeurope --data-location westeurope

# Get Communication Services connection string
COMMUNICATION_CONNECTION_STRING=$(az communication list-key \
    --name confseeker-comm \
    --resource-group confseeker-rg \
    --query primaryConnectionString \
    --output tsv)

# Create Azure SQL Database
echo "Creating Azure SQL Database..."
az sql server create --name confseeker-sql --resource-group confseeker-rg --location westeurope --admin-user confseekeradmin --admin-password "$AZURE_SQL_PASSWORD"
az sql db create --resource-group confseeker-rg --server confseeker-sql --name confseekerdb

# Get SQL connection string
SQL_CONNECTION_STRING=$(az sql db show-connection-string --client sqlcmd --server confseeker-sql --database confseekerdb --output tsv)

# Create App Service
echo "Creating App Service..."
az webapp create --resource-group confseeker-rg --plan confseeker-plan --name confseeker-api --runtime "PYTHON:3.9"

# Configure environment variables
echo "Configuring environment variables..."
az webapp config appsettings set --name confseeker-api --resource-group confseeker-rg --settings \
    DATABASE_URL="$SQL_CONNECTION_STRING" \
    AZURE_SERVICEBUS_CONNECTION_STRING="$SERVICE_BUS_CONNECTION_STRING" \
    AZURE_SERVICEBUS_QUEUE_NAME="conference-notifications" \
    AZURE_COMMUNICATION_CONNECTION_STRING="$COMMUNICATION_CONNECTION_STRING" \
    AZURE_COMMUNICATION_SENDER_EMAIL="$AZURE_COMMUNICATION_SENDER_EMAIL" \
    SIMILARITY_THRESHOLD="0.7" \
    API_URL="https://confseeker-api.azurewebsites.net/api"

# Deploy the application
echo "Deploying application..."
az webapp up --name confseeker-api --resource-group confseeker-rg --runtime python:3.9

echo "Deployment complete!"
echo "Your application is available at: https://confseeker-api.azurewebsites.net"
echo "Please verify your sender email address in Azure Communication Services portal" 