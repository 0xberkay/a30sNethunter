#!/usr/bin/env bash
cd /home/notroot/repos/a30sNethunter/k177
export ARCH=arm64 ANDROID_MAJOR_VERSION=r PLATFORM_VERSION=11 LOCALVERSION=-22825772
export KBUILD_BUILD_USER=build KBUILD_BUILD_HOST=nethunter
exec make -j28 ARCH=arm64 HOSTCC=gcc HOSTCXX=g++ CROSS_COMPILE=/home/notroot/repos/a30sNethunter/gcc/gcc-9.5.0-nolibc/aarch64-linux/bin/aarch64-linux- KCFLAGS="-Wno-error -D__ANDROID__" "$@"
