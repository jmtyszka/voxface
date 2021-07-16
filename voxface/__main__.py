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
import antspy


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Fast MRI face voxelator')
    parser.add_argument('-i', '--infile', required=True, help='Structural MRI with intact face')
    parser.add_argument('-o', '--outfile', default='phantom', help="QC Mode (phantom or live)")

    # Parse command line arguments
    args = parser.parse_args()
    in_fname = os.path.realpath(args.infile)

    if args.outfile:
        out_fname = os.path.realpath(args.outfile)
    else:
        out_fname = in_fname.replace('.nii.gz', 'defaced.nii.gz')



# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':

    main()
