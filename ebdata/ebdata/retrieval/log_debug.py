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
