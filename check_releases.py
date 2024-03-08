import requests

# Assuming file.txt is structured as RepoName==Version
dependency_file = "dependencies.rqr"

def get_latest_release(user_repo):
    url = f"https://api.github.com/repos/{user_repo}/releases/latest"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["tag_name"]
    else:
        print(f"Error fetching release for {user_repo}")
        return None

def main():
    with open(dependency_file, "r") as file:
        for line in file:
            repo, version = line.strip().split("==")
            latest_version = get_latest_release(f"sudopablosilva/{repo}")
            if latest_version and latest_version != version:
                print(f"New release for {repo}: {latest_version}")
                # Here you can add your notification logic
            else:
                print(f"No new release for {repo}. Current version: {version}")

if __name__ == "__main__":
    main()
