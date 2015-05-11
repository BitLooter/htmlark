#!/usr/bin/env python3

# Pack a webpage including images and CSS into a single HTML file.

import argparse
import requests
import base64
from urllib.parse import urlparse, urljoin
import mimetypes
from bs4 import BeautifulSoup

#TODO: Ignore files already data-URI encoded
#TODO: Read/write from/to stdin/stdout

def get_options():
    """Parses command line options"""
    parser = argparse.ArgumentParser(description="Converts a webpage including external resources into a single HTML file")
    parser.add_argument('webpage', help="URL or path of webpage to convert")
    parser.add_argument('--ignore-images', action='store_true', default=False,
                        help="Ignores images during conversion")
    parser.add_argument('--ignore-css', action='store_true', default=False,
                        help="Ignores stylesheets during conversion")
    parser.add_argument('--ignore-js', action='store_true', default=False,
                        help="Ignores Javascript during conversion")
    #TODO: Check for lxml/html5lib availability, use by default if exists
    parser.add_argument('-p', '--parser', default='html.parser',
                        choices=['html.parser', 'lxml', 'html5lib'],
                        help="Select HTML parser. See manual for details.")
    return parser.parse_args()

def make_data_uri(mimetype, data):
    """
    Converts data into a base64-encoded data URI.

    Arguments:
    mimetype - String containing the MIME type of data (e.g. image/jpeg)
    data - Raw data to be encoded.
    """
    encoded_data = base64.b64encode(data).decode()
    return "data:{};base64,{}".format(mimetype, encoded_data)

def encode_resource(resource_url):
    """Downloads and data-URI-encodes an external resource (online or local)"""
    content, mimetype = get_resource(resource_url, 'rb')
    mimetype = '' if mimetype == None else mimetype
    return make_data_uri(mimetype, content)

def get_resource(resource_url, mode):
    """
    Downloads or reads a file (online or local)

    Arguments:
    resource_url - URL or path of resource to load
    mode - Returns text string if 'r', or bytes if 'rb'
    """
    url_parsed = urlparse(resource_url)
    if url_parsed.scheme in ['http', 'https']:
        request = requests.get(resource_url)
        data = request.content if mode == 'rb' else request.text
        if 'Content-Type' in request.headers:
            mimetype = request.headers['Content-Type']
        else:
            mimetype = mimetypes.guess_type(resource_url)
    elif url_parsed.scheme == '':
        data = open(resource_url, mode).read()
        mimetype, _ = mimetypes.guess_type(resource_url)
    else:
        raise ValueError("Not local path or HTTP/HTTPS URL")

    return data, mimetype

def convert_page(page_path, parser, callback=lambda *_:None,
                 ignore_images=False, ignore_css=False, ignore_js=False):
    """
    The part that does all the real work.

    Arguments:
    pageurl - URL or path of web page to convert.
    parser - Parser for Beautiful Soup 4 to use. See BS4's docs for more info.
    ignore_images - If true do not process <img> tags
    ignore_css - If true do not process <link> (stylesheet) tags
    ignore_js - If true do not process <script> tags
    callback - Called before a new resource is processed. Takes a BS4 tag
        object as a parameter.

    Returns: String containing the new webpage HTML.
    """

    # Get page HTML, whether from a server or a local file
    page_text, _ = get_resource(page_path, 'r')

    # Not all parsers are equal - if one skips resources, try another
    soup = BeautifulSoup(page_text, parser)
    # Things to test for: tag case, attribute case, missing attributes,
    # duplicate attributes
    if not ignore_images:
        imgtags = soup('img')
        for image in imgtags:
            callback(image)
            image['src'] = encode_resource(urljoin(page_path, image['src']))
    if not ignore_css:
        csstags = soup('link')
        for css in csstags:
            # 'rel' can have multiple values and BS4 represents it as a list
            if 'stylesheet' in css['rel']:
                callback(css)
                css['href'] = encode_resource(urljoin(page_path, css['href']))
    if not ignore_js:
        scripttags = soup('script')
        for script in scripttags:
            if 'src' in script.attrs:
                callback(script)
                script['src'] = encode_resource(urljoin(page_path, script['src']))

    return str(soup)

def main():
    """Script's main function, used when called as a command-line program"""

    options = get_options()

    print("Processing {}".format(options.webpage))

    def info_callback(tag):
        """Displays progress information during conversion"""
        if tag.name == 'img':
            tagtype = "Image"
        elif tag.name == 'link':
            tagtype = "CSS"
        elif tag.name == 'script':
            tagtype = "JS"
        else:
            tagtype = tag.name

        if 'src' in tag.attrs:
            tagurl = tag['src']
        elif 'href' in tag.attrs:
            tagurl = tag['href']
        else:
            # If this code is used update function to use the URL from this tag
            tagurl = "<Unknown URL>"

        print("{}: {}".format(tagtype, tagurl))

    newhtml = convert_page(options.webpage, options.parser,
                           ignore_images=options.ignore_images,
                           ignore_css=options.ignore_css,
                           ignore_js=options.ignore_js,
                           callback=info_callback)

    outfile = open('out.html', 'w')
    outfile.write(newhtml)
    outfile.close()
    print("All done, file written to " + "out.html")

if __name__ == "__main__":
    main()
