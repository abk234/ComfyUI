// Content script for ComfyWorkflows.com workflow downloader
// This script runs on workflow pages and extracts workflow JSON

(function() {
    'use strict';

    // Extract workflow ID from URL
    function getWorkflowId() {
        const match = window.location.pathname.match(/\/workflows?\/([^/]+)/);
        return match ? match[1] : null;
    }

    // Extract workflow data from the page
    function extractWorkflowData() {
        let workflowData = null;

        // Strategy 1: Check window objects
        const possibleLocations = [
            window.__NEXT_DATA__?.props?.pageProps?.workflow,
            window.__NEXT_DATA__?.props?.pageProps?.data,
            window.__INITIAL_STATE__?.workflow,
            window.workflow,
        ];

        for (const data of possibleLocations) {
            if (data && typeof data === 'object') {
                if (data.nodes || (typeof data === 'string' && data.includes('"nodes"'))) {
                    workflowData = typeof data === 'string' ? JSON.parse(data) : data;
                    break;
                }
            }
        }

        // Strategy 2: Intercept fetch/XMLHttpRequest to catch API calls
        if (!workflowData) {
            // Store original fetch
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                return originalFetch.apply(this, args).then(response => {
                    if (response.url.includes('api') && response.headers.get('content-type')?.includes('json')) {
                        response.clone().json().then(data => {
                            if (data && typeof data === 'object' && data.nodes) {
                                workflowData = data;
                                // Notify background script
                                chrome.runtime.sendMessage({
                                    type: 'WORKFLOW_FOUND',
                                    workflow: workflowData
                                });
                            }
                        }).catch(() => {});
                    }
                    return response;
                });
            };
        }

        return workflowData;
    }

    // Create download button on the page
    function createDownloadButton() {
        // Check if button already exists
        if (document.getElementById('comfyworkflows-download-btn')) {
            return;
        }

        const button = document.createElement('button');
        button.id = 'comfyworkflows-download-btn';
        button.textContent = '📥 Download Workflow';
        button.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 10000;
            padding: 12px 24px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: background 0.3s;
        `;

        button.addEventListener('mouseenter', () => {
            button.style.background = '#45a049';
        });

        button.addEventListener('mouseleave', () => {
            button.style.background = '#4CAF50';
        });

        button.addEventListener('click', async () => {
            button.textContent = '⏳ Extracting...';
            button.disabled = true;

            // Wait a bit for page to fully load
            await new Promise(resolve => setTimeout(resolve, 2000));

            let workflowData = extractWorkflowData();

            // If not found, try to get from network requests
            if (!workflowData) {
                // Request background script to intercept
                chrome.runtime.sendMessage({
                    type: 'GET_WORKFLOW',
                    url: window.location.href
                }, (response) => {
                    if (response && response.workflow) {
                        downloadWorkflow(response.workflow);
                    } else {
                        showError('Could not extract workflow. Try using browser DevTools.');
                    }
                    button.textContent = '📥 Download Workflow';
                    button.disabled = false;
                });
            } else {
                downloadWorkflow(workflowData);
                button.textContent = '📥 Download Workflow';
                button.disabled = false;
            }
        });

        document.body.appendChild(button);
    }

    // Download workflow as JSON file
    function downloadWorkflow(workflowData) {
        const workflowId = getWorkflowId() || 'workflow';
        const filename = `comfyworkflow_${workflowId}.json`;
        const blob = new Blob([JSON.stringify(workflowData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        chrome.runtime.sendMessage({
            type: 'DOWNLOAD_FILE',
            url: url,
            filename: filename
        });

        // Show success message
        showMessage('Workflow downloaded!', 'success');
    }

    // Show message to user
    function showMessage(text, type = 'info') {
        const message = document.createElement('div');
        message.textContent = text;
        message.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10001;
            padding: 16px 24px;
            background: ${type === 'success' ? '#4CAF50' : '#f44336'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            font-size: 14px;
        `;

        document.body.appendChild(message);
        setTimeout(() => message.remove(), 3000);
    }

    function showError(text) {
        showMessage(text, 'error');
    }

    // Initialize when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(createDownloadButton, 2000);
        });
    } else {
        setTimeout(createDownloadButton, 2000);
    }

    // Listen for messages from background script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.type === 'EXTRACT_WORKFLOW') {
            const workflow = extractWorkflowData();
            sendResponse({ workflow: workflow });
        }
    });
})();
