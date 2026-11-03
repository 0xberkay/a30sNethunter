#!/usr/bin/env bash
# usage: mk.sh <make targets...>
T=/home/notroot/repos/a30sNethunter/toolchain/bin
cd /home/notroot/repos/a30sNethunter/kernel
export ARCH=arm64 ANDROID_MAJOR_VERSION=r PLATFORM_VERSION=11 LOCALVERSION=-NetHunter_a30s
exec make -j28 O=out ARCH=arm64 HOSTCC=gcc HOSTCXX=g++ CC=$T/clang LD=$T/ld.lld AR=$T/llvm-ar NM=$T/llvm-nm \
  OBJDUMP=$T/llvm-objdump STRIP=$T/llvm-strip CLANG_TRIPLE=aarch64-linux-gnu- \
  CROSS_COMPILE=$T/aarch64-linux-gnu- CROSS_COMPILE_ARM32=$T/arm-linux-gnueabi- "$@"
