# htmlark
Pack a webpage including images and CSS into a single HTML file.

Through the magic of [data URIs](https://developer.mozilla.org/en-US/docs/Web/HTTP/data_URIs), `htmlark` can save these external dependancies inline right in the HTML. No more keeping around those "reallycoolwebpage_files" directories alongside the HTML files, everything is self-contained.

Note that this will only work with static pages. If an image or other resource is loaded with JavaScript, htmlark won't even know it exists.

## Requirements
Python 3 is required for htmlark. It was developed on 3.4, but will probably work on earlier versions.

Needs Beautiful Soup 4 installed. If you wish to use the lxml (recommended) or html5lib parsers, you will need to install the lxml and/or html5lib Python libraries as well.

## Usage
[Will document after the command line is worked out]

## License
htmlark is released under the MIT license, which may be found in the LICENSE file.