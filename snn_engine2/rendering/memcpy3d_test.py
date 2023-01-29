import sys
import math
import time
import argparse

import numpy

import pycuda
import pycuda.driver
import pycuda.compiler
import pycuda.gpuarray

import pycuda.autoinit


def copyPlane(copy, stream, srcX, dstX, srcY, dstY, srcZ, dstZ, width_in_bytes, height, depth):
    copy.src_x_in_bytes = srcX
    copy.dst_x_in_bytes = dstX
    copy.src_y = srcY
    copy.dst_y = dstY
    copy.src_z = srcZ
    copy.dst_z = dstZ
    copy.width_in_bytes = width_in_bytes
    copy.height = height
    copy.depth = depth
    if stream:
        copy(stream)
    else:
        copy()


parser = argparse.ArgumentParser(description="Test speed of memory copy")

parser.add_argument("-d", "--domain", dest="domainSize", type=int,
                    default=18, help="Size of the domain to copy (default: 18)")
parser.add_argument("-t", "--block", dest="blockSize", type=int,
                    default=64, help="Size of the block of threads to copy (default: 64)")
parser.add_argument("-b", "--basis", dest="basis", type=int,
                    default=19, help="Size of the block of threads to copy (default: 19)")

parser.add_argument("--direction", dest="copyDirection",
                    action="store", default='htod', choices=['htod', 'dtoh', 'both'],
                    help="Copy direction (default: htod)")

parser.add_argument("--envelope_method", dest="envelopeCopyMethod",
                    action="store", default='everything', choices=['naive', 'smart'],
                    help="Copy direction (default: naive)")

args = parser.parse_args()

stream = None

floatSize = 4
floatType = numpy.float32
strideX = int(math.ceil(float(args.domainSize)/args.blockSize))*args.blockSize*floatSize
strides = (args.domainSize*strideX, strideX, floatSize)
strideZ = args.domainSize*args.domainSize*strideX

gpudata = pycuda.driver.mem_alloc(strideZ*args.basis)

a3d = pycuda.gpuarray.GPUArray((args.basis*args.domainSize, args.domainSize, args.domainSize),
                               dtype=floatType, strides=strides, gpudata=gpudata)
a3h = numpy.ndarray((args.basis*args.domainSize, args.domainSize, args.domainSize),
                    dtype=floatType) + 1
c3d = pycuda.driver.Memcpy3D()

startD = pycuda.driver.Event()
endD = pycuda.driver.Event()
startH = time.time()
endH = None

startD.record()
c3d.src_pitch = args.domainSize*floatSize
c3d.dst_pitch = strideX
c3d.src_height = args.domainSize
c3d.dst_height = args.domainSize

if args.envelopeCopyMethod == 'smart':
    if args.copyDirection in {'htod', 'both'}:
        c3d.set_src_host(a3h)
        c3d.set_dst_device(a3d.gpudata)

# copy, stream, srcX, dstX, srcY, dstY, srcZ, dstZ, width_in_bytes, height, depth

# XY
        copyPlane(c3d, stream, srcX=floatSize, dstX=floatSize, srcY=1, dstY=1,
                  srcZ=0, dstZ=0,
                  width_in_bytes=(args.domainSize-2)*floatSize,
                  height=args.domainSize-2, depth=1)
        for i in range(1, args.basis):
            copyPlane(c3d, stream, floatSize, floatSize, 1, 1, i*args.domainSize-1, i*args.domainSize-1,
                (args.domainSize-2)*floatSize, args.domainSize-2, 2)
        copyPlane(c3d, stream, floatSize, floatSize, 1, 1, args.domainSize*args.basis-1, args.domainSize*args.basis-1,
            (args.domainSize-2)*floatSize, args.domainSize-2, 1)
# XZ
        copyPlane(c3d, stream, 0, 0, 0, 0, 0, 0,
            args.domainSize*floatSize, 1, args.domainSize*args.basis)
        copyPlane(c3d, stream, 0, 0, args.domainSize-1, args.domainSize-1, 0, 0,
            args.domainSize*floatSize, 1, args.domainSize*args.basis)
# YZ
        copyPlane(c3d, stream, 0, 0, 0, 0, 0, 0,
            floatSize, args.domainSize, args.domainSize*args.basis)
        copyPlane(c3d, stream, (args.domainSize-1)*floatSize, (args.domainSize-1)*floatSize, 0, 0, 0, 0,
            floatSize, args.domainSize, args.domainSize*args.basis)
    if args.copyDirection in {'dtoh', 'both'}:
        c3d.set_src_device(a3d.gpudata)
        c3d.set_dst_host(a3h)
        c3d.src_pitch, c3d.dst_pitch = c3d.dst_pitch, c3d.src_pitch
