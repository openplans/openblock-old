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
A FileUploadHandler that stops the upload if it's too big.

Code originally copied from FixCity.
"""

from django.core.files.uploadhandler import FileUploadHandler, StopUpload

class QuotaExceededError(StopUpload):
    # Unfortunately this does stop the upload but does seem to let the
    # request complete with a 200 response, weirdly.
    pass

class QuotaUploadHandler(FileUploadHandler):
    """
    This upload handler terminates the connection if a file larger than
    the specified quota is uploaded.
    """

    def __init__(self, request=None):
        super(QuotaUploadHandler, self).__init__(request)
        self.total_upload = 0
        from django.conf import settings
        self.quota_mb = getattr(settings, 'UPLOAD_MAX_MB', 5.0)
        self.quota = self.quota_mb * 1024 * 1024
        self._aborted = False


    def _abort(self):
        self._aborted = True
        raise QuotaExceededError('Maximum upload size is %.2f MB'
                                 % self.quota_mb)

    def receive_data_chunk(self, raw_data, start):
        # First check the content-length header, if provided.
        if self.request:
            content_length = self.request.META.get('CONTENT_LENGTH', None)
            if content_length is not None:
                content_length = int(content_length)
                if content_length >= self.quota:
                    return self._abort()
        # Content-length might not be provided, or might be a lie, so
        # we also have to keep track.
        self.total_upload += len(raw_data)
        if self.total_upload >= self.quota:
            return self._abort()
        # Delegate to the next handler.
        return raw_data

    def upload_complete(self):
        if self._aborted:
            return 1
        return None

    def file_complete(self, file_size):
        return None
