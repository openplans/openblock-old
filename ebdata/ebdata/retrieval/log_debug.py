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
Import this file to send all 'eb.retrieval' messages (of any level, including
logger.DEBUG) to the console. This is convenient for debugging.
"""

from ebdata.retrieval import log
import logging

# Send all DEBUG (and above) messages to the console.
printer = logging.StreamHandler()
printer.setLevel(logging.DEBUG)
printer.setFormatter(logging.Formatter("%(levelname)s %(message)s"))

eb_root_logger = logging.getLogger('eb.retrieval')
eb_root_logger.setLevel(logging.DEBUG)
eb_root_logger.addHandler(printer)

# ... but don't log to console more than once, which happens if a
# parent logger is already set up with a StreamHandler.
_logger = eb_root_logger.parent
while _logger is not None:
    to_remove = []
    for handler in _logger.handlers:
        if isinstance(handler, logging.StreamHandler) \
                and handler.stream.name == '<stderr>':
            to_remove.append(handler)
    for handler in to_remove:
        _logger.removeHandler(handler)
    _logger = _logger.parent

# Remove the e-mail handler.
eb_root_logger.removeHandler(log.emailer)
