#!/usr/bin/python

def random_sample_from_masked_array(masked, nb_sample):
    """ Sample indices uniformely at random in a masked array, ignoring masked values.
        Returns a tuple (idx,idy)
    """
    import numpy as np
     #Assign False = 0, True = 1
    weights =~ masked.mask + 0
    normalized = weights.ravel()/float(weights.sum())
    index = np.random.choice(
        masked.size,
        size=nb_sample,
        replace=False,
        p=normalized
    )
    idy, idx = np.unravel_index(index, masked.shape)
    return idx, idy

def uniform_integer(min, max):
    import random
    print(random.randint(int(min), int(max)))

def uniform_real(min, max):
    import random
    print(random.uniform(float(min), float(max)))

def uniform_latlon(raster_path, band):
    from os.path import exists
    import rasterio
    assert exists(raster_path), 'File doest not exists:' + raster_path
    assert band >= 0, 'Band index must be integer >= 0'

    with rasterio.open(raster_path) as src:
        masked = src.read(1, masked=True)
        assert band < src.count, 'Dataset has only' + src.count + 'bands. Can not sample band index ' + band
        nb_sample = 1
        cols, rows = random_sample_from_masked_array(masked, nb_sample)
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
