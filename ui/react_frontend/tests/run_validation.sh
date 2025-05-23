#!/bin/bash
# Script to run validation of mock implementations

# Set CI environment variable
export CI=true

# Create log directory if it doesn't exist
mkdir -p logs

# Create report directory if it doesn't exist
mkdir -p test-results

# Log file
LOG_FILE="logs/run-validation.log"
echo "Starting validation at $(date)" > "$LOG_FILE"

# Run the validation script
echo "Running validation script..."
node tests/validate_mock_implementations.js

# Store the exit code
EXIT_CODE=$?

# Log the result
if [ $EXIT_CODE -eq 0 ]; then
  echo "Validation successful" | tee -a "$LOG_FILE"
else
  echo "Validation failed with exit code $EXIT_CODE" | tee -a "$LOG_FILE"
fi

# Create a marker file to indicate validation was run
echo "Validation run at $(date)" > "test-results/validation-run.txt"
echo "Exit code: $EXIT_CODE" >> "test-results/validation-run.txt"

# Exit with the validation exit code
exit $EXIT_CODE
