# Endpoint Health Monitor

This project is a Python-based tool to monitor the health of endpoints defined in a YAML configuration file. It performs asynchronous health checks and logs the availability of each endpoint.

## Installation

1. Clone the repository or unzip the file contents:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Prepare a YAML configuration file (e.g., `sample.yaml`) with the endpoint details. The file should follow this structure:
   ```yaml
   - name: <endpoint-name>
     url: <endpoint-url>
     method: <HTTP-method>  # Optional, defaults to GET
     headers: <HTTP-headers>  # Optional
     body: <HTTP-body>  # Optional, must be a JSON-encoded string
   ```

2. Run the script:
   ```bash
   python main.py <config_file_path>
   ```

   Example:
   ```bash
   python main.py sample.yaml
   ```

3. The script will continuously monitor the endpoints and log their availability every 15 seconds.

## Changes and Issue Resolution

### 1. YAML Configuration File Validation
**Issue Identified:** The script did not handle invalid YAML configurations, which could cause runtime errors.

**Change Made:** A validator was added to ensure that the YAML file is properly formatted and that each endpoint has the required fields (`name` and `url`). Invalid configurations are ignored, and the script exits gracefully if the file is entirely invalid.

**Reason for Change:** This ensures that the script only processes valid configurations, improving reliability and user experience.

### 2. Asynchronous Health Checks and Monitoring
**Issue Identified:** The original implementation was not optimized for handling multiple endpoints efficiently. Health checks could block each other, and timeouts could delay subsequent checks.

**Change Made:** The health checks and monitoring logic were made asynchronous using `asyncio` and `aiohttp`. This allows multiple endpoints to be checked concurrently, and the monitoring loop runs every 15 seconds regardless of individual endpoint timeouts.

**Reason for Change:** This improves performance and ensures that the monitoring interval remains consistent, even with a large number of endpoints or slow responses.

### 3. Logging Improvements
**Issue Identified:** The logging was basic and did not provide sufficient context for each endpoint's status.
**Change Made:** The logging format was improved to include the endpoint name, URL, and status code. Additionally, a separate log file is created for each run, and the logs are rotated daily.
**Reason for Change:** This provides better visibility into the health of each endpoint and makes it easier to troubleshoot issues.

### 4. Error Handling and Retries
**Issue Identified:** The original implementation did not handle errors gracefully, which could lead to crashes or unhandled exceptions.
**Change Made:** Added error handling for network errors, timeouts, and invalid responses. The script now retries failed requests a specified number of times before marking an endpoint as down.
**Reason for Change:** This improves the robustness of the script and ensures that temporary network issues do not cause false positives in endpoint availability.

