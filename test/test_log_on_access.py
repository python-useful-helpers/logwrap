# pylint: skip-file

"""Tests for logwrap.LogOnAccess."""

import io
import logging
import unittest

import logwrap

VALUE = "ok"


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

    def test_01_positive(self):
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
        self.assertEqual("DEBUG:logwrap.log_on_access:Request: Target(val=ok).ok", logged[0])
        self.assertRegex(
            logged[1],
            rf"DEBUG:logwrap\.log_on_access:Done at (?:\d+\.\d{{3}})s: "
            rf"Target\(val=ok\)\.ok -> {logwrap.pretty_repr(VALUE)}",
        )

        self.stream.seek(0)
        self.stream.truncate()

        target.ok = VALUE.upper()
        logged = self.stream.getvalue().splitlines()
        self.assertEqual(
            f"DEBUG:logwrap.log_on_access:Request: Target(val=ok).ok = {logwrap.pretty_repr(VALUE.upper())}",
            logged[0],
        )
        self.assertRegex(
            logged[1],
            rf"DEBUG:logwrap\.log_on_access:Done at (?:\d+\.\d{{3}})s: "
            rf"Target\(val=ok\)\.ok = {logwrap.pretty_repr(VALUE.upper())}",
        )

        self.assertEqual(target.ok, VALUE.upper())

        self.stream.seek(0)
        self.stream.truncate()

        del target.ok
        logged = self.stream.getvalue().splitlines()
        self.assertEqual("DEBUG:logwrap.log_on_access:Request: del Target(val=OK).ok", logged[0])
        self.assertRegex(
            logged[1],
            r"DEBUG:logwrap\.log_on_access:Done at (?:\d+\.\d{3})s: del Target\(val=OK\)\.ok",
        )

    def test_02_positive_properties(self):
        # noinspection PyMissingOrEmptyDocstring
        class Target:
            def __init__(tself, val=VALUE):
                tself.val = val

            def __repr__(tself):
                return f"{tself.__class__.__name__}(val={tself.val})"

            @logwrap.LogOnAccess
            def ok(tself):
                return tself.val

            ok.log_level = logging.INFO
            ok.log_object_repr = False
            ok.override_name = "override"

        target = Target()

        self.assertEqual(target.ok, VALUE)
        logged = self.stream.getvalue().splitlines()
        self.assertEqual(
            f"INFO:logwrap.log_on_access:Request: <Target() at 0x{id(target):X}>.override",
            logged[0],
        )
        self.assertRegex(
            logged[1],
            rf"INFO:logwrap\.log_on_access:Done at (?:\d+\.\d{{3}})s: "
            rf"<Target\(\) at 0x{id(target):X}>\.override -> {logwrap.pretty_repr(VALUE)}",
        )

    def test_03_positive_no_log(self):
        # noinspection PyMissingOrEmptyDocstring
        class Target:
            def __init__(tself, val=VALUE):
                tself.val = val

            def __repr__(tself):
                return f"{tself.__class__.__name__}(val={tself.val})"

            @logwrap.LogOnAccess
            def ok(tself):
                return tself.val

            ok.log_success = False
            ok.log_before = False

        target = Target()

        self.assertEqual(target.ok, VALUE)
        self.assertEqual(self.stream.getvalue(), "")

    def test_04_negative(self):
        # noinspection PyMissingOrEmptyDocstring
        class Target:
            def __repr__(tself):
                return f"{tself.__class__.__name__}()"

            @logwrap.LogOnAccess
            def ok(tself):
                raise AttributeError()

            @ok.setter
            def ok(tself, val):
                raise ValueError(val)

            @ok.deleter
            def ok(tself):
                raise RuntimeError()

        target = Target()

        with self.assertRaises(AttributeError):
            self.assertIsNone(target.ok)

        logged = self.stream.getvalue().splitlines()
        self.assertEqual("DEBUG:logwrap.log_on_access:Request: Target().ok", logged[0])
        self.assertRegex(
            logged[1],
            r"DEBUG:logwrap\.log_on_access:Failed after (?:\d+\.\d{3})s: Target\(\)\.ok",
        )
        self.assertEqual("Traceback (most recent call last):", logged[2])

        self.stream.seek(0)
        self.stream.truncate()

        with self.assertRaises(ValueError):
            target.ok = VALUE

        logged = self.stream.getvalue().splitlines()
        self.assertEqual(
            f"DEBUG:logwrap.log_on_access:Request: Target().ok = {logwrap.pretty_repr(VALUE)}",
            logged[0],
        )
        self.assertRegex(
            logged[1],
            rf"DEBUG:logwrap\.log_on_access:Failed after (?:\d+\.\d{{3}})s: "
            rf"Target\(\)\.ok = {logwrap.pretty_repr(VALUE)}",
        )
        self.assertEqual("Traceback (most recent call last):", logged[2])

        self.stream.seek(0)
        self.stream.truncate()

        with self.assertRaises(RuntimeError):
            del target.ok

        logged = self.stream.getvalue().splitlines()
        self.assertEqual("DEBUG:logwrap.log_on_access:Request: del Target().ok", logged[0])
        self.assertRegex(
            logged[1],
            r"DEBUG:logwrap\.log_on_access:Failed after (?:\d+\.\d{3})s: del Target\(\)\.ok",
        )
        self.assertEqual("Traceback (most recent call last):", logged[2])

    def test_05_negative_properties(self):
        # noinspection PyMissingOrEmptyDocstring
        class Target:
            def __init__(tself, val=VALUE):
                tself.val = val

            def __repr__(tself):
                return f"{tself.__class__.__name__}(val={tself.val})"

            @logwrap.LogOnAccess
            def ok(tself):
                raise AttributeError()

            ok.exc_level = logging.ERROR
            ok.log_traceback = False
            ok.log_object_repr = False
            ok.override_name = "override"

        target = Target()

        with self.assertRaises(AttributeError):
            self.assertIsNone(target.ok)

        logged = self.stream.getvalue().splitlines()
        self.assertEqual(
            f"DEBUG:logwrap.log_on_access:Request: <Target() at 0x{id(target):X}>.override",
            logged[0],
        )
        self.assertRegex(
            logged[1],
            rf"ERROR:logwrap\.log_on_access:Failed after (?:\d+\.\d{{3}})s: <Target\(\) at 0x{id(target):X}>\.override",
        )

        self.assertEqual(len(logged), 2)

    def test_06_negative_no_log(self):
        # noinspection PyMissingOrEmptyDocstring
        class Target:
            def __init__(tself, val=VALUE):
                tself.val = val

            def __repr__(tself):
                return f"{tself.__class__.__name__}(val={tself.val})"

            @logwrap.LogOnAccess
            def ok(tself):
                raise AttributeError()

            ok.log_failure = False
            ok.log_before = False

        target = Target()

        with self.assertRaises(AttributeError):
            self.assertIsNone(target.ok)

        self.assertEqual(self.stream.getvalue(), "")

    def test_07_property_mimic(self):
        # noinspection PyMissingOrEmptyDocstring
        class Target:
            def __repr__(tself):
                return f"{tself.__class__.__name__}()"

            empty = logwrap.LogOnAccess(doc="empty_property")

        target = Target()

        with self.assertRaises(AttributeError):
            self.assertIsNone(target.empty)

        with self.assertRaises(AttributeError):
            target.empty = None

        with self.assertRaises(AttributeError):
            del target.empty

        self.assertEqual(self.stream.getvalue(), "")

    def test_08_logger(self):
        v_on_init_set = "on_init_set"
        v_on_init_name = "on_init_name"
        v_prop_set = "prop_set"
        v_prop_name = "prop_name"

        # noinspection PyMissingOrEmptyDocstring
        class Target:
            on_init_set = logwrap.LogOnAccess(logger=logging.getLogger(v_on_init_set), fget=lambda self: v_on_init_set)
            on_init_name = logwrap.LogOnAccess(logger=v_on_init_name, fget=lambda self: v_on_init_name)

            @logwrap.LogOnAccess
            def prop_set(self):
                return v_prop_set

            prop_set.logger = logging.getLogger(v_prop_set)

            @logwrap.LogOnAccess
            def prop_name(self):
                return v_prop_name

            prop_name.logger = v_prop_name

            def __repr__(tself):
                return f"{tself.__class__.__name__}()"

        target = Target()

        getattr(target, "on_init_set")  # noqa: B009
        logged = self.stream.getvalue().splitlines()
        self.assertEqual("DEBUG:on_init_set:Request: Target().on_init_set", logged[0])
        self.assertRegex(
            logged[1],
            rf"DEBUG:on_init_set:Done at (?:\d+\.\d{{3}})s: "
            rf"Target\(\)\.on_init_set -> {logwrap.pretty_repr(v_on_init_set)}",
        )

        self.stream.seek(0)
        self.stream.truncate()

        getattr(target, "on_init_name")  # noqa: B009
        logged = self.stream.getvalue().splitlines()
        self.assertEqual("DEBUG:on_init_name:Request: Target().on_init_name", logged[0])
        self.assertRegex(
            logged[1],
            rf"DEBUG:on_init_name:Done at (?:\d+\.\d{{3}})s: "
            rf"Target\(\)\.on_init_name -> {logwrap.pretty_repr(v_on_init_name)}",
        )

        self.stream.seek(0)
        self.stream.truncate()

        getattr(target, "prop_set")  # noqa: B009
        logged = self.stream.getvalue().splitlines()
        self.assertEqual("DEBUG:prop_set:Request: Target().prop_set", logged[0])
        self.assertRegex(
            logged[1],
            rf"DEBUG:prop_set:Done at (?:\d+\.\d{{3}})s: "
            rf"Target\(\)\.prop_set -> {logwrap.pretty_repr(v_prop_set)}",
        )

        self.stream.seek(0)
        self.stream.truncate()

        getattr(target, "prop_name")  # noqa: B009
        logged = self.stream.getvalue().splitlines()
        self.assertEqual("DEBUG:prop_name:Request: Target().prop_name", logged[0])
        self.assertRegex(
            logged[1],
            rf"DEBUG:prop_name:Done at (?:\d+\.\d{{3}})s: "
            rf"Target\(\)\.prop_name -> {logwrap.pretty_repr(v_prop_name)}",
        )

    def test_09_logger_implemented(self):
        # noinspection PyMissingOrEmptyDocstring
        class Target:
            def __init__(tself, val=VALUE):
                tself.val = val
                tself.logger = logging.getLogger(tself.__class__.__name__)

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
        self.assertEqual("DEBUG:Target:Request: Target(val=ok).ok", logged[0])
        self.assertRegex(
            logged[1],
            rf"DEBUG:Target:Done at (?:\d+\.\d{{3}})s: Target\(val=ok\)\.ok -> {logwrap.pretty_repr(VALUE)}",
        )

        self.stream.seek(0)
        self.stream.truncate()

        target.ok = VALUE.upper()
        logged = self.stream.getvalue().splitlines()
        self.assertEqual(
            f"DEBUG:Target:Request: Target(val=ok).ok = {logwrap.pretty_repr(VALUE.upper())}",
            logged[0],
        )
        self.assertRegex(
            logged[1],
            rf"DEBUG:Target:Done at (?:\d+\.\d{{3}})s: "
            rf"Target\(val=ok\)\.ok = {logwrap.pretty_repr(VALUE.upper())}",
        )

        self.assertEqual(target.ok, VALUE.upper())

        self.stream.seek(0)
        self.stream.truncate()

        del target.ok
        logged = self.stream.getvalue().splitlines()
        self.assertEqual("DEBUG:Target:Request: del Target(val=OK).ok", logged[0])
        self.assertRegex(logged[1], r"DEBUG:Target:Done at (?:\d+\.\d{3})s: del Target\(val=OK\)\.ok")

    def test_10_log_implemented(self):
        # noinspection PyMissingOrEmptyDocstring
        class Target:
            def __init__(tself, val=VALUE):
                tself.val = val
                tself.log = logging.getLogger(tself.__class__.__name__)

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
        self.assertEqual("DEBUG:Target:Request: Target(val=ok).ok", logged[0])
        self.assertRegex(
            logged[1],
            rf"DEBUG:Target:Done at (?:\d+\.\d{{3}})s: Target\(val=ok\)\.ok -> {logwrap.pretty_repr(VALUE)}",
        )

        self.stream.seek(0)
        self.stream.truncate()

        target.ok = VALUE.upper()
        logged = self.stream.getvalue().splitlines()
        self.assertEqual(
            f"DEBUG:Target:Request: Target(val=ok).ok = {logwrap.pretty_repr(VALUE.upper())}",
            logged[0],
        )
        self.assertRegex(
            logged[1],
            rf"DEBUG:Target:Done at (?:\d+\.\d{{3}})s: "
            rf"Target\(val=ok\)\.ok = {logwrap.pretty_repr(VALUE.upper())}",
        )

        self.assertEqual(target.ok, VALUE.upper())

        self.stream.seek(0)
        self.stream.truncate()

        del target.ok
        logged = self.stream.getvalue().splitlines()
        self.assertEqual("DEBUG:Target:Request: del Target(val=OK).ok", logged[0])
        self.assertRegex(logged[1], r"DEBUG:Target:Done at (?:\d+\.\d{3})s: del Target\(val=OK\)\.ok")
