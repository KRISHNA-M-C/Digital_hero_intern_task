# Page Pulse

## Project Overview
Page Pulse is a production-quality website auditing tool designed to evaluate and report critical SEO metrics and page loading characteristics. By entering any webpage URL, Page Pulse fetches the target page, parses its HTML content, calculates performance timings, and dynamically generates a detailed SEO audit report. The application features a lightweight Python/Django backend and a responsive, vanilla HTML5/CSS3/JavaScript single-page frontend.

---

## Features
- **HTTP Status**: Displays the direct HTTP response code returned by the target server.
- **Response Time**: Measures the elapsed time (in milliseconds) taken to fetch the webpage.
- **Page Title**: Extracts the page title content from the HTML `<title>` tag.
- **Meta Description**: Fetches the descriptive text from the `<meta name="description">` tag.
- **H1 Count**: Counts the quantity of structural `<h1>` header tags present on the page.
- **Images Missing Alt Text**: Audits `<img>` elements and reports those without valid or populated `alt` attributes.
- **Approximate Word Count**: Estimates total visible body words, completely ignoring `<script>` and `<style>` tag contents.
- **Error Handling**: Gracefully intercepts invalid inputs, timeouts, non-HTML page returns, and unreachable domains.
- **Responsive UI**: A professional, minimal light-themed dashboard optimized for desktop, tablet, and mobile screens.

---

## Technology Stack
- **Backend**: Python 3.12, Django 5.0 (Latest stable 5.x)
- **Frontend**: Semantic HTML5, CSS3 Custom Properties, Vanilla JavaScript (ES6)
- **Libraries**: `requests` (HTTP client), `beautifulsoup4` (HTML parser)
- **WSGI Server**: `gunicorn` (for production serving)
- **Static Assets**: `whitenoise` (for serving compressed and cached assets on Render)

---

## Project Structure
```
digital hero/
├── manage.py                  # Django CLI entrypoint
├── requirements.txt           # Pip dependencies (Django, requests, bs4, gunicorn, whitenoise)
├── runtime.txt                # Python environment version specification for Render
├── build.sh                   # Deployment script for installing, collecting static assets, and migrating
├── README.md                  # Project documentation (this file)
│
├── page_pulse/                # Project Configuration Package
│   ├── __init__.py
│   ├── settings.py            # Registered app configurations, WhiteNoise static files, and security keys
│   ├── urls.py                # Main url routing configurations directing to the audit app
│   ├── wsgi.py                # WSGI entrypoint for Gunicorn
│   └── asgi.py                # ASGI entrypoint
│
└── audit/                     # URL Auditing Core Application
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py               # UrlAuditForm for validating URL syntax
    ├── utils.py               # Text cleaning and word count calculation helper methods
    ├── services.py            # Business logic (fetching logic and BeautifulSoup parser)
    ├── views.py               # Thin view controller mapping routes and rendering JSON reports
    ├── urls.py                # App-specific URL mapping (/ and /analyze/)
    ├── tests.py               # Test cases (successful parse, invalid url, request timeout)
    │
    ├── templates/
    │   └── audit/
    │       └── index.html     # Single Page HTML5 template
    │
    └── static/
        └── audit/
            ├── css/
            │   └── style.css  # Premium Custom Light Theme CSS
            └── js/
                └── app.js     # Vanilla Javascript AJAX & DOM handler
```

---

## Installation

Follow these step-by-step instructions to set up the project locally:

1. **Clone the repository**:
   ```bash
   git clone <GitHub URL>
   cd "digital hero"
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Start the local server**:
   ```bash
   python manage.py runserver
   ```
   Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## Running Tests

Execute the automated test suite with the following command:
```bash
python manage.py test audit
```

The tests verify:
- **Successful Page Analysis**: Correct extraction of status, response timing, title text, meta description, H1 elements, images missing alt attributes, and word count from standard HTML.
- **Invalid URL Formats**: Rejection of inputs missing schemas (e.g., `google.com`) or utilizing wrong schemas (e.g., `ftp://`).
- **Request Timeout**: Proper throwing and catching of `TimeoutError` when the server takes too long to respond.
- **Non-HTML Response**: Verification that non-HTML mime types (like PDFs) throw `NonHtmlResponseError`.
- **Website Unreachable**: Handlers confirming that DNS failures or connection refusals throw `WebsiteUnreachableError`.

