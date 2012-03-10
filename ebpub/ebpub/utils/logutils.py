#   Copyright 2011 OpenPlans and contributors
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


import logging
import warnings

def log_exception(msg='', level=logging.ERROR, logger=logging.getLogger()):
    """Log the most recent exception & traceback at the given level
    (default ERROR).

    Note this can be replaced by logger.exception(msg) or, if you want a
    level other than ERROR, you can do eg. logger.debug(msg, exc_info=True)
    """
    warnings.warn("logutils.log_exception is deprecated. You can use logging.exception() instead")
    logging.basicConfig()
    logger.log(level=level, msg=msg, exc_info=True)
