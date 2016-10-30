#!/usr/bin/env bash
rm -rf ./dist/* ./build/* ./doc/build/* ./.cache/* ./.eggs/ ./.tox/
tox
python setup.py sdist bdist_wheel bdist_egg
twine register dist/logwrap*.tar.gz
twine upload ./dist/*
python setup.py build_sphinx upload_docs