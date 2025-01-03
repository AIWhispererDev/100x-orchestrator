# URL Replacement in Gitingest

Gitingest provides a convenient way to create LLM-friendly digests of GitHub repositories by simply replacing `github.com` with `gitingest.com` in any GitHub URL. This document explains how this functionality works under the hood.

## How It Works

### 1. URL Transformation

When you have a GitHub URL like:
```
https://github.com/username/repository
```

You can transform it to a Gitingest URL by replacing `github.com` with `gitingest.com`:
```
https://gitingest.com/username/repository
```

### 2. Backend Processing

The URL replacement system works through several steps:

#### 2.1 URL Capture
- A catch-all route handler (`/{full_path:path}`) captures any path after the domain
- When you enter `gitingest.com/username/repo`, it captures `username/repo` as the `full_path`

#### 2.2 GitHub URL Reconstruction
- The system reconstructs the original GitHub URL by prepending `https://github.com/` to the captured path
- Example: `username/repo` becomes `https://github.com/username/repo`

#### 2.3 Repository Processing
1. **URL Parsing**: The URL is parsed to extract:
   - Username
   - Repository name
   - Branch/commit (if specified)
   - Subpath (if specified)

2. **Repository Cloning**: The system clones the repository locally

3. **Content Processing**: 
   - Files are processed according to size limits and patterns
   - A digest is generated that's optimized for LLM prompts

4. **Result Display**: 
   - The processed content is rendered in a user-friendly format
   - Includes repository structure, content summaries, and token estimates

## Example Usage

1. Start with a GitHub URL:
   ```
   https://github.com/cyclotruc/gitingest
   ```

2. Replace `github.com` with `gitingest.com`:
   ```
   https://gitingest.com/cyclotruc/gitingest
   ```

3. The system will automatically:
   - Clone the repository
   - Process its contents
   - Generate an LLM-friendly digest
   - Display the results in your browser

## Benefits

- **Seamless Integration**: Works with any public GitHub repository
- **No Additional Steps**: Just change the URL - no need for additional commands or tools
- **LLM Optimized**: Output is formatted specifically for use with language models
- **Customizable**: Supports filtering by file patterns and size limits

## Technical Implementation

The functionality is implemented through:
- FastAPI route handlers that capture all paths
- URL parsing and validation
- Repository cloning and processing
- Template rendering for displaying results

The system is designed to handle various GitHub URL formats, including:
- Repository root URLs
- Specific branches or commits
- Subdirectories within repositories
