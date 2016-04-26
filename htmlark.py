#!/usr/bin/env python3
"""Embed images, CSS, and JavaScript into an HTML file, using data URIs."""
__version__ = "1.0.0"

import argparse
import base64
from datetime import datetime
import mimetypes
import sys
from typing import Callable
from urllib.parse import quote
from urllib.parse import urljoin
from urllib.parse import urlparse

import bs4
# Import requests if available, dummy it if not
try:
    from requests import get as requests_get
    from requests import RequestException
except ImportError:
    requests_get = None

    class RequestException(Exception):  # NOQA   make flake8 shut up
        """Dummy exception for when Requests is not installed."""
        pass

PARSERS = ['lxml', 'html5lib', 'html.parser']


def get_available_parsers():
    """Return a list of parsers that can be used."""
    available = []
    for p in PARSERS:
        try:
            bs4.BeautifulSoup("", p)
        except bs4.FeatureNotFound:
            # Try the next parser
            continue
        else:
            available.append(p)
    return available


def _get_resource(resource_url: str) -> (str, bytes):
    """Download or reads a file (online or local).

    Parameters:
        resource_url (str): URL or path of resource to load
    Returns:
        str, bytes: Tuple containing the resource's MIME type and its data.
    Raises:
        NameError: If an HTTP request was made and ``requests`` is not available.
        ValueError: If ``resource_url``'s protocol is invalid.
    """
    url_parsed = urlparse(resource_url)
    if url_parsed.scheme in ['http', 'https']:
        # Requests might not be installed
        if requests_get is not None:
            request = requests_get(resource_url)
            data = request.content
            if 'Content-Type' in request.headers:
                mimetype = request.headers['Content-Type']
            else:
                mimetype = mimetypes.guess_type(resource_url)
        else:
            raise NameError("HTTP URL found but requests not available")
    elif url_parsed.scheme == '':
        # '' is local file
        with open(resource_url, 'rb') as f:
            data = f.read()
        mimetype, _ = mimetypes.guess_type(resource_url)
    elif url_parsed.scheme == 'data':
        raise ValueError("Resource path is a data URI", url_parsed.scheme)
    else:
        raise ValueError("Not local path or HTTP/HTTPS URL", url_parsed.scheme)

    return mimetype, data


def make_data_uri(mimetype: str, data: bytes) -> str:
    """Convert data into an encoded data URI.

    Parameters:
        mimetype (str): String containing the MIME type of data (e.g.
            image/jpeg). If ``None``, will be treated as an empty string,
            equivalent in data URIs to ``text/plain``.
        data (bytes): Raw data to be encoded.
    Returns:
        str: Input data encoded into a data URI.
    """
    mimetype = '' if mimetype is None else mimetype
    if mimetype in ['', 'text/css', 'application/javascript']:
        # Text data can simply be URL-encoded
        encoded_data = quote(data.decode())
    else:
        mimetype = mimetype + ';base64'
        encoded_data = base64.b64encode(data).decode()
    return "data:{},{}".format(mimetype, encoded_data)


