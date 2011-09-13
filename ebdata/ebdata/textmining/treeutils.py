#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebdata
#
#   ebdata is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebdata is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebdata.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Common utilities for creating and cleaning lxml HTML trees.
"""

from lxml.etree import ElementTree, Element
from lxml.html import document_fromstring
import lxml.html.soupparser
import re
from ebdata.retrieval.utils import convert_entities
from BeautifulSoup import UnicodeDammit

def make_tree(html):
    """
    Returns an lxml tree for the given HTML string (either Unicode or
    bytestring).

    This is better than lxml.html.document_fromstring because this takes care
    of a few known issues.
    """
    # Normalize newlines. Otherwise, "\r" gets converted to an HTML entity
    # by lxml.
    html = re.sub('\r\n', '\n', html)

    # Remove <?xml> declaration in Unicode objects, because it causes an error:
    # "ValueError: Unicode strings with encoding declaration are not supported."
    # Note that the error only occurs if the <?xml> tag has an "encoding"
    # attribute, but we remove it in all cases, as there's no downside to
    # removing it.
    if isinstance(html, unicode):
        html = re.sub(r'^\s*<\?xml\s+.*?\?>', '', html)
    else:
        html = UnicodeDammit(html, isHTML=True).unicode
    html = html.strip()
    if html:
        try:
            return document_fromstring(html)
        except:
            # Fall back to using the (slow) BeautifulSoup parser.
            return lxml.html.soupparser.fromstring(html)
    else:
        root = Element('body')
        root.text = u''
        return ElementTree(root)


def make_tree_and_preprocess(html, *args, **kw):
    """
    Returns an lxml tree for the given HTML string (either Unicode or
    bytestring). Also preprocesses the HTML to remove data that isn't relevant
    to text mining (see the docstring for preprocess()).

    Extra args are passed to preprocess().
    """
    tree = make_tree(html)
    result = preprocess(tree, *args, **kw)
    return result

def preprocess_to_string(*args, **kw):
    """
    like make_tree_and_preprocess() but returns a string.
    """
    tree = make_tree_and_preprocess(*args, **kw)
    text = tree.findtext('body') or u''
    return text.strip()

def preprocess(tree, drop_tags=(), drop_trees=(), drop_attrs=()):
    """
    Preprocesses a HTML etree to remove data that isn't relevant to text mining.
    The tree is edited in place, but it's also the return value, for
    convenience.

    Specifically, this does the following:
        * Removes all comments and their contents.
        * Removes these tags and their contents:
            <style>, <link>, <meta>, <script>, <noscript>, plus all of drop_trees.
        * For all tags in drop_tags, removes the tags (but keeps the contents).
        * Removes all namespaced attributes in all elements.
    """
    tags_to_drop = set(drop_tags)
    trees_to_drop = set(['style', 'link', 'meta', 'script', 'noscript'])
    for tag in drop_trees:
        trees_to_drop.add(tag)

    elements_to_drop = []
    for element in tree.getiterator():
        if element.tag in tags_to_drop or not isinstance(element.tag, basestring): # If it's a comment...
            element.drop_tag()
        elif element.tag in trees_to_drop:
            elements_to_drop.append(element)
        for attname in element.attrib.keys():
            if ':' in attname or attname in drop_attrs:
                del element.attrib[attname]
    for e in elements_to_drop:
        e.drop_tree()
    return tree


def text_from_html(html):
    """Remove ALL tags and return all plain text.
    """
    text = preprocess_to_string(html, drop_tags=_html_droptags,
                                drop_trees=_html_droptrees)
    if not text:
        # Maybe there was something there but not really HTML.
        if text and not isinstance(text, unicode):
            text = UnicodeDammit(html, isHTML=False).unicode.strip()
        else:
            text = u''
    text = convert_entities(text)
    return text


# Note we leave body and html in because the code expects those.
_html_droptags = [
    'a',
    'abbr',
    'acronym',
    'address',
    'applet',
    'area',
    'b',
    'base',
    'basefont',
    'bdo',
    'big',
    'blockquote',
#    'body',
    'br',
    'button',
    'caption',
    'center',
    'cite',
    'code',
    'col',
    'colgroup',
    'dd',
    'del',
    'dfn',
    'dir',
    'div',
    'dl',
    'dt',
    'em',
    'fieldset',
    'font',
    'form',
    'frame',
    'frameset',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'hr',
#    'html',
    'i',
    'iframe',
    'img',
    'input',
    'ins',
    'kbd',
    'label',
    'legend',
    'li',
    'link',
    'map',
    'menu',
    'noframes',
    'noscript',
    'object',
    'ol',
    'optgroup',
    'option',
    'p',
    'param',
    'pre',
    'q',
    's',
    'samp',
    'select',
    'small',
    'span',
    'strike',
    'strong',
    'sub',
    'sup',
    'table',
    'tbody',
    'td',
    'textarea',
    'tfoot',
    'th',
    'thead',
    'tr',
    'tt',
    'u',
    'ul',
    'var']

_html_droptrees = [
    'head',
    'script',
    'style',
    'title',
    'meta',
 ]
