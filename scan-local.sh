#!/bin/bash
# Scan Local Development Directory
# Triggers ParallelDev to scan d:\dev for projects

SCAN_DIRECTORY="d:\\dev"
API_URL="http://localhost:8000/api/scan"

echo -e "\033[36mScanning directory: $SCAN_DIRECTORY\033[0m"
echo -e "\033[33mThis may take a few moments...\033[0m"
echo ""

# Trigger scan
response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{\"directory\": \"$SCAN_DIRECTORY\"}")

# Check if curl succeeded
if [ $? -ne 0 ]; then
    echo -e "\033[31mError: Could not connect to backend API\033[0m"
    echo -e "\033[33mMake sure the backend is running (./start-backend.sh)\033[0m"
    exit 1
fi

# Parse response
status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [ "$status" = "success" ]; then
    projects_found=$(echo "$response" | grep -o '"projects_found":[0-9]*' | cut -d':' -f2)
    projects_saved=$(echo "$response" | grep -o '"projects_saved":[0-9]*' | cut -d':' -f2)

    echo -e "\033[32mScan completed successfully!\033[0m"
    echo ""
    echo -e "\033[36mResults:\033[0m"
    echo -e "  Projects found: $projects_found"
    echo -e "  Projects saved: $projects_saved"
    echo ""

    if [ "$projects_found" -gt 0 ]; then
        echo -e "\033[32mView your projects at: http://localhost:8001\033[0m"
    else
        echo -e "\033[33mNo projects found. Make sure your projects have REQUIREMENTS.md, TODO.md, or README.md files.\033[0m"
    fi
else
    echo -e "\033[31mError scanning directory:\033[0m"
    echo "$response" | grep -o '"message":"[^"]*"' | cut -d'"' -f4
fi
