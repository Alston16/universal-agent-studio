#!/bin/bash

# This script updates the dependencies in requirements.txt based on the current virtual environment.

# Check if a virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "No virtual environment detected. Please activate a virtual environment first."
    exit 1
fi

# Define the requirements file
REQUIREMENTS_FILE="requirements.txt"

# Generate the updated requirements file
echo "Updating $REQUIREMENTS_FILE with current virtual environment dependencies..."
pip freeze > "$REQUIREMENTS_FILE"

if [[ $? -eq 0 ]]; then
    echo "Dependencies successfully updated in $REQUIREMENTS_FILE."
else
    echo "Failed to update dependencies. Please check for errors."
    exit 1
fi