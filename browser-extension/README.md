# GitOrchestrator Browser Extension

This browser extension enables the URL replacement feature to work with your local GitOrchestrator instance.

## Installation

1. **Load the Extension in Chrome**:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" in the top right
   - Click "Load unpacked"
   - Select this directory

2. **Configure Local Server**:
   - Make sure your GitOrchestrator is running locally (default: http://localhost:5000)
   - If using a different port, update `LOCAL_SERVER` in `background.js`

## Usage

With the extension installed:
1. Browse any GitHub repository
2. The extension will automatically redirect requests to your local GitOrchestrator instance
3. Your local instance will handle the request just like the production version would

## Development Setup

If you want to modify the extension:
1. Edit `background.js` to change the redirect behavior
2. Edit `manifest.json` to modify permissions or metadata
3. Reload the extension in Chrome after making changes

## Production vs Local

This extension makes the URL replacement feature work exactly the same way as it would in production, but pointing to your local instance instead of gitorchestrator.com.

### How it Works

1. **Production Environment**:
   ```
   github.com/user/repo -> gitorchestrator.com/user/repo
   ```

2. **Local Development**:
   ```
   github.com/user/repo -> localhost:5000/user/repo
   ```

The functionality remains identical - the only difference is where the request is sent.
