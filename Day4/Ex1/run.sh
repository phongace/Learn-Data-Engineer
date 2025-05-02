#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project ID
PROJECT_ID="unique-axle-457602-n6"

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

# Function to create firewall rule
create_firewall_rule() {
    print_message $YELLOW "🔒 Creating firewall rules for SSH access..."
    
    # Check and create first firewall rule (allow-ssh)
    if gcloud compute firewall-rules describe allow-ssh --project=$PROJECT_ID &>/dev/null; then
        print_message $YELLOW "🗑️ Deleting existing allow-ssh rule..."
        gcloud compute firewall-rules delete allow-ssh --project=$PROJECT_ID --quiet
    fi
    
    print_message $YELLOW "🔥 Creating allow-ssh rule..."
    gcloud compute firewall-rules create allow-ssh \
        --project=$PROJECT_ID \
        --direction=INGRESS \
        --priority=1000 \
        --network=data-processing-vpc \
        --action=ALLOW \
        --rules=tcp:22 \
        --source-ranges=0.0.0.0/0 \
        --target-tags=data-processing
    
    check_error "Failed to create allow-ssh rule"

    # Check and create second firewall rule (allow-ssh-access)
    if gcloud compute firewall-rules describe allow-ssh-access --project=$PROJECT_ID &>/dev/null; then
        print_message $YELLOW "🗑️ Deleting existing allow-ssh-access rule..."
        gcloud compute firewall-rules delete allow-ssh-access --project=$PROJECT_ID --quiet
    fi
    
    print_message $YELLOW "🔥 Creating allow-ssh-access rule..."
    gcloud compute firewall-rules create allow-ssh-access \
        --project=$PROJECT_ID \
        --direction=INGRESS \
        --priority=1000 \
        --network=data-processing-vpc \
        --action=ALLOW \
        --rules=tcp:22 \
        --source-ranges=0.0.0.0/0 \
        --target-tags=data-processing
    
    check_error "Failed to create allow-ssh-access rule"
}

# Function to deploy infrastructure
deploy_infrastructure() {
    # 1. Delete existing infrastructure
    print_message $YELLOW "🗑️ Cleaning up existing infrastructure..."
    terraform destroy -auto-approve
    check_error "Failed to destroy existing infrastructure"

    # Wait for 30 seconds to ensure all resources are properly deleted
    print_message $YELLOW "⏳ Waiting for resources to be fully deleted..."
    sleep 30

    # 2. Initialize and create new infrastructure
    print_message $YELLOW "🚀 Creating new infrastructure..."

    # Initialize Terraform
    print_message $YELLOW "📦 Initializing Terraform..."
    terraform init
    check_error "Failed to initialize Terraform"

    # Plan the changes
    print_message $YELLOW "📋 Planning infrastructure changes..."
    terraform plan -out=tfplan
    check_error "Failed to create plan"

    # Apply the changes
    print_message $YELLOW "🏗️ Applying infrastructure changes..."
    terraform apply tfplan
    check_error "Failed to apply changes"

    # Clean up the plan file
    rm tfplan

    # Create firewall rule
    create_firewall_rule

    print_message $GREEN "✅ Infrastructure has been successfully created!"

    # Print resource information
    print_message $YELLOW "\n📋 Resource Information:"
    terraform output

    # Log instance details
    print_message $YELLOW "\n🖥️ Instance Details:"
    instance_name=$(terraform output -raw vm_name)
    instance_ext_ip=$(terraform output -raw vm_external_ip)
    instance_int_ip=$(terraform output -raw vm_internal_ip)
    
    print_message $GREEN "Instance Name: $instance_name"
    print_message $GREEN "External IP: $instance_ext_ip"
    print_message $GREEN "Internal IP: $instance_int_ip"

    print_message $YELLOW "\n🔍 You can verify your resources in the Google Cloud Console:"
    print_message $GREEN "VM Instances: https://console.cloud.google.com/compute/instances"
    print_message $GREEN "VPC Networks: https://console.cloud.google.com/networking/networks"
    print_message $GREEN "Cloud Storage: https://console.cloud.google.com/storage"
    print_message $GREEN "BigQuery: https://console.cloud.google.com/bigquery"

    print_message $YELLOW "\n🔑 To SSH into the instance, use option 2 of this script or run:"
    print_message $GREEN "gcloud compute ssh debian@$instance_name --zone=asia-southeast1-a"
}

# Function to SSH into instance
ssh_to_instance() {
    # Get instance name from Terraform output
    if [ ! -f "terraform.tfstate" ]; then
        print_message $RED "❌ No terraform state found. Please deploy the infrastructure first."
        exit 1
    fi

    instance_name=$(terraform output -raw vm_name)
    print_message $YELLOW "🔑 Connecting to instance $instance_name..."
    
    # Ensure firewall rules exist
    if ! gcloud compute firewall-rules describe allow-ssh --project=$PROJECT_ID &>/dev/null || \
       ! gcloud compute firewall-rules describe allow-ssh-access --project=$PROJECT_ID &>/dev/null; then
        print_message $YELLOW "Creating missing firewall rules..."
        create_firewall_rule
    fi

    # Try to SSH with timeout
    print_message $YELLOW "Attempting to SSH into instance..."
    timeout 60 gcloud compute ssh debian@$instance_name --zone=asia-southeast1-a --quiet -- "echo 'SSH connection successful'"
    
    if [ $? -eq 124 ]; then
        print_message $RED "SSH connection timed out. Please try again in a few moments."
        exit 1
    elif [ $? -ne 0 ]; then
        print_message $RED "Failed to SSH into instance. Please check your credentials and try again."
        exit 1
    fi
    
    # If successful, establish the actual SSH connection
    gcloud compute ssh debian@$instance_name --zone=asia-southeast1-a --quiet
}

# Main menu
print_message $YELLOW "Welcome to Infrastructure Management Script"
print_message $YELLOW "Please select an option:"
print_message $GREEN "1) Deploy Infrastructure"
print_message $GREEN "2) SSH into Instance"
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        deploy_infrastructure
        ;;
    2)
        ssh_to_instance
        ;;
    *)
        print_message $RED "❌ Invalid choice. Please select 1 or 2."
        exit 1
        ;;
esac 