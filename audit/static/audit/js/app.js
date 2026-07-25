document.addEventListener('DOMContentLoaded', () => {
    const auditForm = document.getElementById('audit-form');
    const targetUrlInput = document.getElementById('target-url');
    const submitBtn = document.getElementById('submit-btn');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    const loadingContainer = document.getElementById('loading-container');
    const reportContainer = document.getElementById('report-container');
    const reportBadgeUrl = document.getElementById('report-badge-url');
    
    // Result DOM fields
    const valStatus = document.getElementById('val-status');
    const statusExplanation = document.getElementById('status-explanation');
    const valResponseTime = document.getElementById('val-response-time');
    const valTitle = document.getElementById('val-title');
    const valDescription = document.getElementById('val-description');
    const valH1Count = document.getElementById('val-h1-count');
    const valImagesMissingAlt = document.getElementById('val-images-missing-alt');
    const valWordCount = document.getElementById('val-word-count');
    const statusCard = document.querySelector('.status-card');

    // Retrieve CSRF token from head meta
    const getCsrfToken = () => {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    };

    // Helper to explain HTTP statuses
    const getStatusExplanation = (code) => {
        if (code >= 200 && code < 300) return 'Success / OK';
        if (code >= 300 && code < 400) return 'Redirected';
        if (code === 401) return 'Unauthorized';
        if (code === 403) return 'Forbidden Access';
        if (code === 404) return 'Page Not Found';
        if (code === 500) return 'Internal Server Error';
        if (code === 503) return 'Service Unavailable';
        return `HTTP Status Code ${code}`;
    };

    auditForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const urlValue = targetUrlInput.value.trim();
        if (!urlValue) return;

        // Reset UI State
        errorContainer.classList.add('hidden');
        reportContainer.classList.add('hidden');
        loadingContainer.classList.remove('hidden');
        
        // Disable controls during request
        targetUrlInput.disabled = true;
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.7';
        submitBtn.style.cursor = 'not-allowed';

        try {
            const csrfToken = getCsrfToken();
            const response = await fetch('/analyze/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ url: urlValue })
            });

            const data = await response.json();

            if (response.ok) {
                // Populate report details
                reportBadgeUrl.textContent = urlValue;
                valStatus.textContent = data.status;
                statusExplanation.textContent = getStatusExplanation(data.status);
                
                // Color status card based on 2xx success
                statusCard.classList.remove('status-success', 'status-failure');
                if (data.status >= 200 && data.status < 300) {
                    statusCard.classList.add('status-success');
                } else {
                    statusCard.classList.add('status-failure');
                }

                valResponseTime.textContent = data.response_time;
                
                // Textual content safety fallbacks
                valTitle.textContent = data.title ? data.title : 'No Title Tag Found';
                valTitle.classList.toggle('text-italic', !data.title);
                
                valDescription.textContent = data.meta_description ? data.meta_description : 'No meta description tag found on this page.';
                valDescription.classList.toggle('text-italic', !data.meta_description);

                valH1Count.textContent = data.h1_count;
                valImagesMissingAlt.textContent = data.images_missing_alt;
                valWordCount.textContent = data.word_count.toLocaleString();

                // Display reports
                reportContainer.classList.remove('hidden');
                
                // Smooth scroll to report
                reportContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                // Display server validated error message
                errorMessage.textContent = data.error || 'An error occurred during website auditing.';
                errorContainer.classList.remove('hidden');
            }
        } catch (err) {
            // Network loss / crash error catch
            errorMessage.textContent = 'Could not connect to the Page Pulse audit server. Please check your internet connection and try again.';
            errorContainer.classList.remove('hidden');
        } finally {
            // Restore form control elements
            loadingContainer.classList.add('hidden');
            targetUrlInput.disabled = false;
            submitBtn.disabled = false;
            submitBtn.style.opacity = '';
            submitBtn.style.cursor = '';
        }
    });
});
