"""Test cases for HTMLArk."""

import importlib
import os.path
import unittest

import htmlark

# Check for existance of requests
requests_spec = importlib.util.find_spec('requests')
requests_available = True if requests_spec else False


class TestHTMLArk(unittest.TestCase):  # NOQA
    """Test HTMLArk module."""

    def test_make_data_uri(self):
        """Test functionality of data URI creation."""
        samplestring = b"TEST DATA"
        sample_base64 = "VEVTVCBEQVRB"
        sample_quoted = "TEST%20DATA"

        # No MIME type means text/plain in a data URI
        self.assertEqual(htmlark.make_data_uri(None, samplestring),
                         "data:," + sample_quoted)
        self.assertEqual(htmlark.make_data_uri('text/css', samplestring),
                         "data:text/css," + sample_quoted)
        self.assertEqual(htmlark.make_data_uri('application/javascript', samplestring),
                         "data:application/javascript," + sample_quoted)
        self.assertEqual(htmlark.make_data_uri('image/jpeg', samplestring),
                         "data:image/jpeg;base64," + sample_base64)
        self.assertEqual(htmlark.make_data_uri('unknown/mime', samplestring),
                         "data:unknown/mime;base64," + sample_base64)

    @unittest.skipUnless(requests_available, "Requests library not installed")
    def test_get_resource(self):
        """Test getting resources."""
        test_filename = os.path.join(os.path.dirname(__file__), "testpages/test.txt")
        with open(test_filename, "rb") as test_file:
            test_data = test_file.read()
        test_resource = ('text/plain', test_data)

        self.assertEqual(htmlark._get_resource(test_filename), test_resource)

    def test_get_resource_errors(self):
        """Test that _get_resource raises the correct errors."""
        with self.assertRaises(ValueError):
            htmlark._get_resource("ftp://example.com/not/a/real/path.png")
            htmlark._get_resource("data:text/plain,somedummydata")
        # Simulate the effects of the 'requests' module not existing
        htmlark.requests_get = None
        with self.assertRaises(NameError):
            htmlark._get_resource("http://example.com/not/a/real/path.png")
