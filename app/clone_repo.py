from git import Repo

def cloneRepo():

	# GitHub repo URL and destination folder
	repo_url = "https://github.com/alphyemmanuel/node-dependency-deprecator-analyzer-sample-project.git"
	destination = "./cloned_repo"

	# Clone the repository
	Repo.clone_from(repo_url, destination)

	print(f"Repository cloned successfully to {destination}")
	return 'Success'

cloneRepo()