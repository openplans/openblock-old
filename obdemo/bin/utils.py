# TODO: maybe we need an 'oblib.utils' or some such

import logging
import traceback

def log_exception(level=logging.ERROR):
    """Log the most recent exception & traceback
    at the given level (default ERROR).
    """
    logging.basicConfig()
    msg = traceback.format_exc()
    logging.getLogger().log(level=level, msg=msg)

