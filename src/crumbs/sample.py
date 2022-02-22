#!/usr/bin/python

def uniform_integer(min, max):
    import random
    print(random.randint(int(min), int(max)))

def uniform_real(min, max):
    import random
    print(random.uniform(float(min), float(max)))

def uniform_latlon(raster_path, band):
    from raster_utils import random_sample_from_masked_array
    from os.path import exists
    import rasterio
    assert exists(raster_path), 'File doest not exists:' + raster_path
    assert band >= 0, 'Band index must be integer >= 0'

    with rasterio.open(raster_path) as src:
        masked = src.read(1, masked=True)
        assert band < src.count, 'Dataset has only' + src.count + 'bands. Can not sample band index ' + band
        nb_sample = 1
        cols, rows = raster_utils.random_sample_from_masked_array(masked, nb_sample)
        xs, ys = rasterio.transform.xy(src.transform, rows, cols)

    latlon = list(ys, xs)
    print(latlon)

commands = {
    'uniform_integer': uniform_integer,
    'uniform_real': uniform_real,
    'uniform_latlon': uniform_latlon
}

if __name__ == '__main__':
    import sys
    command = os.path.basename(sys.argv[1])
    if command in commands:
        commands[command](*sys.argv[2:])
