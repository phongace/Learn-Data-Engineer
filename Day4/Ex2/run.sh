#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_ID="unique-axle-457602-n6"
PROJECT_NAME="data-processing"
ENVIRONMENT="dev"
USER_EMAIL="lehongvi19x@gmail.com"

# Function to print colored messages
print_message() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check for errors
check_error() {
    if [ $? -ne 0 ]; then
        print_message $RED "❌ Error: $1"
        exit 1
    fi
}

# Function to check and set up authentication
setup_auth() {
    print_message $YELLOW "🔑 Checking authentication..."
    
    # Get current account
    current_account=$(gcloud config get-value account)
    
    # If not logged in or wrong account, do login
    if [ "$current_account" != "$USER_EMAIL" ]; then
        print_message $YELLOW "Logging in as $USER_EMAIL..."
        gcloud auth login $USER_EMAIL
        check_error "Failed to login"
        
        # Set project
        print_message $YELLOW "Setting project..."
        gcloud config set project $PROJECT_ID
        check_error "Failed to set project"
    else
        print_message $GREEN "Already logged in as $USER_EMAIL"
    fi
}

# Function to deploy infrastructure
deploy_infrastructure() {
    # First, ensure we're using the right account
    setup_auth
    
    # 0. Initialize Terraform first
    print_message $YELLOW "📦 Initializing Terraform..."
    terraform init
    check_error "Failed to initialize Terraform"

    # 1. Plan the changes
    print_message $YELLOW "📋 Planning infrastructure changes..."
    terraform plan -out=tfplan
    check_error "Failed to create plan"

    # 2. Apply the changes
    print_message $YELLOW "🏗️ Applying infrastructure changes..."
    terraform apply tfplan
    check_error "Failed to apply changes"

    # Clean up the plan file
    rm tfplan

    print_message $GREEN "✅ Infrastructure has been successfully created/updated!"

    # Print resource information
    print_message $YELLOW "\n📋 Resource Information:"
    terraform output

    # Save service account key to file
    print_message $YELLOW "\n🔑 Saving service account key..."
    terraform output -raw service_account_key > service-account-key.json 2>/dev/null || true
    
    if [ -f "service-account-key.json" ]; then
        print_message $GREEN "✅ Service account key saved to service-account-key.json"
    else
        print_message $YELLOW "⚠️ No new service account key was generated (using existing one)"
    fi

    print_message $YELLOW "\n🔍 You can verify your resources in the Google Cloud Console:"
    print_message $GREEN "Cloud Storage: https://console.cloud.google.com/storage"
    print_message $GREEN "IAM & Admin: https://console.cloud.google.com/iam-admin"
}

# Add new function to destroy infrastructure if needed
destroy_infrastructure() {
    # First, ensure we're using the right account
    setup_auth
    
    print_message $YELLOW "⚠️ This will destroy all infrastructure. Are you sure? (y/N)"
    read -p "" confirm
    
    if [ "$confirm" != "y" ]; then
        print_message $YELLOW "Aborted."
        return
    fi
    
    # 1. Clean up existing bucket and service account if they exist
    bucket_name="${PROJECT_NAME}-${ENVIRONMENT}-bucket"
    sa_name="${PROJECT_NAME}-${ENVIRONMENT}-sa"
    
    print_message $YELLOW "🗑️ Checking and cleaning up existing resources..."
    
    # Check and delete bucket
    if gsutil ls "gs://$bucket_name" &>/dev/null; then
        print_message $YELLOW "Found existing bucket. Deleting gs://$bucket_name..."
        gsutil rm -r "gs://$bucket_name"
        check_error "Failed to delete existing bucket"
    fi
    
    # Check and delete service account
    if gcloud iam service-accounts describe "$sa_name@$PROJECT_ID.iam.gserviceaccount.com" &>/dev/null; then
        print_message $YELLOW "Found existing service account. Deleting $sa_name..."
        gcloud iam service-accounts delete "$sa_name@$PROJECT_ID.iam.gserviceaccount.com" --quiet
        check_error "Failed to delete existing service account"
    fi

    # 2. Delete infrastructure
    print_message $YELLOW "🗑️ Destroying infrastructure..."
    terraform destroy -auto-approve
    check_error "Failed to destroy infrastructure"

    print_message $GREEN "✅ Infrastructure has been successfully destroyed!"
}

# Function to upload a file to the bucket
upload_file() {
    # First, ensure we're using the right account
    setup_auth
    
    if [ -z "$1" ]; then
        print_message $RED "❌ Please provide a file path to upload"
        exit 1
    fi

    local file_path=$1
    if [ ! -f "$file_path" ]; then
        print_message $RED "❌ File not found: $file_path"
        exit 1
    fi

    bucket_name=$(terraform output -raw bucket_name)
    print_message $YELLOW "📤 Uploading file to bucket: $bucket_name"
    
    gsutil cp "$file_path" "gs://$bucket_name/"
    check_error "Failed to upload file"
    
    print_message $GREEN "✅ File uploaded successfully!"
}

# Function to list bucket contents
list_bucket() {
    # First, ensure we're using the right account
    setup_auth
    
    bucket_name=$(terraform output -raw bucket_name)
    print_message $YELLOW "📋 Listing contents of bucket: $bucket_name"
    
    gsutil ls -l "gs://$bucket_name"
    check_error "Failed to list bucket contents"
}

# Main menu
print_message $YELLOW "Welcome to Storage Bucket Management Script"
print_message $YELLOW "Please select an option:"
print_message $GREEN "1) Deploy/Update Infrastructure"
print_message $GREEN "2) Upload File to Bucket"
print_message $GREEN "3) List Bucket Contents"
print_message $GREEN "4) Destroy Infrastructure"
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        deploy_infrastructure
        ;;
    2)
        read -p "Enter the path to the file you want to upload: " file_path
        upload_file "$file_path"
        ;;
    3)
        list_bucket
        ;;
    4)
        destroy_infrastructure
        ;;
    *)
        print_message $RED "❌ Invalid choice. Please select 1-4."
        exit 1
        ;;
esac 