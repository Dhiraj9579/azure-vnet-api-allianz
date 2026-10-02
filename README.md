# Azure VNet Challenge API

A small FastAPI project built for the Azure networking challenge.

This repository contains a simple API that creates an Azure Virtual Network with multiple subnets, stores the result locally, and allows authenticated users to fetch the created data back through the API.

## Goal

- create a VNet with one or more subnets
- save the VNet and subnet metadata
- retrieve the stored data through API calls
- protect the VNet endpoints with JWT authentication

## Project structure

```text
azure-vnet-api-challenge/
├── src/
│   ├── __init__.py
│   ├── auth.py
│   ├── azure_client.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── routes/
│       └── vnet_routes.py
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── vnet-api.db
```

## Requirements

- Python 3.10+
- Azure subscription access for real Azure resource creation
- Azure resource group for the VNet deployment

## Setup

```bash
git clone <your-repo-url>
cd azure-vnet-api-challenge
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Environment variables

Copy `.env.example` to `.env` and replace the sample values.

```env
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_RESOURCE_GROUP=your-resource-group
JWT_SECRET_KEY=replace-with-a-random-secret-key
DATABASE_URL=sqlite:///./vnet-api.db
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
```

## Run the API

```bash
uvicorn src.main:app --reload
```

The app will be available at:

```text
http://localhost:8000
```

## Authentication

The VNet endpoints are protected by JWT bearer tokens.

Generate a token:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/token?user_id=user123&username=testuser"
```

Example response:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

## Create a VNet with subnets

```bash
curl -X POST "http://localhost:8000/api/v1/vnets" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt-token>" \
  -d '{
    "name": "challenge-vnet",
    "location": "eastus",
    "address_space": "10.0.0.0/16",
    "subnets": [
      {"name": "frontend", "address_prefix": "10.0.1.0/24"},
      {"name": "backend", "address_prefix": "10.0.2.0/24"}
    ]
  }'
```

## Retrieve VNet data

List all VNets:

```bash
curl -H "Authorization: Bearer <jwt-token>" \
  "http://localhost:8000/api/v1/vnets?skip=0&limit=10"
```

Get one VNet by ID:

```bash
curl -H "Authorization: Bearer <jwt-token>" \
  "http://localhost:8000/api/v1/vnets/<vnet-id>"
```

## Notes

This project is intentionally limited to the challenge scope: create VNet, add subnets, persist records, read them back, and protect access with JWT.

If Azure credentials are not provided, the app falls back to mock Azure responses for local testing and validation.
