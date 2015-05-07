#!/usr/bin/env python3

# Pack a webpage including images and CSS into a single HTML file.

import sys
import requests
import base64
from urllib.parse import urljoin
from bs4 import BeautifulSoup

#TODO: Properly parse command line

pageurl = sys.argv[1]
print("Processing {}".format(pageurl))

soup = BeautifulSoup(requests.get(pageurl).text)
imgtags = soup.find_all('img')
for image in imgtags:
    print("Image found: " + image['src'])
    url = urljoin(pageurl, image['src'])
    imagecontent = requests.get(url).content
    imageencoded = base64.b64encode(imagecontent).decode()
    image['src'] = "data:image/jpeg;base64," + imageencoded

# Conversion complete, write output and cleanup
outfile = open('out.html', 'w')
outfile.write(str(soup))
outfile.close()
print("All done, file written to " + "out.html")
