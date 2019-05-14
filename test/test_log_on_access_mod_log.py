# pylint: skip-file

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
        self.stream = io.StringIO()
        logging.getLogger().handlers.clear()
        logging.basicConfig(level=logging.DEBUG, stream=self.stream)

    def tearDown(self):
        logging.getLogger().handlers.clear()
        self.stream.close()

    def test_01_logger(self):
        class Target:
            def __init__(tself, val=VALUE):
                tself.val = val

            def __repr__(tself):
                return "{cls}(val={tself.val})".format(cls=tself.__class__.__name__, tself=tself)

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
            "DEBUG:Target_mod:Request: Target(val=ok).ok",
            logged[0]
        )
        self.assertRegex(
            logged[1],
            r"DEBUG:Target_mod:Done at (?:\d+\.\d{{3}})s: "
            r"Target\(val=ok\)\.ok -> {pr_val}".format(pr_val=logwrap.pretty_repr(VALUE))
        )
