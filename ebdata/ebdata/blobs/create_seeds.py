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

from ebdata.blobs.models import Seed
from ebpub.db.models import Schema

def create_rss_seed(url, base_url, rss_full_entry, pretty_name, guess_article_text=True, strip_noise=False):
    if rss_full_entry:
        guess_article_text = strip_noise = False
    if 'www.' in base_url:
        normalize_www = 2
    else:
        normalize_www = 1
    Seed.objects.create(
        url=url,
        base_url=base_url,
        delay=3,
        depth=1,
        is_crawled=False,
        is_rss_feed=True,
        is_active=True,
        rss_full_entry=rss_full_entry,
        normalize_www=normalize_www,
        pretty_name=pretty_name,
        schema=Schema.objects.get(slug='news-articles'),
        autodetect_locations=True,
        guess_article_text=guess_article_text,
        strip_noise=strip_noise,
        city='',
    )