---

## API Contract

### Audit URL Endpoint

Audits a URL and returns structured metrics.

- **URL**: `/analyze/`
- **Method**: `POST`
- **Headers**:
  - `Content-Type: application/json`
  - `X-CSRFToken: <Token>` (For CSRF security when calling inside the browser session)

- **Request**:
  ```json
  {
      "url": "https://example.com"
  }
  ```

- **Successful Response (HTTP 200)**:
  ```json
  {
      "status": 200,
      "response_time": "250 ms",
      "title": "Example Domain",
      "meta_description": "Example description",
      "h1_count": 1,
      "images_missing_alt": 2,
      "word_count": 456
  }
  ```

- **Error Response (e.g., HTTP 400)**:
  ```json
  {
      "error": "Please enter a valid URL (including http:// or https://)."
  }
  ```

### Common HTTP Response Codes
- `200 OK`: Request succeeded, webpage analyzed, metrics returned.
- `400 Bad Request`: Sent JSON was invalid, URL missing, or URL format is incorrect.
- `415 Unsupported Media Type`: Page returned a non-HTML content type (e.g., PDF, JSON, PNG).
- `502 Bad Gateway`: Target server was unreachable, down, or connection refused.
- `504 Gateway Timeout`: Target server took more than 10 seconds to respond.

---

## Design Decisions

### 1. Separation of Concerns (Business Logic in services.py)
Moving business logic out of `views.py` and into `services.py` follows the clean architecture paradigm and Django best practices. By doing so, we ensure that views act solely as entry points that parse HTTP requests and return HTTP responses. This isolation makes the core audit logic easier to unit test, since it doesn't depend on Django's request-response lifecycle mocks. It also makes the application highly maintainable, as parsing rules or libraries can be swapped without touching the controllers.

### 2. BeautifulSoup Chosen for Lightweight HTML Parsing
BeautifulSoup4 was selected as the HTML parser due to its simplicity, speed, and reliability. It provides a clean, pythonic API for traversing, searching, and modifying parse trees, making it perfect for mining specific SEO tags like title, description, and headers. Unlike heavier rendering engines (such as Selenium), BeautifulSoup processes static raw HTML, making audits extremely fast and resource-efficient. It also handles poorly formatted or invalid HTML documents gracefully, ensuring that parser failures do not crash the application.

### 3. Custom Domain-Specific Exception Handlers
Using custom domain-specific exception classes (such as `InvalidUrlError`, `TimeoutError`, `NonHtmlResponseError`, and `WebsiteUnreachableError`) enables precise error categorization. Instead of catching general exceptions and returning generic 500 error messages, we can trace exactly what failed during the auditing lifecycle. The view controller catches these specific domain errors and maps them to appropriate HTTP status codes (400, 408, 415, 502) and descriptive JSON error payloads. This strategy provides clear, actionable debugging information to the client while keeping the application completely crash-proof.

---

## Future Improvements
- **Asynchronous Audits**: Implement Celery background tasks or Django Channels ASGI handlers to prevent locking threads on slow website requests.
- **Audit History**: Add a user dashboard and database logs using Django Models to track, view, and compare past audits.
- **Exporting Reports**: Build exporters to download compiled audit metrics as clean PDF files or CSV sheets.
- **Batch URL Audits**: Allow users to enter a list of multiple URLs to run comparative batch tests.
- **SEO Scoring System**: Develop an algorithm to grade the target URL's page quality out of 100 based on metadata completeness and alt descriptions.
- **Accessibility & Lighthouse Audits**: Integrate checks for color contrast, screen reader compatibility, and script performance factors.

---

## Live Demo
Placeholders for production deployment. *Note: Replace these URLs after configuring your hosting provider.*

- **Live Application**: `<Render URL>` (e.g., `https://pagepulse.onrender.com`)
- **GitHub Repository**: `<GitHub URL>` (e.g., `https://github.com/your-username/page-pulse`)

---

## Footer Requirement
The frontend displays a footer on every page containing the mandatory text:
**Built for Digital Heroes Training Task**
where the text "Digital Heroes" is a hyperlink linking directly to:
[https://digitalheroesco.com](https://digitalheroesco.com)
