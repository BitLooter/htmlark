#!/usr/bin/env python3

# Pack a webpage including images and CSS into a single HTML file.

import sys
import requests
import base64
from urllib.parse import urljoin
from bs4 import BeautifulSoup

#TODO: Properly parse command line
#TODO: Ignore files already data-URI encoded

def main():
    pageurl = sys.argv[1]
    print("Processing {}".format(pageurl))

    # Default parser skips some images on some pages
    # TODO: Command-line option to select parser
    soup = BeautifulSoup(requests.get(pageurl).text, "html.parser")
    imgtags = soup.find_all('img')
    for image in imgtags:
        print("Image found: " + image['src'])
        url = urljoin(pageurl, image['src'])
        imagerequest = requests.get(url)
        imageencoded = base64.b64encode(imagerequest.content).decode()
        #TODO: If no Content-Type header (or local file) use mimetypes module
        imagetype = imagerequest.headers['Content-Type']
        image['src'] = "data:{};base64,{}".format(imagetype, imageencoded)

    # Conversion complete, write output and cleanup
    outfile = open('out.html', 'w')
    outfile.write(str(soup))
    outfile.close()
    print("All done, file written to " + "out.html")

if __name__ == "__main__":
    main()
