#!/usr/bin/env bash
cd /home/notroot/repos/a30sNethunter/mint
export PATH=/home/notroot/repos/a30sNethunter/hosttools/bin:$PATH
export LD_LIBRARY_PATH=/home/notroot/repos/a30sNethunter/hosttools/lib
export ARCH=arm64 KBUILD_BUILD_USER=build KBUILD_BUILD_HOST=nethunter
exec make -j"${JOBS:-8}" ARCH=arm64 HOSTCC=gcc HOSTCXX=g++ KCFLAGS="-Wno-error" "$@"
