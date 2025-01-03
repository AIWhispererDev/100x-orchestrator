// Service worker for Manifest V3
chrome.runtime.onInstalled.addListener(() => {
  console.log('GitOrchestrator URL Redirector installed');
});

chrome.webRequest.onBeforeRequest.addListener(
  function(details) {
    // Only handle github.com URLs
    if (details.url.includes('github.com')) {
      // Extract the path from the GitHub URL
      const url = new URL(details.url);
      const path = url.pathname;
      
      // Construct the new URL pointing to your local server
      const newUrl = `${LOCAL_SERVER}${path}`;
      
      return {
        redirectUrl: newUrl
      };
    }
  },
  {
    urls: ["*://github.com/*"],
    types: ["main_frame"] // Only redirect main page loads, not resources
  },
  ["blocking"]
);
