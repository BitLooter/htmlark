HTMLArk
=======

.. image:: https://img.shields.io/github/downloads/BitLooter/htmlark/total.svg
        :target: https://github.com/BitLooter/htmlark
.. image:: https://img.shields.io/pypi/v/HTMLArk.svg
        :target: https://pypi.python.org/pypi/HTMLArk
.. image:: https://img.shields.io/pypi/l/HTMLArk.svg
        :target: https://raw.githubusercontent.com/BitLooter/htmlark/master/LICENSE.txt

Embed images, CSS, and JavaScript into an HTML file. Through the magic of `data URIs <https://developer.mozilla.org/en-US/docs/Web/HTTP/data_URIs>`_, HTMLArk can save these external dependencies inline right in the HTML. No more keeping around those "reallycoolwebpage_files" directories alongside the HTML files, everything is self-contained.

Note that this will only work with static pages. If an image or other resource is loaded with JavaScript, HTMLArk won't even know it exists.

Installation and Requirements
-----------------------------
Python 3.5 or greater is required for HTMLArk.

Install HTMLArk with ``pip`` like so:

.. code-block:: bash

    pip install htmlark

To use the `lxml <http://lxml.de/>`_ (recommended) or `html5lib <https://github.com/html5lib/html5lib-python>`_ parsers, you will need to install the lxml and/or html5lib Python libraries as well. HTMLArk can also get resources from the web, to enable this functionality you need `Requests <http://python-requests.org/>`_ installed. You can install HTMLArk with all optional dependencies with this command:

.. code-block:: bash

    pip install htmlark[http,parsers]


If you want to install it manually, the only hard dependency HTMLArk has is `Beautiful Soup 4 <http://www.crummy.com/software/BeautifulSoup/>`_.


Command-line usage
------------------
You can also get this information with ``htmlark --help``.

::

    usage: htmlark [-h] [-o OUTPUT] [-E] [-I] [-C] [-J]
                   [-p {html.parser,lxml,html5lib,auto}] [-v] [--version]
                   [webpage]

    Converts a webpage including external resources into a single HTML file. Note
    that resources loaded with JavaScript will not be handled by this program, it
    will only work properly with static pages.

    positional arguments:
      webpage               URL or path of webpage to convert. If not specified,
                            read from STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            File to write output. Defaults to STDOUT.
      -E, --ignore-errors   Ignores unreadable resources
      -I, --ignore-images   Ignores images during conversion
      -C, --ignore-css      Ignores stylesheets during conversion
      -J, --ignore-js       Ignores external JavaScript during conversion
      -p {html.parser,lxml,html5lib,auto}, --parser {html.parser,lxml,html5lib,auto}
                            Select HTML parser. If not specifed, htmlark tries to
                            use lxml, html5lib, and html.parser in that order (the
                            'auto' option). See documentation for more
                            information.
      -v, --verbose         Prints information during conversion
      --version             Displays version information


Using HTMLArk as a module
-------------------------
You can also integrate HTMLArk into your own scripts, by importing it and calling ``convert_page``. Example:

.. code-block:: python

    import htmlark
    packed_html = htmlark.convert_page("samplepage.html", ignore_errors=True)

Details::

    def convert_page(page_path: str, parser: str='auto',
                     callback: Callable[[str, str, str], None]=lambda *_: None,
                     ignore_errors: bool=False, ignore_images: bool=False,
                     ignore_css: bool=False, ignore_js: bool=False) -> str

        Take an HTML file or URL and outputs new HTML with resources as data URIs.

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


Compatibility
-------------
Data URIs have been supported by every major browser for many years now. The only browser that might cause problems is Internet Explorer (surprise!). IE7 and below have no support for data URIs, but IE8 and above support them for CSS and images. As far as I know no version of IE allows you to load JavaScript from a data URI, though it is supported in Edge.

See `Can I Use's page on data URIs <http://caniuse.com/#feat=datauri>`_ for more compatibility information.

License
-------
HTMLArk is released under the MIT license, which may be found in the LICENSE file.
