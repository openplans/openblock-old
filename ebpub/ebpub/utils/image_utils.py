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
Utilities for images, eg. rotating jpegs according to EXIF data.
"""

from PIL import Image
from PIL.ExifTags import TAGS

def get_exif_info(img):
    """
    Get EXIF information from a PIL.Image instance.
    Found this code at:
    http://wolfram.kriesing.de/blog/index.php/2006/reading-out-exif-data-via-python
    """
    result = {}
    try:
        info = img._getexif() or {}
    except AttributeError:
        info = {}
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        result[decoded] = value
    return result

def rotate_image_by_exif(img):
    """
    Rotate a PIL.Image instance according to its EXIF rotation information.

    Based on code from: http://stackoverflow.com/questions/1606587/how-to-use-pil-to-resize-and-apply-rotation-exif-information-to-the-file

    NOTE, this is a LOSSY transformation. Probably fine for our
    purposes.  We could use something like
    http://ebiznisz.hu/python-jpegtran/ if we change our minds about
    that.
    """
    exif_info = get_exif_info(img)
    # We rotate regarding to the EXIF orientation information
    orientation = exif_info.get('Orientation', 1)
    if orientation == 1:
        rotated = img
    elif orientation == 2:
        # Vertical Mirror
        rotated = img.transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation == 3:
        # Rotation 180
        rotated = img.transpose(Image.ROTATE_180)
    elif orientation == 4:
        # Horizontal Mirror
        rotated = img.transpose(Image.FLIP_TOP_BOTTOM)
    elif orientation == 5:
        # Horizontal Mirror + Rotation 270
        rotated = img.transpose(Image.FLIP_TOP_BOTTOM).transpose(
            Image.ROTATE_270)
    elif orientation == 6:
        # Rotation 270
        rotated = img.transpose(Image.ROTATE_270)
    elif orientation == 7:
        # Vertical Mirror + Rotation 270
        rotated = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(
            Image.ROTATE_270)
    elif orientation == 8:
        # Rotation 90
        rotated = img.transpose(Image.ROTATE_90)
    else:
        # unknown? do nothing.
        rotated = img

    return rotated

