#!/bin/bash
package_name="$1"
if [ -z "$package_name" ]
then
    # shellcheck disable=SC2210
    &>2 echo "Please pass package name as a first argument of this script ($0)"
    exit 1
fi

docker pull "quay.io/pypa/manylinux2010_i686" & arch_pull_pid=$!

echo
echo
echo waiting for docker pull pid $arch_pull_pid to complete downloading container for i686 arch...
wait $arch_pull_pid  # await for docker image for current arch to be pulled from hub

echo Building wheel for i686 arch
docker run --rm -v "$(pwd)":/io "quay.io/pypa/manylinux2010_i686" linux32 /io/tools/build-wheels.sh "$package_name"
