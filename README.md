# Page Pulse

Page Pulse is a production-quality, responsive Django web application that audits any website URL. It fetches target webpages, analyzes them for core SEO metrics and performance, and delivers structured details in a modern, single-page interface.

Built for the **Digital Heroes Training Task**.

---

## Features

- **Performance Auditing**: Measures the server response time of the target page.
- **SEO Metric Extraction**: Analyzes page title, meta description, and H1 heading counts.
- **Image Accessibility Checker**: Scans image tags and flags elements missing valid `alt` text.
- **Word Count Utility**: Computes approximate content word count inside the `<body>` tag, ignoring script and style tags.
- **Robust Exception Shielding**: Safely captures timeouts, invalid links, unreachable domains, and non-HTML contents, returning clean JSON structures without ever crashing.
- **Single Page Interface**: A high-fidelity, light-themed responsive SPA (Single Page Application) styled using clean Vanilla CSS and responsive grid elements.
- **CSRF Protected AJAX**: Secure asynchronous POST transactions using standard Django CSRF headers.

---

## Requirements

- **Python**: `3.10+` (Tested on Python 3.12.3)
- **Django**: `5.0`
- **requests**: `2.31+`
- **beautifulsoup4**: `4.12+`

---

## Installation

1. **Clone or copy the project files** into your working directory.
2. **Open a terminal** inside the root directory (`digital hero`).
3. **Install dependencies** using pip:
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Run Locally

1. **Apply database migrations** (pre-configures sqlite):
   ```bash
   python manage.py migrate
   ```
2. **Start the Django local development server**:
   ```bash
   python manage.py runserver
   ```
3. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:8000/
   ```

---

## API Endpoint Documentation

### Audit Endpoint

Run page checks programmatically via POST.

- **URL**: `/analyze/`
- **Method**: `POST`
- **Headers**:
  - `Content-Type: application/json`
  - `X-CSRFToken: <Token>` (For CSRF security when calling from external/browser requests)
- **Request Body**:
  ```json
  {
      "url": "https://example.com"
  }
  ```

#### Successful Response (HTTP 200)

```json
{
    "status": 200,
    "response_time": "325 ms",
    "title": "Example Domain",
    "meta_description": "Example description",
    "h1_count": 1,
    "images_missing_alt": 2,
    "word_count": 542
}
```

#### Error Response Example (e.g. HTTP 504 Timeout)

```json
{
    "error": "The request timed out. The website took too long to respond."
}
```

---

## Project Structure

```
digital hero/
│
├── manage.py                  # Django CLI entrypoint
├── requirements.txt           # Pip dependencies list
├── README.md                  # Project documentation
│
├── page_pulse/                # Django project config package
│   ├── __init__.py
│   ├── settings.py            # Registered app configurations
│   ├── urls.py                # Main url routing configurations
│   ├── wsgi.py
│   └── asgi.py
│
└── audit/                     # URL Auditing Application
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py               # UrlAuditForm validation
    ├── utils.py               # Text cleaning and word count helper methods
    ├── services.py            # Business logic (requests, BeautifulSoup parser)
    ├── views.py               # Thin view controller mapping routes
    ├── urls.py                # App-specific URL mapping
    ├── tests.py               # Test cases (successful parse, invalid, timeout)
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

## Design Decisions

1. **Separation of Concerns (Thin Controllers / Dedicated Services)**:
   We kept views in `views.py` thin and clean. The scraping, processing, parsing, and measuring logic is encapsulated inside `services.py`, with text extraction delegate functions located in `utils.py`. Input schema confirmation resides inside `forms.py`. This ensures high modularity, readability, and ease of unit testing.
   
2. **Type-Safe Domain-Specific Exceptions**:
   We defined a clean hierarchy of custom exceptions inheriting from `AuditError` (`InvalidUrlError`, `TimeoutError`, `NonHtmlResponseError`, `WebsiteUnreachableError`). This allows `services.py` to identify failure classes and `views.py` to catch them explicitly, mapping distinct errors to meaningful JSON feedback and appropriate HTTP response codes rather than throwing general 500 crashes.

3. **High-Fidelity Custom Light Theme (No Frameworks)**:
   To wow the user while strictly avoiding Bootstrap or Tailwind CSS, we crafted custom Vanilla CSS from scratch. It uses contemporary font styling (`Inter` + `Outfit`), HSL variable tokens, custom double-ring spinning keyframe loading states, glassmorphism cards, glowing border inputs, and standard screen grid breakpoints for robust multi-device display.

---

## Testing Instructions

Run the automated test suite using Django's standard CLI test harness:

```bash
python manage.py test audit
```

The test runner will set up a mock database, invoke mock responses representing success states, bad URLs, and timeout conditions, and return status results.