def convert_page(page_path: str, parser: str='auto',
                 callback: Callable[[str, str, str], None]=lambda *_: None,
                 ignore_errors: bool=False, ignore_images: bool=False,
                 ignore_css: bool=False, ignore_js: bool=False) -> str:
    """Take an HTML file or URL and outputs new HTML with resources as data URIs.

    Parameters:
        pageurl (str): URL or path of web page to convert.
    Keyword Arguments:
        parser (str): HTML Parser for Beautiful Soup 4 to use. See
            `BS4's docs. <http://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser>`_
            Default: 'auto' - Not an actual parser, but tells the library to
            automatically choose a parser.
        ignore_errors (bool): If ``True`` do not abort on unreadable resources.
            Unprocessable tags (e.g. broken links) will simply be skipped.
            Default: ``False``
        ignore_images (bool): If ``True`` do not process ``<img>`` tags.
            Default: ``False``
        ignore_css (bool): If ``True`` do not process ``<link>`` (stylesheet) tags.
            Default: ``False``
        ignore_js (bool): If ``True`` do not process ``<script>`` tags.
            Default: ``False``
        callback (function): Called before a new resource is processed. Takes
            three parameters: message type ('INFO' or 'ERROR'), a string with
            the category of the callback (usually the tag related to the
            message), and the message data (usually a string to be printed).
    Returns:
        str: The new webpage HTML.
    Raises:
        OSError: Error reading a file
        ValueError: Problem with a path/URL
        requests.exceptions.RequestException: Problem getting remote resource
        NameError: HTMLArk requires Requests to be installed to get resources
            from the web. This error is raised when an external URL is
            encountered.
    Examples:
        A very basic conversion of a local HTML file, using default settings:

        >>> convert_page("webpage.html")
        <Converted page HTML>

        However, that example will fail if there are any problems accessing
        linked resources in the HTML (e.g. a missing image). If you cannot
        verify the validity of links ahead of time (converting a downloaded
        web page, for example) you can disable failing on error:

        >>> convert_page("brokenpage.html", ignore_errors=True)
        <Converted page HTML, tags with broken links untouched>

        You can also skip processing of content types:

        >>> convert_page("webpage.html", ignore_images=True)
        <Converted page HTML, with <img> tags untouched>

        If you want to get feedback on the progress of the conversion, you can
        define a callback function. For example, a callback that prints all
        CSS-related errors to stdout (note that ignore_errors will bypass
        broken links but still report them to the callback):

        >>> def mycallback(message_type, message_category, message):
        ...     if message_type == 'ERROR' and message_category == 'link':
        ...         print(message)
        >>> convert_page("badcss.html", ignore_errors=True, callback=mycallback)
        <Converted page HTML, CSS links untouched, CSS errors printed to screen>
    """
    # Check features
    if requests_get is None:
        callback('INFO', 'feature', "Requests not available, web downloading disabled")

    # Get page HTML, whether from a server, a local file, or stdin
    if page_path is None:
        # Encoding is unknown, read as bytes (let bs4 handle decoding)
        page_text = sys.stdin.buffer.read()
    else:
        _, page_text = _get_resource(page_path)

    # Not all parsers are equal - it can be specified on the command line
    # so the user can try another when one fails
    if parser == 'auto':
        parser = get_available_parsers()[0]
    soup = bs4.BeautifulSoup(page_text, parser)
    callback('INFO', 'parser', "Using parser " + parser)

    tags = []

    # Gather all the relevant tags together
    if not ignore_images:
        tags += soup('img')
    if not ignore_css:
        csstags = soup('link')
        for css in csstags:
            if 'stylesheet' in css['rel']:
                tags.append(css)
    if not ignore_js:
        scripttags = soup('script')
        for script in scripttags:
            if 'src' in script.attrs:
                tags.append(script)

    # Convert the linked resources
    for tag in tags:
        tag_url = tag['href'] if tag.name == 'link' else tag['src']
        try:
            # BUG: doesn't work if using relative remote URLs in a local file
            fullpath = urljoin(page_path, tag_url)
            tag_mime, tag_data = _get_resource(fullpath)
        except RequestException:
            callback('ERROR', tag.name, "Can't access URL " + fullpath)
            if not ignore_errors:
                raise
        except OSError as e:
            callback('ERROR', tag.name, "Error reading '{}': {}".format(e.filename, e.strerror))
            if not ignore_errors:
                raise
        except ValueError as e:
            # Raised when a problem with the URL is found
            scheme = e.args[1]
            # Don't need to process things that are already data URIs
            if scheme == 'data':
                callback('INFO', tag.name, "Already data URI")
            else:
                # htmlark can only get from http/https and local files
                callback('ERROR', tag.name, "Unknown protocol in URL: " + tag_url)
                if not ignore_errors:
                    raise
        except NameError as e:
            # Requests module is not available
            callback('ERROR', tag.name, str(e))
            if not ignore_errors:
                raise
        else:
            encoded_resource = make_data_uri(tag_mime, tag_data)
            if tag.name == 'link':
                tag['href'] = encoded_resource
            else:
                tag['src'] = encoded_resource
            callback('INFO', tag.name, tag_url)
        # Record the original URL so the original HTML can be recovered
        tag.insert_after(bs4.Comment("URL:" + tag_url))

    soup.html.insert_after(bs4.Comment(
        "Generated by HTMLArk {}. Original URL {}".format(datetime.now(),
                                                          page_path)))
    return str(soup)


