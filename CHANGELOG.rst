CHANGELOG
=========
Version 1.0.0
-------------
* Drop historical code and update documentation

Version 0.9.0
-------------
* get_arg_names and get_call_args now presents only for historical reasons

* logwrap now logs argument types as commentaries
(POSITIONAL_ONLY(builtins only) | POSITIONAL_OR_KEYWORD (standard) | VAR_POSITIONAL (e.g. *args) | KEYWORD_ONLY (Python 3+ only) | VAR_KEYWORD (e.g. **kwargs))

Version 0.8.5
-------------
* Use funcsigs instead of manual reimplementation of inspect.signature & supplemental

* Implement parsing of functions and methods (log interfaces in additional to standard repr)

* internal modules was moved to protected scope

Version 0.8.0
-------------
* Drop six requirement

Version 0.7.3
-------------
* Documentation update only

Version 0.7.2
-------------
Internal bump for CI systems check

Version 0.7.1
-------------

* Tests is included in package

* Docstrings and misprints in documents fixed

* CI CD

Version 0.7
-----------
Functional changes:

* Fixed difference of repr empty set() between python versions: replace by string `set()`


CI and structure changes:

* Added CHANGELOG

* Use CirceCI for pylint and coverage upload (uploaded from python 2.7)

* LICENSE file has been replaced by template from GitHub due to parsing issues

Version 0.6
-----------
* Started stabilization: package structure, tests, CI

Prior to 0.6
------------
Preparing package, CI and fixing found issues.