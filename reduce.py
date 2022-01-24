import functools
import glob

import numpy
import pygeoprocessing
from osgeo import gdal

# I should really just take a look through InVEST
#  * How often do I need to operate on a single raster vs a stack of them?
#  * Can't I just use reduce directly?  Do I really need a custom reduce
#  function?

# I see python also has a functools.accumulate ... maybe there's a good way to
# apply functools.accumulate() and functools.reduce() creatively?
#  Maybe the easy thing to do would be to handle mutual nodata masking?

def raster_reduce(func, raster_path_band_list, dtype=None):
    raster_list = []
    band_list = []
    for raster_path, band_index in raster_path_band_list:
        raster = gdal.OpenEx(raster_path)
        raster_list.append(raster)
        band_list.append(raster.GetRasterBand(band_index))

    def _iterblocks_callable(array, block_data):
        return func(
            array, (band.ReadAsArray(**block_data) for band in band_list))

    # Deliberately using a generator here for iterblocks.
    return functools.reduce(
        _iterblocks_callable, (
            block_data for block_data in pygeoprocessing.iterblocks(
                raster_path_band_list[0], offset_only=True)))


def count(value, blocks):
    import pdb; pdb.set_trace()
    accumulator = numpy.zeros(next(blocks).shape, dtype=numpy.uint16)
    for block in blocks:
        valid_values = (block == 1)
        accumulator[valid_values] += 1

    value = max(value, numpy.amax(accumulator))

if __name__ == '__main__':
    raster_band_list = [
        (path, 1) for path in
        glob.glob('jades_data/hra_outputs/intermediate_outputs/file_preprocessing/base*.tif')]
    print(raster_reduce(count, raster_band_list))
