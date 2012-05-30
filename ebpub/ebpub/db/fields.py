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
Custom Fields for OpenBlock models.

"""
from django.conf import settings

from easy_thumbnails.fields import ThumbnailerImageField
class OpenblockImageField(ThumbnailerImageField):
    """
    A model Field based on ThumbnailerImageField that makes sure we
    save a correct *relative* filename.

    Uses :py:class:`OpenblockImageFormField` as its formfield.
    """
    def generate_filename(self, instance, name):
        # Save it as relative, not absolute, because absolute paths in
        # the db are A) foolishly not portable and B) too long.
        path = super(OpenblockImageField, self).generate_filename(instance, name)
        if path.startswith(settings.MEDIA_ROOT):
            path = path[len(settings.MEDIA_ROOT) + 1:]
        return path

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', OpenblockImageFormField)
        return super(OpenblockImageField, self).formfield(**kwargs)

from django.forms.fields import ImageField
class OpenblockImageFormField(ImageField):
    """
    A version of ImageField that fixes EXIF rotation on upload, so
    eg. mobile phone photos will have the correct orientation.
    """
    def to_python(self, value):
        """
        Fixes rotation if needed.
        """
        image = super(OpenblockImageFormField, self).to_python(value)
        if not image:
            return image
        from ebpub.utils.image_utils import rotate_image_by_exif
        from PIL import Image
        pil_img = Image.open(image)
        rotated = rotate_image_by_exif(pil_img)
        if not (rotated is pil_img):
            image.seek(0)
            rotated.save(image)
        return image


