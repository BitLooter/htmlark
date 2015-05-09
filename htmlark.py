#!/usr/bin/env python3

# Pack a webpage including images and CSS into a single HTML file.

import argparse
import requests
import base64
from urllib.parse import urljoin
from bs4 import BeautifulSoup

#TODO: Ignore files already data-URI encoded

def get_options():
    """Parses command line options"""
    parser = argparse.ArgumentParser(description="Converts a webpage including external resources into a single HTML file")
    parser.add_argument('webpage', help="URL or path of webpage to convert")
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

def convert_page(pageurl, parser, callback=lambda *_:None):
    """
    The part that does all the real work.

    Arguments:
    pageurl - URL or path of web page to convert.
    parser - Parser for Beautiful Soup 4 to use. See BS4's docs for more info.
    callback - Called before a new resource is processed. Takes a BS4 tag
        object and the full URL as parameters.

    Returns: String containing the new webpage HTML.
    """

    # Not all parsers are equal - if one skips resources, try another
    soup = BeautifulSoup(requests.get(pageurl).text, parser)
    imgtags = soup.find_all('img')
    for image in imgtags:
        url = urljoin(pageurl, image['src'])
        callback(image, url)
        imagerequest = requests.get(url)
        #TODO: If no Content-Type header (or local file) use mimetypes module
        image['src'] = make_data_uri(imagerequest.headers['Content-Type'],
                                     imagerequest.content)

    return str(soup)

def main():
    """Script's main function, used when called as a command-line program"""

    options = get_options()

    print("Processing {}".format(options.webpage))

    def info_callback(tag, url):
        """Displays progress information during conversion"""
        if tag.name == 'img':
            tagtype = "Image"
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

    newhtml = convert_page(options.webpage, options.parser, callback=info_callback)

    outfile = open('out.html', 'w')
    outfile.write(newhtml)
    outfile.close()
    print("All done, file written to " + "out.html")

if __name__ == "__main__":
    main()
