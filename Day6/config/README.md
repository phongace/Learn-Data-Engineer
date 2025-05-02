# Google Cloud Platform Credentials Setup

This directory should contain your Google Cloud Platform service account key for authentication with GCP services.

## Setting up credentials

1. Create a GCP service account with appropriate permissions (Storage Admin is recommended for this workflow)
2. Generate a JSON key for the service account
3. Save the JSON key as `service_account_key.json` in this directory
4. **Important**: This file contains sensitive credentials and should never be committed to Git

## Example structure

Your service account key should look similar to the sample file `service-account-sample.json` but with real credentials:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "service-account@your-project-id.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "...",
  "universe_domain": "googleapis.com"
}
```

## Usage in workflows

The workflows are configured to expect the credentials file at `/config/service_account_key.json` in the Docker container. The file gets mounted into the container at runtime.

_Note: The actual file path can be configured in the workflow's `vars` section if needed._