# XY
        copyPlane(c3d, stream, floatSize*2, floatSize*2, 2, 2, 0, 0,
            (args.domainSize-4)*floatSize, args.domainSize-4, 1)
        for i in range(1, args.basis):
            copyPlane(c3d, stream, floatSize*2, floatSize*2, 2, 2, i*args.domainSize-1, i*args.domainSize-1,
                (args.domainSize-4)*floatSize, args.domainSize-4, 2)
        copyPlane(c3d, stream, floatSize*2, floatSize*2, 2, 2, args.domainSize*args.basis-1, args.domainSize*args.basis-1,
            (args.domainSize-4)*floatSize, args.domainSize-4, 1)
# XZ
        copyPlane(c3d, stream, 1, 1, 1, 1, 1, 1,
            (args.domainSize-2)*floatSize, 1, args.domainSize*args.basis-2)
        copyPlane(c3d, stream, 1, 1, args.domainSize-2, args.domainSize-2, 1, 1,
            (args.domainSize-2)*floatSize, 1, args.domainSize*args.basis-2)
# YZ
        copyPlane(c3d, stream, 1, 1, 1, 1, 1, 1,
            floatSize, args.domainSize-2, args.domainSize*args.basis-2)
        copyPlane(c3d, stream, (args.domainSize-2)*floatSize, (args.domainSize-2)*floatSize, 1, 1, 1, 1,
            floatSize, args.domainSize-2, args.domainSize*args.basis-2)
elif args.envelopeCopyMethod == 'naive':
    if args.copyDirection in {'htod', 'both'}:
        c3d.set_src_host(a3h)
        c3d.set_dst_device(a3d.gpudata)
        for i in range(args.basis):
            c3d.set_src_host(a3h[i*args.domainSize:(i+1)*args.domainSize, :, :])
            c3d.set_dst_device(int(a3d.gpudata)+i*args.domainSize*args.domainSize*args.domainSize)
# XY
            copyPlane(c3d, stream, 0, 0, 0, 0, 0, 0,
                args.domainSize*floatSize, args.domainSize, 1)
            copyPlane(c3d, stream, 0, 0, 0, 0, args.domainSize-1, args.domainSize-1,
                args.domainSize*floatSize, args.domainSize, 1)
# XZ
            copyPlane(c3d, stream, 0, 0, 0, 0, 0, 0,
                args.domainSize*floatSize, 1, args.domainSize)
            copyPlane(c3d, stream, 0, 0, args.domainSize-1, args.domainSize-1, 0, 0,
                args.domainSize*floatSize, 1, args.domainSize)
# YZ
            copyPlane(c3d, stream, 0, 0, 0, 0, 0, 0,
                floatSize, args.domainSize, args.domainSize)
            copyPlane(c3d, stream, (args.domainSize-1)*floatSize, (args.domainSize-1)*floatSize,
                0, 0, 0, 0, floatSize, args.domainSize, args.domainSize)
    if args.copyDirection in {'dtoh', 'both'}:
        c3d.src_pitch, c3d.dst_pitch = c3d.dst_pitch, c3d.src_pitch
        for i in range(args.basis):
            c3d.set_src_device(int(a3d.gpudata)+i*args.domainSize*args.domainSize*args.domainSize)
            c3d.set_dst_host(a3h[i*args.domainSize:(i+1)*args.domainSize, :, :])
# XY
            copyPlane(c3d, stream, 1, 1, 1, 1, 1, 1,
                (args.domainSize-2)*floatSize, args.domainSize, 1)
            copyPlane(c3d, stream, 1, 1, 1, 1, args.domainSize-2, args.domainSize-2,
                (args.domainSize-2)*floatSize, args.domainSize-2, 1)
# XZ
            copyPlane(c3d, stream, 1, 1, 1, 1, 1, 1,
                (args.domainSize-2)*floatSize, 1, args.domainSize-2)
            copyPlane(c3d, stream, 1, 1, args.domainSize-2, args.domainSize-2, 1, 1,
                (args.domainSize-2)*floatSize, 1, args.domainSize-2)
# YZ
            copyPlane(c3d, stream, 1, 1, 1, 1, 1, 1,
                floatSize, args.domainSize-2, args.domainSize-2)
            copyPlane(c3d, stream, (args.domainSize-2)*floatSize, (args.domainSize-2)*floatSize,
                1, 1, 1, 1, floatSize, args.domainSize-2, args.domainSize-2)

endD.record()
endD.synchronize()
endH = time.time()
print("{0:.3f} {1:.3f}".format(endD.time_since(startD), 1000*(endH-startH)))
print()