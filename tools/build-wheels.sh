#!/bin/bash
set -e -o pipefail
PYTHON_VERSIONS="cp38-cp38 cp39-cp39 cp310-cp310"

# Avoid creation of __pycache__/*.py[c|o]
export PYTHONDONTWRITEBYTECODE=1

package_name="$1"
if [[ -z "$package_name" ]]; then
  # shellcheck disable=SC2210
  echo &>2 "Please pass package name as a first argument of this script ($0)"
  exit 1
fi

arch=$(uname -m)

# Clean-up
rm -rf /io/.tox
rm -rf /io/*.egg-info
rm -rf /io/.pytest_cache
find /io/ -noleaf \( -iname "*.py[co]" -o -iname "*.c" -o -iname "*-linux_*.whl" \) -delete

echo
echo
echo "Compile wheels"
cd /io

for PYTHON in ${PYTHON_VERSIONS}; do
  echo "Python ${PYTHON} ${arch}:"
  python_bin="/opt/python/${PYTHON}/bin"
  pip="$python_bin/pip"
  "$pip" install -U pip setuptools auditwheel
  "$pip" install -r /io/build_requirements.txt
  "$pip" wheel /io/ -w /io/dist/
  "$python_bin/python" setup.py bdist_wheel clean

  wheels=(/io/dist/"${package_name}"*"${PYTHON}"*linux_"${arch}".whl)
  for whl in "${wheels[@]}"; do
    echo "Repairing $whl..."
    if "$python_bin/python" -m auditwheel repair "$whl" -w /io/dist/; then
      echo
      echo "Cleanup OS specific wheels"
      rm -fv "$whl"
    else
      auditwheel show "$whl"
      exit 1
    fi
  done
  echo
  echo

  echo -n "Test $PYTHON ${arch}: $package_name "
  "$python_bin/python" -c "import platform;print(platform.platform())"
  "$pip" install "$package_name" --no-index -f file:///io/dist
  "$pip" install -r /io/pytest_requirements.txt
  echo
  "$python_bin/py.test" -vvv /io/test
  echo
done

# Clean caches + cythonized + not fixed
find /io/ -noleaf \( -iname "*.py[co]" -o -iname "*.c" -o -iname "*-linux_*.whl" \) -delete
rm -rf /io/.eggs
rm -rf /io/build
rm -rf /io/*.egg-info
rm -rf /io/.pytest_cache
rm -rf /io/.tox
rm -f /io/.coverage

# Reset permissions
chmod -v a+rwx /io/dist
chmod -v a+rw /io/dist/*
chmod -vR a+rw /io/"$package_name"
