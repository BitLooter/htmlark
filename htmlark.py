#!/usr/bin/env python3
"""Pack a webpage including images and CSS into a single HTML file, using data URIs."""

import argparse
import base64
import mimetypes
import sys
from urllib.parse import urljoin, urlparse

import bs4
import requests

VERSION = "0.9.dev1"
PARSERS = ['lxml', 'html5lib', 'html.parser']


def make_data_uri(mimetype, data):
    """Convert data into a base64-encoded data URI.

    Parameters:
        mimetype (str): String containing the MIME type of data (e.g.
            image/jpeg). If ``None``, will be treated as an empty string.
        data (str): Raw data to be encoded.
    Returns:
        str: Input data encoded into a data URI.
    """
    mimetype = '' if mimetype is None else mimetype
    encoded_data = base64.b64encode(data).decode()
    return "data:{};base64,{}".format(mimetype, encoded_data)


def get_resource(resource_url: str):
    """Download or reads a file (online or local).

    Parameters:
        resource_url (str): URL or path of resource to load
    Returns:
        str, str: Tuple containing the resource's data and its MIME type.
    Raises:
        ValueError: If ``resource_url``'s protocol is invalid.
    """
    url_parsed = urlparse(resource_url)
    if url_parsed.scheme in ['http', 'https']:
        request = requests.get(resource_url)
        data = request.content
        if 'Content-Type' in request.headers:
            mimetype = request.headers['Content-Type']
        else:
            mimetype = mimetypes.guess_type(resource_url)
    elif url_parsed.scheme == '':
        # '' is local file
        data = open(resource_url, 'rb').read()
        mimetype, _ = mimetypes.guess_type(resource_url)
    elif url_parsed.scheme == 'data':
        raise ValueError("Resource path is a data URI", url_parsed.scheme)
    else:
        raise ValueError("Not local path or HTTP/HTTPS URL", url_parsed.scheme)

    return data, mimetype


def convert_page(page_path, parser='auto', callback=lambda *_: None,
                 ignore_errors=False, ignore_images=False, ignore_css=False,
                 ignore_js=False):
    """Take an HTML file or URL and outputs new HTML with resources as data URIs.

    Parameters:
        pageurl (str): URL or path of web page to convert.
    Keyword Arguments:
        parser (str): HTML Parser for Beautiful Soup 4 to use. See
            `BS4's docs. <http://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser>`_
            Default: 'auto' - Not an actual parser, but tells the library to
            automatically choose a parser.
        ignore_errors (bool): If ``True`` do not abort on unreadable resources.
            Default: ``False``
        ignore_images (bool): If ``True`` do not process ``<img>`` tags.
            Default: ``False``
        ignore_css (bool): If ``True`` do not process ``<link>`` (stylesheet) tags.
            Default: ``False``
        ignore_js (bool): If ``True`` do not process ``<script>`` tags.
            Default: ``False``
        callback (function): Called before a new resource is processed. Takes
            three parameters: severity level ('INFO' or 'ERROR'), a string with
            the category of the callback (usually the tag related to the
            message), and the message data (usually a string to be printed).

    Returns:
        str: The new webpage HTML.
    """
    # Get page HTML, whether from a server, a local file, or stdin
    if page_path is None:
        # Encoding is unknown, read as bytes (let bs4 handle decoding)
        page_text = sys.stdin.buffer.read()
    else:
        page_text, _ = get_resource(page_path)

    # Not all parsers are equal - it can be specified on the command line
    # so the user can try another when one fails
    if parser == 'auto':
        for p in PARSERS:
            try:
                soup = bs4.BeautifulSoup(page_text, p)
            except bs4.FeatureNotFound as e:
                # Try the next parser
                continue
            # Parser found, don't try any more
            callback('INFO', 'parser', "Using parser " + p)
            break
    else:
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
            tag_data, tag_mime = get_resource(fullpath)
        except requests.exceptions.RequestException:
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
        else:
            encoded_resource = make_data_uri(tag_mime, tag_data)
            if tag.name == 'link':
                tag['href'] = encoded_resource
            else:
                tag['src'] = encoded_resource
            callback('INFO', tag.name, tag_url)

    return str(soup)


def get_options():
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
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="Prints information during conversion")
    parser.add_argument('-V', '--version', action='store_true', default=False,
                        help="Displays version information")
    return parser.parse_args()


def main():
    """Main function when called as a script."""
    options = get_options()

    # --version switch
    if options.version:
        print("HTMLArk v{}".format(VERSION))
        sys.exit(0)

    # All further messages use print_verbose() or print_error()
    print_error = lambda m: print(m, file=sys.stderr)
    if options.verbose:
        print_verbose = print_error
    else:
        print_verbose = lambda _: None

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
    except (OSError, requests.exceptions.RequestException, ValueError) as e:
        print_error("Unable to convert webpage: {}".format(e))
        sys.exit(1)

    # Write output
    try:
        options.output.write(newhtml)
    except OSError as e:
        # Note that argparse handles errors opening the file handle
        print_error("Unable to write to output file: {}".format(e.strerror))
        sys.exit(1)

    print_verbose("All done, output written to " + options.output.name)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelling webpage conversion", file=sys.stderr)
        sys.exit(1)
