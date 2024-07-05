#!/bin/bash

# Navigate to the directory containing the Flask app
cd .

# Start the Flask app
# Make sure to use the appropriate environment variables if needed
export FLASK_APP=./app.py
export FLASK_ENV=development

# Start the Flask app in the background
flask run &

# Save the Flask process ID
FLASK_PID=$!

# Function to kill both processes
function cleanup {
    echo "Stopping Flask and React apps..."
    kill $FLASK_PID
}

# Trap the EXIT signal to ensure both apps are stopped when the script exits
trap cleanup EXIT

# Check if Flask app is running
FLASK_URL="http://127.0.0.1:5000"
echo "Checking if Flask app is running..."
# shellcheck disable=SC2091
until $(curl --output /dev/null --silent --head --fail $FLASK_URL); do
    printf '.'
    sleep 1
done

echo "Flask app is running successfully."

# Navigate to the directory containing the React app
# shellcheck disable=SC2164
cd connect-four-ui

# Start the React app
npm start &

# Save the React process ID
REACT_PID=$!

# Wait a few seconds to ensure React app starts
sleep 5

# Check if React app is running
REACT_URL="http://localhost:3000"
echo "Checking if React app is running..."
# shellcheck disable=SC2091
until $(curl --output /dev/null --silent --head --fail $REACT_URL); do
    printf '.'
    sleep 1
done

echo "React app is running successfully."

echo "Both Flask and React apps are running successfully."

# Wait for both processes to exit
wait $FLASK_PID
wait $REACT_PID
