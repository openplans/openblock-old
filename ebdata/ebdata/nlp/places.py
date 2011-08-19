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

import re
from ebpub.db.models import Location, LocationSynonym
from ebpub.streets.models import Place, PlaceSynonym


def loose_phrase_grabber(phrases):
    """
    phrase grabber that does not care about 
    existing tagging.
    """
    def grab_phrases(text):
        phrases.sort(key=len, reverse=True)

        tags = []
        def handle_match(m):
            tags.append((m.start(), m.end(), m.group()))
            return ' '*(m.end() - m.start())

        for phrase in phrases:
            # don't bother buiding and exhaustively searching unless
            # we at least weakly see this phrase in the text, 
            # re compiling and searching is not cheap added up 
            # over all locations.
            if phrase in text:
                text = re.sub(r'\b%s\b' % phrase, handle_match, text)

        tags.sort()
        return tags

    return grab_phrases

def paranoid_phrase_grabber(phrases, pre, post):
    """
    phrase grabber that tries not to tag inside of 
    existing pre/post tags.
    """
    
    def handle_match(m):
        return ' ' * len(m.group())
    nuke_tags = re.compile('%s.*?%s' % (re.escape(pre), re.escape(post)))
    loose_grabber = loose_phrase_grabber(phrases)
    
    def grab_phrases(text):
        text = nuke_tags.sub(handle_match, text)
        return loose_grabber(text)

    return grab_phrases

def phrase_tagger(phrases, pre='<span>', post='</span>', paranoid=True):
    
    if paranoid:
        grabber = paranoid_phrase_grabber(phrases, pre, post)
    else: 
        grabber = loose_phrase_grabber(phrases)

    def tag_phrases(text):
        out_text = []
        curpos = 0
        for tag in grabber(text):
            out_text += [text[curpos:tag[0]], pre, tag[2], post]
            curpos = tag[1]
        out_text.append(text[curpos:])
        return ''.join(out_text)

    return tag_phrases

def place_tagger(pre='<addr>', post='</addr>', paranoid=True):
    phrases = [p['pretty_name'] for p in Place.objects.filter(place_type__is_geocodable=True).values('pretty_name').order_by('-pretty_name')]
    synonyms = [m['pretty_name'] for m in PlaceSynonym.objects.values('pretty_name').order_by('-pretty_name')]
    return phrase_tagger(phrases + synonyms, pre, post, paranoid)

def location_tagger(pre='<addr>', post='</addr>', paranoid=True):
    location_qs = Location.objects.values('name').order_by('-name').exclude(location_type__slug__in=('boroughs', 'cities'))
    locations = [p['name'] for p in location_qs]
    synonyms = [m['pretty_name'] for m in LocationSynonym.objects.values('pretty_name').order_by('-pretty_name')]
    return phrase_tagger(locations + synonyms, pre, post, paranoid)

def place_grabber():
    phrases = [p['pretty_name'] for p in Place.objects.filter(place_type__is_geocodable=True).values('pretty_name').order_by('-pretty_name')]
    synonyms = [m['pretty_name'] for m in PlaceSynonym.objects.values('pretty_name').order_by('-pretty_name')]
    return loose_phrase_grabber(phrases + synonyms)

def location_grabber():
    location_qs = Location.objects.values('name').order_by('-name').exclude(location_type__slug__in=('boroughs', 'cities'))
    locations = [p['name'] for p in location_qs]
    synonyms = [m['pretty_name'] for m in LocationSynonym.objects.values('pretty_name').order_by('-pretty_name')]
    return loose_phrase_grabber(locations + synonyms)
