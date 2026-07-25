from django.test import TestCase
from unittest.mock import patch, MagicMock
import requests

from .services import (
    analyze_url,
    InvalidUrlError,
    TimeoutError,
    NonHtmlResponseError,
    WebsiteUnreachableError,
)

class AuditServiceTests(TestCase):
    """
    Tests for Page Pulse auditing business logic.
    """

    @patch('requests.get')
    def test_successful_analysis(self, mock_get):
        """
        Tests that analyze_url correctly parses valid HTML content
        and extracts SEO metrics properly.
        """
        # Mock HTML body
        html_content = (
            "<html>"
            "<head>"
            "  <title>  Page Pulse Testing Page  </title>"
            "  <meta name='description' content='A test meta description for testing.'>"
            "</head>"
            "<body>"
            "  <h1>Title Header One</h1>"
            "  <p>Hello world. This is a simple test website to check word counts.</p>"
            "  <!-- 2 images, both missing valid alt text (one empty, one missing alt attribute) -->"
            "  <img src='image1.png' alt=''>"
            "  <img src='image2.png'>"
            "  <!-- 1 image with valid alt text -->"
            "  <img src='image3.png' alt='Valid alt'>"
            "</body>"
            "</html>"
        )
        
        # Configure Mock Response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html; charset=utf-8'}
        mock_response.content = html_content.encode('utf-8')
        mock_get.return_value = mock_response

        # Execute
        report = analyze_url("https://digitalheroesco.com")

        # Verify
        self.assertEqual(report["status"], 200)
        self.assertTrue(report["response_time"].endswith("ms"))
        self.assertEqual(report["title"], "Page Pulse Testing Page")
        self.assertEqual(report["meta_description"], "A test meta description for testing.")
        self.assertEqual(report["h1_count"], 1)
        self.assertEqual(report["images_missing_alt"], 2)
        # Word count is from body, ignoring tags.
        # "Title Header One Hello world. This is a simple test website to check word counts."
        # Words: Title(1) Header(2) One(3) Hello(4) world(5) This(6) is(7) a(8) simple(9) test(10) website(11) to(12) check(13) word(14) counts(15). 
        # Total words count is approximately 15.
        self.assertEqual(report["word_count"], 15)

    def test_invalid_url_format(self):
        """
        Tests that analyze_url raises InvalidUrlError for incorrectly formatted URLs.
        """
        invalid_urls = [
            "google.com",              # missing schema
            "ftp://google.com",        # wrong schema
            "http://",                 # incomplete
            "https://invalid space",   # invalid characters
            "not_a_url"
        ]
        
        for url in invalid_urls:
            with self.assertRaises(InvalidUrlError):
                analyze_url(url)

    @patch('requests.get')
    def test_request_timeout(self, mock_get):
        """
        Tests that analyze_url raises TimeoutError if the requests GET times out.
        """
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with self.assertRaises(TimeoutError):
            analyze_url("https://example.com")

    @patch('requests.get')
    def test_non_html_response(self, mock_get):
        """
        Tests that analyze_url raises NonHtmlResponseError if target content is not text/html.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/pdf'}
        mock_response.content = b"%PDF-1.4..."
        mock_get.return_value = mock_response
        
        with self.assertRaises(NonHtmlResponseError):
            analyze_url("https://example.com/document.pdf")

    @patch('requests.get')
    def test_website_unreachable(self, mock_get):
        """
        Tests that analyze_url raises WebsiteUnreachableError if target connection is refused or DNS fails.
        """
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        with self.assertRaises(WebsiteUnreachableError):
            analyze_url("https://unreachablesite12345.com")
