import requests
import logging
import os

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

dependency_file = "file.txt"

def get_latest_release(user_repo):
    url = f"https://api.github.com/repos/{user_repo}/releases/latest"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",  # Using an environment variable for the token
        "X-GitHub-Api-Version": "2022-11-28"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an exception for 4XX/5XX errors
        return response.json()["tag_name"]
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred for {user_repo}: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request exception occurred for {user_repo}: {req_err}")
    except KeyError:
        logging.error(f"Could not find the 'tag_name' key in the response for {user_repo}.")
    return None

def main():
    try:
        with open(dependency_file, "r") as file:
            for line in file:
                repo, version = line.strip().split("==")
                latest_version = get_latest_release(f"sudopablosilva/{repo}")
                if latest_version and latest_version != version:
                    logging.info(f"New release for {repo}: {latest_version}")
                    # Here you can add your notification logic
                elif latest_version:
                    logging.info(f"No new release for {repo}. Current version: {version}")
                else:
                    logging.warning(f"Could not check releases for {repo}")
    except FileNotFoundError:
        logging.error(f"Dependency file '{dependency_file}' not found.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
