#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebpub
#
#   ebpub is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebpub is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebpub.  If not, see <http://www.gnu.org/licenses/>.
#

from django import template
import re

register = template.Library()

class FullLinksNode(template.Node):
    """
    Converts all <a href>s within {% full_links %} / {% end_full_links %} to
    use fully qualified URLs -- i.e., to start with 'http://'. Doesn't touch
    the ones that already start with 'http://'.
    """
    def __init__(self, nodelist, domain_var):
        self.nodelist = nodelist
        self.domain_var = template.Variable(domain_var)

    def render(self, context):
        domain = self.domain_var.resolve(context)
        output = self.nodelist.render(context)
        output = re.sub(r'(?i)(<a.*?\bhref=")/', r'\1http://%s/' % domain, output)
        return output

def do_full_links(parser, token):
    # {% full_links [domain] %} ... {% end_full_links %}
    args = token.contents.split()
    if len(args) != 2:
        raise template.TemplateSyntaxError("%r tag requires exactly one argument." % args[0])
    nodelist = parser.parse(('end_full_links',))
    parser.delete_first_token()
    return FullLinksNode(nodelist, args[1])
register.tag('full_links', do_full_links)
