HTMLArk
=======

.. image:: https://img.shields.io/github/downloads/BitLooter/htmlark/total.svg
        :target: https://github.com/BitLooter/htmlark
.. image:: https://img.shields.io/pypi/v/HTMLArk.svg
        :target: https://github.com/BitLooter/htmlark
.. image:: https://img.shields.io/pypi/l/HTMLArk.svg
        :target: https://github.com/BitLooter/htmlark

Embed images, CSS, and JavaScript into an HTML file. Through the magic of `data URIs <https://developer.mozilla.org/en-US/docs/Web/HTTP/data_URIs>`_, ``htmlark`` can save these external dependencies inline right in the HTML. No more keeping around those "reallycoolwebpage_files" directories alongside the HTML files, everything is self-contained.

Note that this will only work with static pages. If an image or other resource is loaded with JavaScript, HTMLArk won't even know it exists.

Installation and Requirements
-----------------------------
Python 3.5 or greater is required for HTMLArk.

Install HTMLArk with ``pip`` like so:

.. code-block:: bash

    pip install htmlark

To use the `lxml <http://lxml.de/>`_ (recommended) or `html5lib <https://github.com/html5lib/html5lib-python>`_ parsers, you will need to install the lxml and/or html5lib Python libraries as well. HTMLArk can also get resources from the web, to enable this functionality you need `Requests <http://python-requests.org/`_ installed. You can install HTMLArk with all optional dependencies with this command:

.. code-block:: bash

    pip install htmlark[http,parsers]


If you want to install it manually, the only hard dependency HTMLArk has is `Beautiful Soup 4 <http://www.crummy.com/software/BeautifulSoup/>`_.


Command-line usage
------------------
You can also get this information with ``htmlark --help``.

Details::

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

    def convert_page(page_path, parser='auto', callback=lambda *_: None,
                     ignore_errors=False, ignore_images=False, ignore_css=False,
                     ignore_js=False):

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


License
-------
HTMLArk is released under the MIT license, which may be found in the LICENSE file.
