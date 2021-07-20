#!/usr/bin/env python3
"""
Fast MRI face voxelator for deidentifying T1w and T2w structural images

Authors
----
Mike Tyszka, Caltech Brain Imaging Center

MIT License

Copyright (c) 2021 Mike Tyszka

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import sys
import argparse
import time

import ants
import pkg_resources
import numpy as np


def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Fast MRI face voxelator')
    parser.add_argument('-i', '--infile', help='Structural MRI with intact face')
    parser.add_argument('-o', '--outfile', help="Defaced image filename")
    parser.add_argument('--voxdim', default=8.0, type=float,
                        help='Voxelation dimension in mm [8.0]')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="Verbose output [False]")
    parser.add_argument('-V', '--version', action='store_true', default=False,
                        help='Display voxface version number and exit')

    # Parse command line arguments
    args = parser.parse_args()

    # Read version from setup.py
    ver = pkg_resources.get_distribution('voxface').version

    if args.version:
        print('VOXFACE {}'.format(ver))
        sys.exit(1)

    if args.infile:
        in_fname = os.path.realpath(args.infile)
    else:
        print('* No faced image provided - exiting')
        sys.exit(1)

    if args.outfile:
        out_fname = os.path.realpath(args.outfile)
    else:
        out_fname = in_fname.replace('.nii.gz', '_defaced.nii.gz')

    if args.verbose:

        print('')
        print('Facial Voxelator {}'.format(ver))
        print('----------------')
        print('Faced image     : {}'.format(in_fname))
        print('Voxelated image : {}'.format(out_fname))
        print('Voxelation size : {} mm'.format(args.voxdim))
        print('')

    # Start timer
    tic = time.perf_counter()

    # Load faced image as an AntsImage
    if args.verbose:
        print('Loading faced image')

    faced_ai = ants.image_read(in_fname)

    # Load template image
    t1_template_fname = pkg_resources.resource_filename(
        'voxface',
        os.path.join('templates', 'ConteCore2_50_T1w_2mm.nii.gz')
    )

    if args.verbose:
            print('Loading T1 template')

    template_ai = ants.image_read(t1_template_fname)

    # Load deface mask
    facemask_fname = pkg_resources.resource_filename(
        'voxface',
        os.path.join('templates', 'ConteCore2_50_2mm_deface_mask.nii.gz')
    )

    if args.verbose:
        print('Loading template facemask')

    facemask_ai = ants.image_read(facemask_fname)

    # Affine register template to faced image
    if args.verbose:
        print('Registering template to individual space')

    affine_tx = ants.registration(
        fixed=faced_ai,
        moving=template_ai,
        type_of_transform='AffineFast'
    )

    # Apply transform to deface mask
    if args.verbose:
        print('Applying transform to facemask')

    ind_facemask_ai = ants.apply_transforms(
        fixed=faced_ai,
        moving=facemask_ai,
        transformlist=affine_tx['fwdtransforms'],
        interpolator='nearestNeighbor'
    )

    # Voxelate input image
    # 1. Cubic downsample
    # 2. Nearest neighbor upsample

    # Get original image voxel dimensions and matrix size
    vx, vy, vz = faced_ai.spacing
    nx, ny, nz = faced_ai.shape

    # Downsampled matrix size to yield voxelation of requested dimensions
    nx_dwn = np.round(nx * vx / args.voxdim).astype(int)
    ny_dwn = np.round(ny * vy / args.voxdim).astype(int)
    nz_dwn = np.round(nz * vz / args.voxdim).astype(int)

    if args.verbose:
        print('Spline downsampling')

    faced_spdwn_ai = ants.resample_image(
        image=faced_ai,
        resample_params=(nx_dwn, ny_dwn, nz_dwn),
        use_voxels=True,
        interp_type=4  # B-spline
    )

    if args.verbose:
        print('Nearest neighbor upsampling')

    voxed_ai = ants.resample_image(
        image=faced_spdwn_ai,
        resample_params=(nx, ny, nz),
        use_voxels=True,
        interp_type=1  # Nearest neighbor
    )

    # Replace original with voxelated image within deface mask
    ones_ai = faced_ai.new_image_like(np.ones(faced_ai.shape))
    voxfaced_ai = faced_ai * ind_facemask_ai + voxed_ai * (ones_ai - ind_facemask_ai)

    # Save face voxelated image
    if args.verbose:
        print('Saving face voxelated image to {}'.format(out_fname))

    voxfaced_ai.to_filename(out_fname)

    if args.verbose:
        toc = time.perf_counter()
        print('Completed in {:0.1f} seconds'.format(toc-tic))


# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':

    main()
