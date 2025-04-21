import yaml
from collections import defaultdict
import aiohttp
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("monitoring.log"),
        logging.StreamHandler()
    ]
)


# Function to load configuration from the YAML file and verify if the yaml is valid
def load_config(file_path):
    """
    Load and validate the YAML configuration file as per the instructions.
    :param file_path:
    :return:
    """

    def validate_endpoint(endpoint):
        if not isinstance(endpoint.get('name'), str):
            raise ValueError("Each endpoint must have a 'name' field of type string.")
        if not isinstance(endpoint.get('url'), str):
            raise ValueError("Each endpoint must have a 'url' field of type string.")
        if 'method' in endpoint and not isinstance(endpoint['method'], str):
            raise ValueError("'method' field, if present, must be of type string.")
        if 'headers' in endpoint and not isinstance(endpoint['headers'], dict):
            raise ValueError("'headers' field, if present, must be a dictionary.")
        if 'body' in endpoint and not isinstance(endpoint['body'], str):
            raise ValueError("'body' field, if present, must be a JSON-encoded string.")

    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            if not isinstance(data, list):
                raise ValueError("YAML file must contain a list of endpoints.")
            for endpoint in data:
                validate_endpoint(endpoint)
            logging.info(   "Parsed and validated YAML data:", data)
            return data
    except yaml.YAMLError as e:
        logging.info(f"Error parsing YAML file: {e}")
        sys.exit(1)
    except Exception as e:
        logging.info(f"Error loading configuration: {e}")
        sys.exit(1)


# Function to perform health checks asynchronously
async def check_health(endpoint):
    url = endpoint.get('url')
    method = endpoint.get('method', 'GET').upper()  # Default to GET if not specified
    headers = endpoint.get('headers')
    body = endpoint.get('body')

    try:
        async with aiohttp.ClientSession() as session:
            start_time = asyncio.get_event_loop().time()
            for attempt in range(3):  # Retry logic: try up to 2 times
                try:
                    async with session.request(method, url, headers=headers, json=body, timeout=30) as response:
                        end_time = asyncio.get_event_loop().time()
                        if 200 <= response.status < 300 and end_time - start_time <= 0.5:
                            logging.info(f"Response from {url}: {response.status}")
                            return "UP"
                        else:
                            logging.info(f"Response from {url}: {response.status}")
                            return "DOWN"
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    logging.info(f"Attempt {attempt + 1} failed for {url}: {e}")
                    if attempt == 1:  # If it's the last attempt, mark as DOWN
                        return "DOWN"
    except Exception as e:
        logging.info(f"Unexpected error for {url}: {e}")
        return "DOWN"


async def monitor_endpoints(file_path):
    config = load_config(file_path)
    domain_stats = defaultdict(lambda: {"up": 0, "total": 0})

    async def check_and_update(endpoint):
        domain = endpoint.get('url').split('/')[2].split(':')[0]  # Extract domain from URL, ignoring port numbers
        print(f"Checking {domain}...")
        result = await check_health(endpoint)
        print(f"{domain} is {result}")

        domain_stats[domain]["total"] += 1
        if result == "UP":
            domain_stats[domain]["up"] += 1

    cycle = 1
    while True:
        logging.info(f"Cycle {cycle}: Starting endpoint checks...")
        tasks = [check_and_update(endpoint) for endpoint in config]
        await asyncio.gather(*tasks)

        # Log cumulative availability percentages
        for domain, stats in domain_stats.items():
            availability = round(100 * stats["up"] / stats["total"])
            logging.info(
                f"Domain: {domain}, Availability: {availability}% (Up: {stats['up']}, Total: {stats['total']})")

        logging.info(f"Cycle {cycle}: Sleeping for 15 seconds...")
        cycle += 1
        await asyncio.sleep(15)


# Entry point of the program
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python main.py <config_file_path>")
        sys.exit(1)

    config_file = sys.argv[1]
    try:
        asyncio.run(monitor_endpoints(config_file))
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
