#!/bin/bash

# Set working directory
cd "$(dirname "$0")"

echo "=== Stopping and removing all Docker containers ==="
docker-compose down
docker rm -f $(docker ps -aq) 2>/dev/null || true
docker volume prune -f

echo "=== Starting Kestra container ==="
docker-compose up -d

# Simplified: wait a fixed time and check once
echo "=== Waiting 10 seconds for Kestra to start ==="
sleep 10

# Check once
echo "=== Checking Kestra API ==="
if curl -s --head --request GET http://localhost:8080/api/health | grep "200" > /dev/null; then
    echo "Kestra API is working properly!"
else
    echo "WARNING: Kestra API may not be ready. Continuing anyway..."
fi

# Delete all existing flows before uploading
echo "=== Deleting all existing flows ==="
# Get all namespaces
namespaces=$(curl -s "http://localhost:8080/api/v1/flows/distinct-namespaces" | jq -r '.[]')
for namespace in $namespaces; do
    echo "Checking namespace: $namespace"
    # Get all flows in the namespace
    flows=$(curl -s "http://localhost:8080/api/v1/flows/$namespace" | jq -r '.[].id')
    for flow in $flows; do
        echo "Deleting flow: $namespace/$flow"
        curl -s -X DELETE "http://localhost:8080/api/v1/flows/$namespace/$flow"
    done
done
echo "All existing flows have been deleted."

# Count the number of flow files
flow_files=(flows/*.yml)
file_count=${#flow_files[@]}
echo "=== Found $file_count flow files to upload ==="

# Push all flow files to Kestra API
echo "=== Uploading flow files to Kestra ==="
counter=1
for flow_file in flows/*.yml; do
    echo "[$counter/$file_count] Uploading $flow_file..."
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:8080/api/v1/flows" \
        -H "Content-Type: application/x-yaml" \
        --data-binary @"$flow_file")
    
    if [ "$response" == "200" ] || [ "$response" == "201" ]; then
        echo "✅ Successfully uploaded $flow_file"
    else
        echo "❌ Failed to upload $flow_file (HTTP $response)"
        # Print detailed error
        curl -s -X POST "http://localhost:8080/api/v1/flows" \
            -H "Content-Type: application/x-yaml" \
            --data-binary @"$flow_file"
        echo ""
    fi
    counter=$((counter + 1))
done

echo "=== Process completed ==="
echo "Kestra UI available at: http://localhost:8080/ui"