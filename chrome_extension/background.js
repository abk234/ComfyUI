// Background service worker for ComfyWorkflows Downloader

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'DOWNLOAD_FILE') {
        // Download the file
        chrome.downloads.download({
            url: message.url,
            filename: message.filename,
            saveAs: false
        }, (downloadId) => {
            if (chrome.runtime.lastError) {
                console.error('Download error:', chrome.runtime.lastError);
                sendResponse({ success: false, error: chrome.runtime.lastError.message });
            } else {
                sendResponse({ success: true, downloadId: downloadId });
            }
        });
        return true; // Keep channel open for async response
    }

    if (message.type === 'GET_WORKFLOW') {
        // Request workflow extraction from content script
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0]) {
                chrome.tabs.sendMessage(tabs[0].id, { type: 'EXTRACT_WORKFLOW' }, (response) => {
                    sendResponse(response);
                });
            }
        });
        return true;
    }

    if (message.type === 'WORKFLOW_FOUND') {
        // Workflow was found by content script
        console.log('Workflow found:', message.workflow);
    }
});
