# pylint: skip-file

"""Tests for logwrap.LogOnAccess with logger pick-up from module/instance."""

# Standard Library
import io
import logging
import unittest

# LogWrap Implementation
import logwrap


VALUE = "ok"
LOG = logging.getLogger("Target_mod")


class TestLogOnAccess(unittest.TestCase):
    def setUp(self):
        """Preparation for tests."""
        self.stream = io.StringIO()
        logging.getLogger().handlers.clear()
        logging.basicConfig(level=logging.DEBUG, stream=self.stream)

    def tearDown(self):
        """Revert modifications."""
        logging.getLogger().handlers.clear()
        self.stream.close()

    def test_01_logger(self):
        # noinspection PyMissingOrEmptyDocstring
        class Target:
            def __init__(tself, val=VALUE):
                tself.val = val

            def __repr__(tself):
                return f"{tself.__class__.__name__}(val={tself.val})"

            @logwrap.LogOnAccess
            def ok(tself):
                return tself.val

            @ok.setter
            def ok(tself, val):
                tself.val = val

            @ok.deleter
            def ok(tself):
                tself.val = ""

        target = Target()
        self.assertEqual(target.ok, VALUE)
        logged = self.stream.getvalue().splitlines()
        self.assertEqual(
            f"DEBUG:Target_mod:Request: Target(val=ok).ok",
            logged[0]
        )
        self.assertRegex(
            logged[1],
            rf"DEBUG:Target_mod:Done at (?:\d+\.\d{{3}})s: "
            rf"Target\(val=ok\)\.ok -> {logwrap.pretty_repr(VALUE)}"
        )
