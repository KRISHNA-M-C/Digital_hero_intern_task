import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie

from .services import (
    analyze_url,
    InvalidUrlError,
    TimeoutError,
    NonHtmlResponseError,
    WebsiteUnreachableError,
)

@ensure_csrf_cookie
def index(request):
    """
    Renders the single-page application landing page.
    Sets the CSRF cookie on the browser so our AJAX requests can access it.
    """
    return render(request, 'audit/index.html')

@require_http_methods(["POST"])
def analyze(request):
    """
    Exposes the endpoint: POST /analyze/
    Accepts JSON body: {"url": "https://example.com"}
    Analyzes the URL content and returns a JSON audit report.
    """
    # 1. Parse JSON body
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body. Please send a valid JSON request."}, status=400)
        
    url = data.get("url")
    if not url:
        return JsonResponse({"error": "URL parameter is required."}, status=400)
        
    # 2. Invoke auditing service
    try:
        report = analyze_url(url)
        return JsonResponse(report)
    except InvalidUrlError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except TimeoutError as e:
        return JsonResponse({"error": str(e)}, status=504)
    except NonHtmlResponseError as e:
        return JsonResponse({"error": str(e)}, status=415)
    except WebsiteUnreachableError as e:
        return JsonResponse({"error": str(e)}, status=502)
    except Exception as e:
        # Catch-all to guarantee that "the application must never crash"
        return JsonResponse({"error": f"An unexpected system error occurred: {str(e)}"}, status=500)
