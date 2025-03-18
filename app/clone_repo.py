from git import Repo, GitCommandError
import os

def clone_or_pull_repo():
	# GitHub repo URL and destination folder
    repo_url = "https://github.com/alphyemmanuel/node-dependency-deprecator-analyzer-sample-project.git"
    destination = "./cloned_repo"
    try:
        if os.path.exists(destination):
            print("Repository already exists. Pulling latest changes...")
            repo = Repo(destination)
            repo.git.fetch()  
            repo.git.pull()  
            repo.close()
        else:
            print("Cloning repository...")
            repo = Repo.clone_from(repo_url, destination)
            repo.close()
            print("Clone completed.")

        print(f"Repository cloned successfully to {destination}")
        return 'Success'
    except GitCommandError as e:
        print(f"Git command error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

clone_or_pull_repo()