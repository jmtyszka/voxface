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
import argparse
import ants
import pkg_resources
import numpy as np


def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Fast MRI face voxelator')
    parser.add_argument('-i', '--infile', required=True, help='Structural MRI with intact face')
    parser.add_argument('-o', '--outfile', help="Defaced image filename")

    # Parse command line arguments
    args = parser.parse_args()
    in_fname = os.path.realpath(args.infile)

    if args.outfile:
        out_fname = os.path.realpath(args.outfile)
    else:
        out_fname = in_fname.replace('.nii.gz', '_defaced.nii.gz')

    print('Faced image   : {}'.format(in_fname))
    print('Defaced image : {}'.format(out_fname))

    # Load faced image as an AntsImage
    print('Loading faced image')
    faced_ai = ants.image_read(in_fname)

    # Load template image
    t1_template_fname = pkg_resources.resource_filename(
        'voxface',
        os.path.join('templates', 'ConteCore2_50_T1w_2mm.nii.gz')
    )
    print('Loading T1 template')
    template_ai = ants.image_read(t1_template_fname)

    # Load deface mask
    facemask_fname = pkg_resources.resource_filename(
        'voxface',
        os.path.join('templates', 'ConteCore2_50_2mm_deface_mask.nii.gz')
    )
    print('Loading template facemask')
    facemask_ai = ants.image_read(facemask_fname)

    # Affine register template to faced image
    print('Registering template to individual space')
    affine_tx = ants.registration(
        fixed=faced_ai,
        moving=template_ai,
        type_of_transform='AffineFast'
    )

    # Apply transform to deface mask
    print('Applying transform to facemask')
    ind_facemask_ai = ants.apply_transforms(
        fixed=faced_ai,
        moving=facemask_ai,
        transformlist=affine_tx['fwdtransforms'],
        interpolator='nearestNeighbor'
    )

    # Save transformed facemask
    ind_facemask_ai.to_filename('facemask.nii.gz')

    # Voxelate input image
    # 1. Cubic downsample
    # 2. Nearest neighbor upsample

    vox_sf = 8.0
    old_dims = np.array(faced_ai.shape)
    new_dims = (old_dims / vox_sf).astype(int)

    print('Spline downsampling')
    faced_spdwn_ai = ants.resample_image(
        image=faced_ai,
        resample_params=new_dims,
        use_voxels=True,
        interp_type=4  # B-spline
    )

    print('  Nearest neighbor upsampling')
    voxed_ai = ants.resample_image(
        image=faced_spdwn_ai,
        resample_params=old_dims,
        use_voxels=True,
        interp_type=1  # Nearest neighbor
    )

    # Save voxelated image
    voxed_ai.to_filename('voxelated.nii.gz')

    # Replace original with voxelated image within deface mask
    ones_ai = faced_ai.new_image_like(np.ones(faced_ai.shape))
    voxfaced_ai = faced_ai * ind_facemask_ai + voxed_ai * (ones_ai - ind_facemask_ai)
    voxfaced_ai.to_filename('voxfaced.nii.gz')


# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':

    main()