def _get_options():
    """Parse command line options."""
    parser = argparse.ArgumentParser(description="""
        Converts a webpage including external resources into a single HTML
        file. Note that resources loaded with JavaScript will not be handled
        by this program, it will only work properly with static pages.""")
    # Can't make this an argparse.FileType, because it could be a local path
    # or an URL, and convert_page needs the path
    parser.add_argument('webpage', nargs='?', default=None,
                        help="""URL or path of webpage to convert. If not
                        specified, read from STDIN.""")
    parser.add_argument('-o', '--output', default=sys.stdout,
                        type=argparse.FileType('w', encoding='UTF-8'),
                        help="File to write output. Defaults to STDOUT.")
    parser.add_argument('-E', '--ignore-errors', action='store_true', default=False,
                        help="Ignores unreadable resources")
    parser.add_argument('-I', '--ignore-images', action='store_true', default=False,
                        help="Ignores images during conversion")
    parser.add_argument('-C', '--ignore-css', action='store_true', default=False,
                        help="Ignores stylesheets during conversion")
    parser.add_argument('-J', '--ignore-js', action='store_true', default=False,
                        help="Ignores external JavaScript during conversion")
    parser.add_argument('-p', '--parser', default='auto',
                        choices=['html.parser', 'lxml', 'html5lib', 'auto'],
                        help="""Select HTML parser. Defaults to auto, which
                                tries to use lxml, html5lib, and html.parser
                                in that order. See documentation for more
                                information.""")
    parser.add_argument('--list-parsers', action='store_true', default=False,
                        help="Lists installed parsers available to HTMLArk")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="Prints information during conversion")
    parser.add_argument('-V', '--version', action='version',
                        version="HTMLArk v{}".format(__version__),
                        help="Displays version information")
    parsed = parser.parse_args()

    if parsed.list_parsers:
        """Print list of available parsers and exit."""
        print(", ".join(get_available_parsers()))
        sys.exit()

    return parsed


def _main():
    """Main function when called as a script."""
    options = _get_options()

    # All further messages should use print_verbose() or print_error()
    def print_error(m):
        print(m, file=sys.stderr)
    # print_error = lambda m: print(m, file=sys.stderr)
    if options.verbose:
        print_verbose = print_error
    else:
        def print_verbose(_):
            pass

    def info_callback(severity, message_type, message_data):
        """Display progress information during conversion."""
        if message_type == 'img':
            tagtype = "Image"
        elif message_type == 'link':
            tagtype = "CSS"
        elif message_type == 'script':
            tagtype = "JS"
        else:
            tagtype = message_type
        # Only display info messages if -v/--verbose flag is set
        if severity == 'INFO':
            if options.verbose:
                print_verbose("{}: {}".format(tagtype, message_data))
        elif severity == 'ERROR':
            print_error("{}: {}".format(tagtype, message_data))
        else:
            print_error("Unknown message level {}, please tell the author of the program".format(severity))
            print_error("{}: {}".format(tagtype, message_data))

    # Convert page
    if options.webpage is None:
        print_verbose("Reading from STDIN")
    else:
        print_verbose("Processing {}".format(options.webpage))

    try:
        newhtml = convert_page(options.webpage,
                               parser=options.parser,
                               ignore_errors=options.ignore_errors,
                               ignore_images=options.ignore_images,
                               ignore_css=options.ignore_css,
                               ignore_js=options.ignore_js,
                               callback=info_callback)
    except (OSError, RequestException, ValueError) as e:
        sys.exit("Unable to convert webpage: {}".format(e))
    except NameError:
        raise
        sys.exit("Cannot download web resource: Need Requests installed")

    # Write output
    try:
        options.output.write(newhtml)
    except OSError as e:
        # Note that argparse handles errors opening the file handle
        sys.exit("Unable to write to output file: {}".format(e.strerror))

    print_verbose("All done, output written to " + options.output.name)


def _main_wrapper():
    """Used as an entry point for pip's automatic script creation."""
    try:
        _main()
    except KeyboardInterrupt:
        sys.exit("\nCancelling webpage conversion")


if __name__ == "__main__":
    _main_wrapper()
