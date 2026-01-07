import os.path

import requests
from git import Repo, GitCommandError
from kimera.helpers.Helpers import Helpers


class GitManager:
    def __init__(self, token, username):
        self.token = token
        self.username = username
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

    def is_connected(self):
        """Check if the provided GitHub token and username are valid."""
        url = "https://api.github.com/user"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            user_data = response.json()
            if user_data.get("login") == self.username:
                print("Token and username are valid.")
                return True
            else:
                print("Token is valid but username does not match.")
                return False
        else:
            print(f"Failed to validate token and username: {response.content}")
            return False

    def repo_exists(self, repo_name):
        """Check if a GitHub repository exists for the authenticated user."""
        url = f"https://api.github.com/user/repos"
        params = {'per_page': 200, 'page': 1}
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            repos = response.json()
            for repo in repos:
                if repo['name'].lower() == repo_name.lower():
                    print(f"Repository '{repo_name}' already exists.")
                    return True
            return False
        else:
            print(f"Failed to retrieve repositories: {response.content}")
            return False

    def invite_user(self, repo_name, invitee_username):
        """
        Invite a user to a repository.

        :param repo_name: Name of the repository.
        :param invitee_username: GitHub username of the invitee.
        :return: True if the invitation was sent successfully, False otherwise.
        """
        if not self.repo_exists(repo_name):
            print(f"Repository '{repo_name}' does not exist.")
            return False

        url = f"https://api.github.com/repos/{self.username}/{repo_name}/collaborators/{invitee_username}"
        data = {
            "permission": "push"  # You can adjust this to "pull", "push", or "admin" depending on permissions
        }

        response = requests.put(url, headers=self.headers, json=data)

        if response.status_code in [201, 204]:
            print(f"User '{invitee_username}' invited to repository '{repo_name}'.", flush=True)
            return True
        else:
            print(f"Failed to invite user: {response.content}", flush=True)
            return False

    def create_repo(self, repo_name, private=True):
        if self.repo_exists(repo_name=repo_name):
            return True
        """Create a new GitHub repository."""
        url = f"https://api.github.com/user/repos"
        payload = {
            "name": repo_name,
            "private": private,
            "auto_init": True
        }
        response = requests.post(url, json=payload, headers=self.headers)

        if response.status_code == 201:
            print(f"Repository '{repo_name}' created successfully.", flush=True)
            return True
        else:
            print(f"Failed to create repository: {response.content}", flush=True)
            return False

    def clone_repo(self, repo_name, clone_dir):
        """Clone a repository."""
        repo_url = f"https://{self.username}:{self.token}@github.com/{self.username}/{repo_name}.git"
        Helpers.sysPrint("pth", f"{clone_dir}/{repo_name}")
        if os.path.exists(f"{clone_dir}"):
            return True
        try:
            Helpers.infoPrint(repo_url)
            Repo.clone_from(repo_url, clone_dir)
            return True
        except GitCommandError as e:
            Helpers.print(e)
            return False

    def add_commit(self, repo_dir, message):
        """Add and commit changes."""
        try:
            repo = Repo(repo_dir)
            repo.git.add(A=True)
            repo.index.commit(message)
            print(f"Committed changes: {message}")
        except GitCommandError as e:
            print(f"Error committing: {e}")

    def push(self, repo_dir, branch="main"):
        """Push changes to GitHub."""
        try:
            repo = Repo(repo_dir)
            origin = repo.remote(name='origin')
            origin.push(branch)
            print(f"Pushed changes to branch {branch}.")
            return True
        except GitCommandError as e:
            print(f"Error pushing to GitHub: {e}")
            return False

    def pull(self, repo_dir, branch="main"):
        """Pull changes from GitHub."""
        try:
            repo = Repo(repo_dir)
            origin = repo.remote(name='origin')
            origin.pull(branch)
            print(f"Pulled latest changes from branch {branch}.")
            return True
        except GitCommandError as e:
            print(f"Error pulling changes: {e}")
            return False

    def create_branch(self, repo_dir, branch_name):
        """Create a new branch."""
        try:
            repo = Repo(repo_dir)
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            print(f"Switched to new branch '{branch_name}'.")
        except GitCommandError as e:
            print(f"Error creating branch: {e}")

    def delete_repo(self, repo_name):
        """Delete a repository on GitHub."""
        url = f"https://api.github.com/repos/{self.username}/{repo_name}"
        response = requests.delete(url, headers=self.headers)

        if response.status_code == 204:
            print(f"Repository '{repo_name}' deleted successfully.", flush=True)
            return True
        else:
            print(f"Failed to delete repository: {response.content}", flush=True)
            return False

    def list_repos_starting_with(self, prefix):
        """
        List all repositories that start with a given prefix.

        :param prefix: The prefix string to match repository names.
        :return: A list of repository names that start with the given prefix.
        """
        url = f"https://api.github.com/user/repos"
        params = {'per_page': 200, 'page': 1}
        repos_matching = []

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            repos = response.json()

            # Filter repositories by prefix
            for repo in repos:
                if repo['name'].startswith(prefix):
                    repos_matching.append(repo['name'])

            # Check if there's a next page of repositories
            if 'next' in response.links:
                url = response.links['next']['url']

        return repos_matching
