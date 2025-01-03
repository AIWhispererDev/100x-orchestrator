# Browser Extension Documentation

## Overview

The GitOrchestrator browser extension is a Chrome extension that enables automatic URL redirection from GitHub repositories to the GitOrchestrator instance. It's built using Chrome's Manifest V3 and uses declarative net request rules for efficient URL redirection.

## Extension Structure

The extension is located in the `browser-extension` directory and consists of these key files:

```
browser-extension/
├── manifest.json     # Extension configuration
├── rules.json       # URL redirection rules
├── background.js    # Background script
└── README.md        # Installation instructions
```

### 1. Manifest Configuration (manifest.json)

```json
{
  "manifest_version": 3,
  "name": "GitOrchestrator URL Redirector",
  "version": "1.0",
  "description": "Redirects github.com URLs to your local GitOrchestrator instance",
  "permissions": [
    "declarativeNetRequest"
  ],
  "host_permissions": [
    "*://github.com/*"
  ],
  "declarative_net_request": {
    "rule_resources": [{
      "id": "ruleset_1",
      "enabled": true,
      "path": "rules.json"
    }]
  }
}
```

### 2. Redirection Rules (rules.json)

```json
[
  {
    "id": 1,
    "priority": 1,
    "action": {
      "type": "redirect",
      "redirect": {
        "regexSubstitution": "http://localhost:5000\\1"
      }
    },
    "condition": {
      "regexFilter": "^https?://github\\.com(/.*)",
      "resourceTypes": ["main_frame"]
    }
  }
]
```

## Installation Guide

1. **Prerequisites**:
   - Google Chrome browser
   - GitOrchestrator running locally (default: http://localhost:5000)

2. **Installation Steps**:
   ```
   1. Open Chrome
   2. Navigate to chrome://extensions/
   3. Enable "Developer mode" (top right toggle)
   4. Click "Load unpacked"
   5. Select the 'browser-extension' directory
   ```

3. **Verification**:
   - Look for the GitOrchestrator extension icon in Chrome's toolbar
   - Visit any GitHub repository - it should automatically redirect to your local instance

## How It Works

### Local Development Mode

1. User visits a GitHub URL:
   ```
   https://github.com/username/repository
   ```

2. Extension intercepts the request using the regex pattern:
   ```
   ^https?://github\\.com(/.*) 
   ```

3. URL is transformed to local instance:
   ```
   http://localhost:5000/username/repository
   ```

### Production Mode

1. User visits a GitHub URL:
   ```
   https://github.com/username/repository
   ```

2. URL is transformed to production instance:
   ```
   https://gitorchestrator.com/username/repository
   ```

## Technical Details

1. **Manifest V3 Features**:
   - Uses `declarativeNetRequest` for efficient URL redirection
   - No background service worker needed
   - Minimal permissions required

2. **URL Processing**:
   - Regex-based URL matching
   - Path preservation during redirection
   - Main frame requests only (no subresources)

3. **Security Considerations**:
   - Host permissions limited to GitHub URLs
   - No access to page content
   - No script injection

## Troubleshooting

1. **Extension Not Redirecting**:
   - Verify extension is enabled in Chrome
   - Check if local GitOrchestrator is running
   - Ensure port 5000 is correct and available

2. **Port Configuration**:
   - Default port is 5000
   - To change port:
     1. Update `rules.json` regex substitution
     2. Reload extension

## Development

To modify the extension:

1. **Change Redirect Target**:
   - Edit `rules.json` regex substitution pattern
   - Update host permissions in `manifest.json` if needed

2. **Testing Changes**:
   - Make edits to configuration files
   - Go to chrome://extensions
   - Click the refresh icon on the extension
   - Test with a GitHub URL

## Related Documentation

- [URL Replacement Guide](url_replacement.md)
- [Redirect System](redirect.md)
- [Flask Backend Documentation](../README.md)
