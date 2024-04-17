# CBCT Ceph Script

![Alt text](./cbct_to_ceph.svg)

## Dependencies
```console
$ pip install matplotlib numpy pydicom pypng
```

## Usage
```console
$ python3 main.py --help
Usage: main.py [-h] [--output OUTPUT] [--input_axis INPUT_AXIS] dicom_files [dicom_files ...]

Construct cephalogram from CBCT.

positional arguments:
  dicom_files           Dicom files of the CBCT.

options:
  -h, --help               show this help message and exit
  --output OUTPUT          Name of the output file.
  --input_axis INPUT_AXIS  Plane of dicom data (i.e. sagittal, coronal or transverse)
```
