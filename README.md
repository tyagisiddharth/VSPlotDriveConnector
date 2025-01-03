# VSPlotDriveConnector

## Description
VSPlotDriveConnector is a microservice designed to automatically save all plots generated in Visual Studio Code to Google Drive using Google Drive API credentials. This tool enables seamless backup of visualization work, particularly useful for illustrating ML model performance metrics such as accuracy to non-technical audiences.

## Features
1. **Automatic Backup**: Automatically saves plots to Google Drive.
2. **Integration with VS Code**: Operates directly within the Visual Studio Code environment.
3. **Secure**: Utilizes Google Drive API credentials for secure data transfer.
4. **User-Friendly**: Easy setup and configuration—simply call the API with the required parameters.

## Requirements
1. Visual Studio Code
2. Google Drive API credentials

## Setup

### 1. Configuration
- Set up your configurations in the `src/settings.py` file.
- Configure folder settings in `targets_plot_uploader.py` at line 288.
- Specify file names and formats (e.g., PDF, JPG, PNG) and other settings as needed.

### 2. Start the Microservice
Run the following commands to start the VSPlotDriveConnector microservice bot:
```bash
cd VSPlotDriveConnector
python app.py
```
This will start the Flask server and make the microservice available for use.

### 3. Configure Google Drive API Credentials
- Obtain your Google Drive API credentials by following these steps:
  1. Navigate to the Google Cloud Console and go to the "APIs and Services" section.
  2. Click on the **"ENABLE APIS AND SERVICES"** button.
  3. Locate "Google Drive API" under the "Google Workspace" section and click on it.
  4. Enable the API if not already enabled (otherwise, click **"Manage"**).
  5. Create a service account under the **"Create Credentials"** section if you don’t already have one.
  6. Generate an API key under the service account. A JSON file will be downloaded—store it securely as it contains sensitive information.
  7. Place the JSON credentials in the `src/api_credentials.json` file.

### 4. Call the Flask Server API
- Run the `Client_request/call_VSPlotDriveConnector.py` file to interact with the microservice.
- Ensure that your input parameters are configured as outlined in the `schema.graphql` file.

### 5. Verify Operation
- After calling the API, you should receive email notifications (configured in `settings.py`) and see generated plots automatically saved to your Google Drive.

## Usage
The `targets_plot_generator.py` file contains functions for generating plots. Currently, it supports:
1. **Ratio Plot**
2. **Comparison Plot**
3. **Scatter Plots**

You can also define additional plot functions in this file to extend functionality.

---
This microservice streamlines the process of saving and sharing visualizations, ensuring efficient workflow and effective communication of insights.

