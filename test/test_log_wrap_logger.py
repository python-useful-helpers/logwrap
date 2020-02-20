"""LogWrap tests with logger instance pick-up from module."""

# Standard Library
import io
import logging
import unittest

# LogWrap Implementation
import logwrap


LOGGER = logging.getLogger(__name__)


# noinspection PyUnusedLocal,PyMissingOrEmptyDocstring
class TestLogWrapLoggerInTargetModule(unittest.TestCase):
    def setUp(self):
        """Preparation for tests.

        Due to no possibility of proper mock patch of function defaults, modify directly.
        """
        self.logger = LOGGER
        self.logger.setLevel(logging.DEBUG)

        self.stream = io.StringIO()

        self.logger.handlers.clear()
        handler = logging.StreamHandler(self.stream)
        handler.setFormatter(logging.Formatter(fmt='%(levelname)s>%(message)s'))
        self.logger.addHandler(handler)

    def tearDown(self):
        """Revert modifications."""
        self.logger.handlers.clear()

    def test_001_simple(self):
        @logwrap.logwrap
        def func():
            return 'No args'

        result = func()
        self.assertEqual(result, 'No args')

        self.assertEqual(
            f"DEBUG>Calling: \n"
            f"func()\n"
            f"DEBUG>Done: 'func' with result:\n"
            f"{logwrap.pretty_repr(result)}\n",
            self.stream.getvalue(),
        )

    def test_002_logger_no_prefetch(self):
        @logwrap.logwrap()
        def func():
            return 'No args'

        result = func()
        self.assertEqual(result, 'No args')

        self.assertEqual(
            f"DEBUG>Calling: \n"
            f"func()\n"
            f"DEBUG>Done: 'func' with result:\n"
            f"{logwrap.pretty_repr(result)}\n",
            self.stream.getvalue(),
        )
