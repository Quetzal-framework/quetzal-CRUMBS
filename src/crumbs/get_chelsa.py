import requests, os
import rasterio
from rasterio import mask as msk
import fiona
from shapely.geometry import shape, Point, Polygon
from optparse import OptionParser
from tqdm import tqdm

def to_polygon(long0, lat0, long1, lat1, margin=0.0):
    return Polygon([[long0 - margin , lat0 - margin],
                    [long1 + margin , lat0 - margin],
                    [long1 + margin , lat1 + margin],
                    [long0 - margin , lat1 + margin]])

def rewrite_clip(inputFile, shape):
    # read source
    source = rasterio.open(inputFile)
    out_image, out_transform = msk.mask(source, [shape], crop=True)
    out_meta = source.meta
    # udate metadata
    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})
    source.close()
    # remove heavy source
    os.remove(inputFile)
    # rewrite file
    with rasterio.open(inputFile, "w", **out_meta) as dest:
        dest.write(out_image)

def get_chelsa(url, output_dir):
    """downloads bio and orog variables from CHELSA-TraCE21k – 1km climate timeseries since the LG"""
    print("Downloading to", output_dir, "directory, url", url)
    try:
        # Streaming, so we can iterate over the response.
        response = requests.get(url, stream=True)
        total_size_in_bytes= int(response.headers.get('content-length', 0))
        block_size = 1024 #1 Kibibyte
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        # Retrieving the filename from the URL
        fname = ''
        if "Content-Disposition" in response.headers.keys():
            fname = re.findall("filename=(.+)", response.headers["Content-Disposition"])[0]
        else:
            fname = url.split("/")[-1]
        # now we can have a relevant filename to write to
        filename = output_dir.strip() + "/" + fname.strip()
        with open(filename, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print("ERROR, something went wrong")
        return filename
    except RequestException as e:
        print(e)





def get_chelsa_and_clip(inputFile, shapefile, margin=0.0, output_dir="chelsa"):
    """downloads bio and orog variables from CHELSA-TraCE21k – 1km climate timeseries since the LG and clip to spatial extent of sampling points"""
    print("Sampling points shapefile: ", shapefile)
    shapes = fiona.open(shapefile)
    print("schema: ", shapes.schema)
    print("bounding box before margin: ", shapes.bounds)
    bbox = to_polygon(*shapes.bounds, margin)
    print("bounding box after margin: ", bbox)
    # Using readlines()
    input = open(inputFile, 'r')
    urls = input.readlines()
    # Strips the newline character
    for url in urls:
        filename = get_chelsa(url.strip(), output_dir.strip())
        rewrite_clip(filename, bbox)


def main(argv):
    parser = OptionParser()
    parser.add_option("-i", "--input", type="str", dest="input_file", help="Input urls file")
    parser.add_option("-s", "--points", type="str", dest="points_file", help="Sampling points shapefile")
    parser.add_option("-d", "--dir", type="str", dest="output_dir", help="Output directory")
    parser.add_option("-m", "--margin", type="float", dest="margin", help="Margin around points bounding box")
    (options, args) = parser.parse_args(argv)
    return get_chelsa_and_clip(options.input_file, options.points_file, options.margin, options.output_dir)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
