#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting deployment process...${NC}"

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}Error: terraform is not installed${NC}"
    exit 1
fi

# Check if gcloud is installed and configured
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud is not installed${NC}"
    exit 1
fi

# Check if project ID is set in terraform.tfvars
if [ ! -f "terraform.tfvars" ]; then
    echo -e "${RED}Error: terraform.tfvars file not found${NC}"
    exit 1
fi

# Initialize Terraform
echo -e "${YELLOW}Initializing Terraform...${NC}"
terraform init

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Terraform initialization failed${NC}"
    exit 1
fi

# Validate Terraform configuration
echo -e "${YELLOW}Validating Terraform configuration...${NC}"
terraform validate

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Terraform validation failed${NC}"
    exit 1
fi

# Plan Terraform changes
echo -e "${YELLOW}Planning Terraform changes...${NC}"
terraform plan -out=tfplan

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Terraform plan failed${NC}"
    exit 1
fi

# Apply Terraform changes
echo -e "${YELLOW}Applying Terraform changes...${NC}"
terraform apply tfplan

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Terraform apply failed${NC}"
    exit 1
fi

# Show outputs
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${YELLOW}Resource Information:${NC}"
terraform output

# Clean up the plan file
rm tfplan

echo -e "${GREEN}Deployment process completed!${NC}"
echo -e "${YELLOW}You can SSH into the instance using:${NC}"
echo -e "gcloud compute ssh debian@$(terraform output -raw vm_name) --zone=$(terraform output -raw vm_zone)" 