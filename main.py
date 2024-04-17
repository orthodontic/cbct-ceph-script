import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from pydicom import dcmread
from pydicom.pixel_data_handlers.util import apply_windowing
import png


def construct(dcm_files: list[Path], input_axis):
    volume_arr = None
    pixel_spacing = None  # [row, column]
    slice_thickness = None

    for dcm_file in dcm_files:
        ds = dcmread(dcm_file)
        _ps = ds[0x00280030].value
        if pixel_spacing is None:
            pixel_spacing = _ps
        elif pixel_spacing != _ps:
            print(f"Image {dcm_file.name} has a different"
                  f"pixel spacing ({_ps} instead of {pixel_spacing}!")
            exit(0)
        _st = ds[0x00180050].value
        if slice_thickness is None:
            slice_thickness = _st
        elif slice_thickness != _st:
            print(f"Image {dcm_file.name} has a different"
                  f"slice thickness ({_st} instead of {slice_thickness}!")
            exit(0)

        arr = ds.pixel_array
        arr = apply_windowing(ds.pixel_array, ds)
        arr = np.divide(arr, 162 - 16)

        if volume_arr is None:
            volume_arr = np.atleast_3d(arr)
        else:
            volume_arr = np.append(volume_arr, np.atleast_3d(arr), axis=2)

    if pixel_spacing is None:
        print("No pixel spacing was defined")
        exit(0)
    if slice_thickness is None:
        print("No slice thickness was defined")
        exit(0)
    if volume_arr is None:
        print("No data was read.")
        exit(0)

    print(np.shape(volume_arr))

    if input_axis == "sagittal":
        sum_arr = np.sum(volume_arr, axis=2)
        output_spacing = [pixel_spacing[0], pixel_spacing[1]]
        scale_pixels = round(10 / pixel_spacing[0])
    elif input_axis == "coronal":
        sum_arr = np.sum(volume_arr, axis=1)
        output_spacing = [pixel_spacing[0], slice_thickness]
        scale_pixels = round(10 / pixel_spacing[0])
    elif input_axis == "transverse":
        sum_arr = np.sum(volume_arr, axis=1)
        output_spacing = [slice_thickness, pixel_spacing[0]]
        scale_pixels = round(10 / slice_thickness)
    else:
        print(
            f'Unsupported axis "{input_axis}", supported axis are sagittal, coronal or transverse.')
        exit(0)

    sum_arr = np.interp(
        sum_arr,
        (sum_arr.min(), sum_arr.max()),
        (0, 2**16 - 1)
    )

    scale_column = np.array(
        10*[
            [0]*10 +
            [2**16 - 1]*scale_pixels +
            [0] * (sum_arr.shape[0]-10-scale_pixels)
        ]).transpose()

    img = np.c_[scale_column, sum_arr].astype(int)
    return img, output_spacing


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Construct cephalogram from CBCT.')
    parser.add_argument('dicom_files', type=Path, nargs='+',
                        help='Dicom files of the CBCT.')
    parser.add_argument('--output', type=Path, help='Name of the output file.')
    parser.add_argument('--input_axis', type=str,
                        help='Plane of dicom data (i.e. sagittal, coronal or transverse)',
                        default="sagittal")

    args = parser.parse_args()
    print(args)

    img, output_spacing = construct(
        args.dicom_files, input_axis=args.input_axis)

    print(output_spacing)
    pixels_per_meter = [100*10 / output_spacing[0], 100*10 / output_spacing[1]]
    print(pixels_per_meter)

    if not args.output:
        plt.imshow(img, cmap="gray")
        plt.show()
    else:
        with open(args.output, 'wb') as f:
            writer = png.Writer(width=img.shape[1],
                                height=img.shape[0],
                                bitdepth=16,
                                greyscale=True,
                                x_pixels_per_unit=int(pixels_per_meter[1]),
                                y_pixels_per_unit=int(pixels_per_meter[0]),
                                unit_is_meter=True)
            writer.write(f, img)
