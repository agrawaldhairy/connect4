# Define variables
PYTHON_ENV = venv
FLASK_APP_DIR = .
REACT_APP_DIR = ./connect-four-ui

# Create and activate Python virtual environment, install requirements
.PHONY: setup-flask
setup-flask:
	@echo "Setting up Flask environment..."
	@cd $(FLASK_APP_DIR) && python3 -m venv $(PYTHON_ENV)
	@cd $(FLASK_APP_DIR) && . $(PYTHON_ENV)/bin/activate && pip install -r requirements.txt

# Install npm packages for React app
.PHONY: setup-react
setup-react:
	@echo "Setting up React environment..."
	@cd $(REACT_APP_DIR) && npm install

# Run both Flask and React apps
.PHONY: run
run:
	@echo "Starting Flask and React apps..."
	@cd $(FLASK_APP_DIR) && . $(PYTHON_ENV)/bin/activate && FLASK_APP=app.py FLASK_ENV=development flask run &
	@sleep 5 # Wait for Flask app to start
	@cd $(REACT_APP_DIR) && npm start

# Clean up the environment
.PHONY: clean
clean:
	@echo "Cleaning up..."
	@cd $(FLASK_APP_DIR) && rm -rf $(PYTHON_ENV)
	@cd $(REACT_APP_DIR) && rm -rf node_modules

# Setup everything
.PHONY: setup
setup: setup-flask setup-react

# Complete setup and run
.PHONY: all
all: setup run

