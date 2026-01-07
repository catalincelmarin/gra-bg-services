# Module `kimera.dev.GitManager`

Wrapper around GitHub's REST API and GitPython for repo lifecycle automation.

## `GitManager(token: str, username: str)`
Stores credentials and prepares default headers (`Authorization: token ...`, `Accept: application/vnd.github.v3+json`).

### Connectivity helpers
- `is_connected() -> bool`: Confirms that the token belongs to `username` by hitting `/user`.
- `repo_exists(repo_name) -> bool`: Pages through the authenticated user's repos to check for an existing name (case-insensitive).

### Repo administration
- `create_repo(repo_name, private=True) -> bool`: Creates a repository (auto-initialised) unless it already exists.
- `delete_repo(repo_name) -> bool`: Deletes an owned repository, returning `True` on HTTP 204.
- `invite_user(repo_name, invitee_username) -> bool`: Sends a collaborator invite with `push` permissions.
- `list_repos_starting_with(prefix) -> list[str]`: Returns repo names with the given prefix (only the first page of results is processed).

### Local git operations
- `clone_repo(repo_name, clone_dir) -> bool`: Clones over HTTPS with embedded username/token. Short-circuits if `clone_dir` already exists.
- `add_commit(repo_dir, message) -> None`: `git add -A` followed by a commit via GitPython.
- `push(repo_dir, branch="main") -> bool`: Pushes to the origin remote.
- `pull(repo_dir, branch="main") -> bool`: Pulls latest changes.
- `create_branch(repo_dir, branch_name) -> None`: Creates and checks out a new branch.

All git operations emit human-readable errors by catching `GitCommandError`.
