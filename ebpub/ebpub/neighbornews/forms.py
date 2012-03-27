#   Copyright 2011 OpenPlans, and contributors
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

"""
Forms for adding & editing :ref:`user_content`

"""
from django import forms
from django.conf import settings
from ebpub.db.forms import NewsItemForm as NewsItemFormBase
from ebpub.db.models import NewsItem
from recaptcha.client import captcha
from ebpub.db.fields import OpenblockImageFormField
import logging
logger = logging.getLogger('neighbornews.forms')

class NewsItemForm(NewsItemFormBase):

    need_captcha = False
    recaptcha_ip = None

    image = OpenblockImageFormField(required=False, label="Upload image")

    def _clean_captcha(self):
        if self.need_captcha and \
                getattr(settings, 'RECAPTCHA_PRIVATE_KEY', None) and \
                getattr(settings, 'RECAPTCHA_PUBLIC_KEY', None):
            challenge_field = self.data.get('recaptcha_challenge_field')
            response_field = self.data.get('recaptcha_response_field')
            client = self.recaptcha_ip  # Must be set by our view code.
            check_captcha = captcha.submit(
                challenge_field, response_field,
                settings.RECAPTCHA_PRIVATE_KEY, client)

            if check_captcha.is_valid is False:
                self.errors['recaptcha'] = 'Invalid captcha value'

    def clean(self):
        self._clean_captcha()
        cleaned_data = super(NewsItemForm, self).clean()
        # Reverse-geocode if we need to - eg. user clicked map
        # but didn't give an address.
        if not cleaned_data.get('location_name'):
            if cleaned_data.get('location'):
                from ebpub.geocoder.reverse import reverse_geocode
                from ebpub.geocoder.reverse import ReverseGeocodeError
                try:
                    block, distance = reverse_geocode(cleaned_data['location'])
                    cleaned_data['location_name'] = block.pretty_name
                except ReverseGeocodeError:
                    logger.info("Saving NewsItem with no location_name because reverse-geocoding %(location)s failed" % cleaned_data)

        # Geocode if we can, and need to.
        # Should not be necessary, but this is groundwork for #284.
        if not cleaned_data.get('location'):
            if cleaned_data.get('location_name'):
                from ebpub.geocoder.base import full_geocode
                try:
                    geocoded = full_geocode(cleaned_data['location_name'].strip(),
                                            guess=True)
                    cleaned_data['location'] = geocoded['result'].location.wkt
                except (IndexError, KeyError, AttributeError):
                    logger.info("Saving NewsItem with no location because geocoding %(location_name)s failed" % cleaned_data)

        # Note, any NewsItem fields that aren't listed in self._meta.fields
        # have to be manually saved here, because that's the list that's
        # normally consulted when setting attributes on the instance.
        # ... And yes, clean() is normally responsible for setting
        # attributes on the bound instance.
        for key in forms.fields_for_model(self._meta.model):
            if key in cleaned_data.keys():
                setattr(self.instance, key, cleaned_data[key])

        return cleaned_data

class NeighborMessageForm(NewsItemForm):

    class Meta:
        model = NewsItem
        # Hide some fields, re-order others.
        fields = ('title', 'location_name', 'url',
                  'image',
                  'image_url', 'categories',
                  'description',
                  'location',
                  )

    location_name = forms.CharField(max_length=255, label="Address or Location",
                                    help_text=u"Or click the map.",
                                    required=False)
    image_url = forms.CharField(max_length=2048, label="Link to external image",
                                required=False)
    categories = forms.CharField(max_length=10240, required=False,
                                 help_text="Separate with commas")
    location = forms.CharField(max_length=255, widget=forms.HiddenInput)


class NeighborEventForm(NeighborMessageForm):

    class Meta:
        model = NewsItem
        # Hide some fields, re-order others.
        fields = ('title', 'location_name',
                  'item_date',
                  'start_time', 'end_time',
                  'url', 'image', 'image_url',
                  'categories',
                  'description',
                  )

    item_date = forms.DateField(label="Date")
    start_time = forms.TimeField(label="Start Time", required=False,
                                 input_formats=("%I:%M%p",))
    end_time = forms.TimeField(label="End Time", required=False,
                               input_formats=("%I:%M%p",))
