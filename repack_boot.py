#!/usr/bin/env python3
"""Replace kernel in an Android boot.img v1 (page 2048), keep ramdisk/footer, pad to original size."""
import struct, sys, hashlib
src, kernel_path, out = sys.argv[1:4]
b = bytearray(open(src, 'rb').read())
assert b[:8] == b'ANDROID!'
ksz, kaddr, rsz, raddr, ssz, saddr, taddr, psz, hver = struct.unpack('<9I', b[8:44])
rec_sz = struct.unpack('<I', b[1632:1636])[0]
hdr_sz = struct.unpack('<I', b[1648:1652])[0] if hver >= 1 else 0
al = lambda n: (n + psz - 1) // psz * psz
k_off = psz
r_off = k_off + al(ksz)
s_off = r_off + al(rsz)
rec_off = s_off + al(ssz)
end = rec_off + al(rec_sz)
kernel = open(kernel_path, 'rb').read()
ramdisk = bytes(b[r_off:r_off + rsz]); second = bytes(b[s_off:s_off + ssz]); rec = bytes(b[rec_off:rec_off + rec_sz])
footer = bytes(b[end:])
avb_end = footer[-64:] if footer[-64:-60] == b'AVBf' else b''
footer_head = footer[:len(footer) - len(avb_end)].rstrip(b'\0')
pad = lambda d: d + b'\0' * (al(len(d)) - len(d))
h = bytearray(b[:psz])
struct.pack_into('<I', h, 8, len(kernel))
sha = hashlib.sha1()
for d in (kernel, ramdisk, second):
    sha.update(d); sha.update(struct.pack('<I', len(d)))
if hver >= 1:
    sha.update(rec); sha.update(struct.pack('<I', len(rec)))
    if hver >= 2: pass
h[576:608] = sha.digest().ljust(32, b'\0')
body = bytes(h) + pad(kernel) + pad(ramdisk) + pad(second) + pad(rec)
o = body + footer_head
# keep total size identical to source (partition-sized image)
if len(o) + len(avb_end) > len(b): sys.exit('too big: %d > %d' % (len(o) + len(avb_end), len(b)))
o += b'\0' * (len(b) - len(o) - len(avb_end)) + avb_end
open(out, 'wb').write(o)
print('ok', out, len(o), 'kernel', len(kernel), 'footer', len(footer))
