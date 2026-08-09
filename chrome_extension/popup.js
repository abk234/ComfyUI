// Popup script for ComfyWorkflows Downloader

document.addEventListener('DOMContentLoaded', () => {
    const downloadBtn = document.getElementById('downloadBtn');
    const statusDiv = document.getElementById('status');

    function showStatus(message, type) {
        statusDiv.textContent = message;
        statusDiv.className = `status ${type}`;
        setTimeout(() => {
            statusDiv.textContent = '';
            statusDiv.className = '';
        }, 3000);
    }

    downloadBtn.addEventListener('click', async () => {
        downloadBtn.disabled = true;
        downloadBtn.textContent = '⏳ Extracting...';

        // Get current tab
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (!tabs[0]) {
                showStatus('No active tab found', 'error');
                downloadBtn.disabled = false;
                downloadBtn.textContent = 'Download Current Workflow';
                return;
            }

            const url = tabs[0].url;
            if (!url.includes('comfyworkflows.com/workflow') && !url.includes('comfyworkflows.com/workflows')) {
                showStatus('Please navigate to a workflow page first', 'error');
                downloadBtn.disabled = false;
                downloadBtn.textContent = 'Download Current Workflow';
                return;
            }

            // Request workflow extraction
            chrome.tabs.sendMessage(tabs[0].id, { type: 'EXTRACT_WORKFLOW' }, (response) => {
                if (chrome.runtime.lastError) {
                    showStatus('Error: ' + chrome.runtime.lastError.message, 'error');
                    downloadBtn.disabled = false;
                    downloadBtn.textContent = 'Download Current Workflow';
                    return;
                }

                if (response && response.workflow) {
                    // Download the workflow
                    const workflowId = url.match(/\/workflows?\/([^/]+)/)?.[1] || 'workflow';
                    const filename = `comfyworkflow_${workflowId}.json`;
                    const blob = new Blob([JSON.stringify(response.workflow, null, 2)], { type: 'application/json' });
                    const blobUrl = URL.createObjectURL(blob);

                    chrome.runtime.sendMessage({
                        type: 'DOWNLOAD_FILE',
                        url: blobUrl,
                        filename: filename
                    }, (downloadResponse) => {
                        if (downloadResponse && downloadResponse.success) {
                            showStatus('✓ Workflow downloaded!', 'success');
                        } else {
                            showStatus('Download failed', 'error');
                        }
                        downloadBtn.disabled = false;
                        downloadBtn.textContent = 'Download Current Workflow';
                        URL.revokeObjectURL(blobUrl);
                    });
                } else {
                    showStatus('Could not extract workflow. Try using the button on the page.', 'error');
                    downloadBtn.disabled = false;
                    downloadBtn.textContent = 'Download Current Workflow';
                }
            });
        });
    });
});
