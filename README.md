# Samsung Galaxy A30s NetHunter Kernel Lab

> **Status: experimental / work in progress.** This repository is a development workspace for building and testing Linux 4.4 kernels and Kali NetHunter features on Samsung Exynos 7885 devices, especially Galaxy A30s. It is not a polished, one-click installer. Device variant, Android firmware, boot image format and partition layout must match your phone exactly.

## Contents

- [Overview](#overview)
- [Kernel trees](#kernel-trees)
- [NetHunter-related features](#nethunter-related-features)
- [Repository layout](#repository-layout)
- [Build requirements](#build-requirements)
- [Build](#build)
- [Boot image repacking](#boot-image-repacking)
- [Installation and recovery](#installation-and-recovery)
- [Troubleshooting](#troubleshooting)
- [Security and responsible use](#security-and-responsible-use)
- [Licensing and upstream credits](#licensing-and-upstream-credits)

## Overview

Workspace contains several Exynos 7885 kernel source trees and experiments, rather than one canonical release branch:

| Directory | Source / base | Kernel version | Purpose |
|---|---|---:|---|
| `kernel/` | Eureka Exynos7885 Q/R/S, branch `R14.2-OneUI` | 4.4.302-p6 | Eureka-based build, DTB work and NetHunter config experiments |
| `k177/` | TWRP Samsung A30s, branch `android-11` | 4.4.177 | Older A30s-oriented kernel build and experiments |
| `mint/` | Sliva4 A30s, Mint R1 | 4.4.260 | Mint-based build, AnyKernel3 packaging and KernelSU-related source |

Each tree has its own source history and configuration. Do not mix generated files, `.config` files or output images between trees. The root directory itself is not a Git repository; the kernel source directories are separate Git checkouts.

## Kernel trees

### Eureka (`kernel/`)

Build wrapper `mk.sh` invokes `make` in `kernel/` using the bundled `toolchain/` (Proton Clang checkout). It sets `ARCH=arm64`, Android 11 build variables and `LOCALVERSION=-NetHunter_a30s`. `kernel/NOTES.md` belongs to the upstream Eureka project and describes that project's build modes; this workspace does **not** include its original top-level `build.sh` workflow.

Useful A30s config: `arch/arm64/configs/exynos7885-a30s_defconfig`.

### Linux 4.4.177 (`k177/`)

Build wrapper `mk177.sh` uses GCC 9.5 nolibc cross compiler under `gcc/`. NetHunter-oriented config snapshot is at root as `config177.uh_on`; feature fragment is `nh.fragment`. Those are experiment/config reference files, not an installer or guaranteed complete config.

### Mint R1 (`mint/`)

Contains the upstream `build_kernel.sh`, `AnyKernel3/` packaging tree, device defconfigs and Git submodules, including KernelSU and Baseband-guard. Its build script takes device name and DTB mode as positional arguments, cleans after build, then packages a flashable ZIP. Run it only after reviewing its submodule/version assumptions and outputs (see [Build](#build)).

## NetHunter-related features

`nh.fragment` and `config177.uh_on` enable or configure a number of kernel capabilities commonly used by NetHunter, including:

- mac80211 and selected USB Wi-Fi drivers (for example RTL8XXXU, RT2800USB, MT7601U, ATH9K-HTC and ZD1211RW, where enabled in the selected config)
- USB gadget functions such as HID, RNDIS, ECM, ACM, serial and mass storage
- USB serial adapters, Bluetooth transports, networking, advanced routing and selected netfilter options
- Wireless extensions and related kernel networking support

These settings do not by themselves guarantee compatibility with every adapter, firmware, Android userspace or NetHunter feature. External USB adapters may require a powered OTG hub, compatible firmware and device-specific testing. Verify final `.config` and runtime devices on the target phone.

`nhdl/` contains local NetHunter installer/download material and extracted Kali rootfs files. It is not needed to compile the kernel. NetHunter app/chroot installation is a separate process from kernel installation.

## Repository layout

```text
.
├── kernel/                 # Eureka 4.4.302 source tree
├── k177/                   # TWRP A30s 4.4.177 source tree
├── mint/                   # Mint R1 4.4.260 source and AnyKernel3
├── toolchain/              # Proton Clang toolchain checkout
├── gcc/                    # GCC cross-toolchain archive / extracted toolchain
├── hosttools/              # Local host-tool compatibility helpers
├── backup/                 # Stock boot, recovery, DTB/DTBO, config backups
├── out_images/             # Locally produced kernel and boot image artifacts
├── nh.fragment             # NetHunter-oriented Kconfig fragment
├── config177.uh_on         # Linux 4.4.177 config snapshot
├── mk.sh                   # Eureka kernel make wrapper
├── mk177.sh                # 4.4.177 kernel make wrapper
├── mkmint.sh               # Mint kernel make wrapper
└── repack_boot.py          # Android boot image kernel-replacement helper
```

The workspace also contains local logs, scratch test scripts, extracted/downloaded archives, source snapshots and compiled objects. They document active development, and should not be treated as release artifacts. Large binaries, stock firmware images, downloaded APK/ZIP files, build products and device logs generally should stay out of public Git history.

## Build requirements

Build on a Linux x86-64 host. Expected tools include `bash`, `make`, `gcc`/`g++`, `python3`, `git`, `bc`, `bison`, `flex`, `openssl`, `perl`, `zip` and standard binutils. Adequate RAM, disk space and a multi-core CPU are recommended; set parallelism to suit host capacity.

Toolchain details vary by tree:

- Eureka wrapper expects `toolchain/bin/clang`, `ld.lld`, LLVM tools and AArch64/ARM cross tools.
- `mk177.sh` expects GCC 9.5 at `gcc/gcc-9.5.0-nolibc/aarch64-linux/bin/`.
- Mint kernel script uses host `make` plus its local host-tool setup and initialized Git submodules.

**Important:** current root wrappers embed `/home/notroot/repos/a30sNethunter` absolute paths. Change those paths for your checkout before using scripts elsewhere. Some source trees/submodules are separate Git checkouts; clone/update the required upstream repositories and submodules according to their respective licenses and instructions.

## Build

### Eureka tree

From workspace root, after adjusting paths in `mk.sh` if needed:

```bash
cd kernel
../mk.sh exynos7885-a30s_defconfig
../mk.sh -j"$(nproc)"
```

`mk.sh` itself sets `-j28`, so its fixed job count can be edited to match your machine. Typical output is `kernel/arch/arm64/boot/Image`; DTB/DTBO targets and image assembly depend on source configuration. Review the selected defconfig and resulting `.config` before building. For a separate output directory, wrapper currently specifies `O=out`.

### Linux 4.4.177 tree

From workspace root:

```bash
cd k177
../mk177.sh exynos7885-a30s_defconfig
../mk177.sh -j"$(nproc)"
```

The wrapper sets its own `-j28` and uses an absolute GCC path. Adjust wrapper path and parallelism if required. The `config177.uh_on` snapshot may be applied/compared using the kernel's normal Kconfig tools, but inspect the resulting config rather than assuming the snapshot maps cleanly to another source revision.

### Mint tree and AnyKernel ZIP

From workspace root, inspect `mint/build_kernel.sh` first. It expects a device identifier and DTB option; for example, use the supported device string corresponding to your exact A30s build and choose `dtb` only when you intend to include rebuilt DTB:

```bash
cd mint
./build_kernel.sh a30s without-dtb
```

The script's DTB check is exact (`dtb` enables DTB packaging); any other second argument skips it. It initializes submodules, cleans source, builds a device defconfig, creates an AnyKernel3 ZIP and cleans again. Confirm submodule availability, selected config, and generated ZIP contents before use. Mint's script uses `make -j4` internally; `mkmint.sh` is a separate general make wrapper and is not called by `build_kernel.sh`.

## Boot image repacking

`repack_boot.py` replaces the kernel payload in an Android boot image v1 with 2048-byte pages while retaining ramdisk and footer data, updating the header size/checksum and padding output to source image size:

```bash
python3 repack_boot.py stock-boot.img Image patched-boot.img
```

This helper has a narrow format assumption and is not a general-purpose Android image tool. It does not build a complete firmware package or validate that image is suitable for your model/firmware. Check image header, partition size, AVB/vbmeta state and boot chain independently. Keep an untouched copy of stock `boot`, `dtb`, `dtbo`, `vbmeta` and recovery images before any device operation.

## Installation and recovery

Installation is device- and firmware-specific. Use a tested Mint AnyKernel ZIP only if it explicitly supports your exact model and firmware, or use a correctly assembled image through the recovery/flash method documented for that device. Do not flash `out_images/` artifacts merely because they were produced here.

Before changing boot-related partitions:

1. Confirm exact model number, SoC, Android/One UI version, current kernel and partition names.
2. Make and verify restorable backups, including `boot`, `dtb`, `dtbo` and `vbmeta` where present.
3. Ensure recovery/download mode and a known-good restore path work before flashing.
4. Never flash images from a different device variant or firmware generation.
5. After boot, check `uname -a`, `dmesg`, device functions and kernel config before testing additional features.

NetHunter full chroot/app installation is separate. A kernel flash does not install Kali userspace, and installing NetHunter userspace does not install a compatible kernel. Root/Magisk requirements depend on the chosen installer and firmware.

## Troubleshooting

- **Compiler/tool not found:** check toolchain checkout, executable permissions and hard-coded paths in wrapper.
- **Build fails after switching trees/configs:** clean that source tree and regenerate config; never reuse another tree's generated output.
- **Missing Kconfig option:** verify option exists in the selected kernel revision and dependencies are enabled; inspect final `.config`.
- **Kernel boots but adapter/HID is absent:** inspect `dmesg`, `/sys/kernel/config/usb_gadget`, `/sys/class/android_usb`, `/dev/hidg*`, firmware availability and active USB gadget mode. Built-in config alone does not imply Android userspace exposes function.
- **Boot loop or no boot:** restore matching stock boot-related images using device-specific recovery instructions. Do not continue experimenting without a verified recovery path.
- **Useful diagnostics:** save `dmesg`, `last_kmsg`/pstore output, exact model and firmware, kernel version, build config and reproduction steps. Remove personal identifiers before sharing logs.

## Security and responsible use

NetHunter and wireless/USB testing capabilities are intended for authorized security research, device testing and education. Only test systems and networks you own or have explicit permission to assess. Users assume responsibility for device damage, data loss and applicable laws. Keep test devices and backups available; development kernels can reduce device security and reliability.

## Licensing and upstream credits

Kernel components are covered by their respective upstream licenses, commonly GPL-2.0, as indicated by each source tree and file. Eureka, TWRP-exynos7885, Sliva4/Mint, Proton Clang, AnyKernel3, Kali NetHunter, KernelSU and other included/upstream projects retain their own copyrights and licenses. Consult source tree license files and submodule notices before redistribution. This README does not change upstream licensing.

## Contributing

Keep changes scoped to one kernel tree where possible. Include source tree/branch, exact device and firmware, config used, build command, build result and relevant sanitized logs with reports. Avoid committing generated objects, personal device dumps, stock images, proprietary downloads or secrets.
