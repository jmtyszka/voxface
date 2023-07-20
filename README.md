# Voxface

Fast voxelation of the face in 3D structural MRI data combining spline downsampling with nearest-neighbor upsampling to
deidentify the face while retaining some signal intensity to guide whole-head registration.

## Installation

### Latest Version
2023.7.20.1

### GitHub Installation

1. Clone this branch to your local system
   ```
   % git clone https://github.com/jmtyszka/voxface.git
   ```
2. Install to your local Python 3 environment
   ```
   % cd voxface
   % [sudo] python3 setup.py install
   ```
   
### PyPI Installation

1. Install the latest Python 3 version of *voxface* from PyPI
    ```
    % [sudo] pip3 install voxface
    ```

### Typical Performance
Face voxelation of a typical 1 mm isotropic T1w image takes 5 - 6 seconds on a 3.2 GHz 6-Core Intel Core i7 Mac Mini.
