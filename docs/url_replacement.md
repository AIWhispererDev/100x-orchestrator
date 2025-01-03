# URL Replacement Feature

## Overview

The URL replacement feature allows you to instantly analyze and merge changes from different branches or repositories by simply replacing `github.com` with `gitorchestrator.com` in your browser's URL bar. This provides a seamless way to handle git operations and code merging without leaving your browsing workflow.

## How It Works

### 1. URL Transformation

When browsing GitHub, simply change the domain:

```
Original: https://github.com/username/repository
Replace with: https://gitorchestrator.com/username/repository
```

You can also specify branches:
```
Original: https://github.com/username/repository/tree/feature-branch
Replace with: https://gitorchestrator.com/username/repository/tree/feature-branch
```

### 2. Backend Process

The system automatically:

1. Captures the repository path and branch information
2. Validates your GitHub token
3. Clones the repository locally
4. Initializes AI agents to analyze the code
5. Handles git operations (commit, push, PR)

### 3. Git Operations

The system manages all git operations automatically:

1. **Repository Setup**
   - Clones the repository
   - Configures git credentials
   - Creates new branches for changes

2. **Code Changes**
   - AI agents analyze and modify code
   - Changes are committed with descriptive messages
   - Code is pushed to the remote repository

3. **Pull Requests**
   - Automatically creates PRs for changes
   - Adds appropriate labels and descriptions
   - Assigns reviewers if configured

## Example Usage

1. **View a Pull Request on GitHub**
   ```
   You're viewing: https://github.com/username/repo/pull/123
   ```

2. **Replace Domain**
   ```
   Change to: https://gitorchestrator.com/username/repo/pull/123
   ```

3. **Automatic Processing**
   - AI agents analyze the PR
   - Changes are reviewed and processed
   - Additional commits are made if needed
   - PRs are created or updated automatically

4. **Review Changes**
   - View the agent's analysis
   - Monitor git operations
   - Review generated PRs

## Technical Implementation

The feature is implemented through:

1. **URL Routing**
   ```python
   @app.route('/<path:github_path>')
   def handle_github_redirect(github_path):
       # Extract repository and branch info
       # Validate GitHub token
       # Initialize agents for git operations
   ```

2. **Git Operations**
   - Automated commit generation
   - Branch management
   - PR creation and updates

3. **Pull Request Management**
   - Uses GitHub API for repository interaction
   - Handles branch synchronization
   - Manages PR metadata (labels, reviewers)

## Benefits

- **Automated Git Operations**: No manual git commands needed
- **Branch Management**: Handles multiple branches automatically
- **PR Integration**: Creates and updates PRs as needed
- **Code Analysis**: AI-powered code review and modification

## Requirements

- Valid GitHub token with repository access
- Proper domain setup for `gitorchestrator.com`
- Running instance of the orchestrator application
- Write access to target repositories
