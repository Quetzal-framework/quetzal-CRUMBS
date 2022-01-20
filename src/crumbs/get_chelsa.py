import requests
import os
import rasterio
from rasterio import mask as msk
import fiona
from shapely.geometry import shape, Point, Polygon
from optparse import OptionParser
from tqdm import tqdm
from osgeo import gdal
from pathlib import Path;
from os import walk
from os.path import exists
import re
import glob

def tryfloat(s):
    try:
        return float(s)
    except:
        return s

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryfloat(c) for c in re.split('_(-*\d+)_' , s) ]

def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=alphanum_key)
    return l

def to_polygon(long0, lat0, long1, lat1, margin=0.0):
    """ Convert the given points into a polygon, adding a margin.
    """
    return Polygon([[long0 - margin , lat0 - margin],
                    [long1 + margin , lat0 - margin],
                    [long1 + margin , lat1 + margin],
                    [long0 - margin , lat1 + margin]])

def clip(inputFile, shape, outputFile):
    """ Clip the input file by the shape given, saving the output file
    """
    # read source
    source = rasterio.open(inputFile)
    out_image, out_transform = msk.mask(source, [shape], crop=True)
    out_meta = source.meta
    # udate metadata
    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})

    with rasterio.open(outputFile, "w", **out_meta) as dest:
        dest.write(out_image)


def resume_download(fileurl, resume_byte_pos):
    """ Resume the download of the file given its url
    """
    resume_header = {'Range': 'bytes=%d-' % resume_byte_pos}
    return requests.get(fileurl, headers=resume_header, stream=True,  verify=True, allow_redirects=True)

def get_chelsa(url, output_dir):
    """ Downloads bio and orog variables from CHELSA-TraCE21k – 1km climate timeseries since the LG
    """
    #  Retrievethe filename from the URL so we have a local file to write to
    filename = output_dir.strip() + "/" + url.rsplit('/', 1)[-1].strip()
    path = Path(filename)
    resume_byte = path.stat().st_size

    try:
        with open(filename, 'ab') as file:
            response = resume_download(url, resume_byte)

            # progress bar
            total_size_in_bytes= int(response.headers.get('content-length', 0))
            block_size = 1024 #1 Kibibyte
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

            # download progress
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)

        progress_bar.close()

        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print("ERROR, something went wrong")
        return filename
    except requests.RequestException as e:
        print(e)
    return

def generate_url(variables, timesID):
    """ Generate the expected CHELSA TraCE21k urls given the variables and the time IDS to retrieve.
    """
    urls = []
    implemented = ['dem', 'glz', *['bio' + str(i) for i in range(1, 19,1)]]
    if(set(variables).issubset(set(implemented))):
        if(set('dem').issubset(set(variables))):
            for timeID in timesID :
                url = "https://os.zhdk.cloud.switch.ch/envicloud/chelsa/chelsa_V1/chelsa_trace/orog/CHELSA_TraCE21k_dem_"+ str(timeID) + "_V1.0.tif"
                urls.append(url)
        if(set('glz').issubset(set(variables))):
            for timeID in timesID :
                url = "https://os.zhdk.cloud.switch.ch/envicloud/chelsa/chelsa_V1/chelsa_trace/orog/CHELSA_TraCE21k_glz_"+ str(timeID) + "_V1.0.tif"
                urls.append(url)
        bioset = set(variables) - set(['dem','glz'])
        if( len(bioset) >= 1 ) :
            for bio in bioset:
                for timeID in timesID :
                    url = "https://os.zhdk.cloud.switch.ch/envicloud/chelsa/chelsa_V1/chelsa_trace/bio/CHELSA_TraCE21k_" + bio + "_"+ str(timeID) + "_V1.0.tif"
                    urls.append(url)
    else:
        raise ValueError(variable_string, ": not implemented. Implemented CHELSA variables are:", implemented)
    return

def to_vrt(inputFiles, outputFile='stacked.vrt'):
    """ Converts the list of input files into an output VRT file, that can be converted to geoTiff
    """
    gdal.BuildVRT(outputFile, inputFiles, separate=True, callback=gdal.TermProgress_nocb)
    vrt_options = gdal.BuildVRTOptions(separate=True, callback=gdal.TermProgress_nocb, resampleAlg='average')
    my_vrt = gdal.BuildVRT(outputFile, inputFiles, options=vrt_options)
    my_vrt = None
    return(outputFile)

def to_geotiff(vrt, outputFile='stacked.tif'):
    """ Converts the VRT files to a geotiff file
    """
    ds = gdal.Open(vrt)
    ds = gdal.Translate(outputFile, ds)
    ds = None

def create_folders_if_dont_exist(output_dir, clipped_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(clipped_dir):
        os.makedirs(clipped_dir)
    return

def bounds_to_polygon(shapefile):
    shapes = fiona.open(points)
    bbox = to_polygon(*shapes.bounds, margin)
    return bbox

def read_urls(inputFile):
    input = open(inputFile, 'r')
    urls = input.readlines()
    return [url.strip() for url in urls]

def get_filename(url):
    #  splits the url into a list, starting from the right and get last element
    filename = url.rsplit('/', 1)[-1].strip()
    return filename

def download(url, output_dir, clip_shape, clipped_file, cleanup):
    downloaded = get_chelsa(url, output_dir)
    clip(downloaded, clip_shape, clipped_file)
    os.remove(downloaded) if cleanup
    return

def remove_empty_chelsa_dir(output_dir):
    if len(os.listdir(output_dir)) == 0:
        os.rmdir(output_dir)
    else:
        print("Directory", output_dir, "is not empty and will not be deleted.")
    return

def get_chelsa(inputFile, variables, timesID, points=None, margin=0.0, output_dir=None, clipped_dir=None, outputGeotiff=None, variable_string=None, cleanup=False):
    """ Downloads bio and orog variables from CHELSA-TraCE21k –
        1km climate timeseries since the LG and clip to spatial extent of sampling points, converting the output into a geotiff file
    """
    if points is not None bounding_box = bounds_to_polygon(points)

    create_folders_if_dont_exist(output_dir, clipped_dir):

    urls = generate_url(variables, timesID) if inputFile is None else read_urls(inputFile)

    for url in urls:
        clipped_file = clipped_dir.strip() + "/" + url.rsplit('/', 1)[-1].strip()
        print(clipped_file)
        if not exists(clipped_file):
            download(url, output_dir, bounding_box, clipped_file, cleanup)

    remove_empty_chelsa_dir(output_dir) if cleanup

    clipped_files = next(walk(clipped_dir), (None, None, []))[2]  # [] if no file
    #clipped_files = [url.rsplit('/', 1)[-1].strip() for url in generate_url(variables, timesID)]
    images = [clipped_dir + '/' + str(f) for f in clipped_files]
    to_geotiff(to_vrt(sort_nicely(images)), outputGeotiff)


def get_variables_args(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))

def get_timesID_args(option, opt, value, parser, type='int'):
    setattr(parser.values, option.dest, [int(s) for s in value.split(',')])

def main(argv):

    parser = OptionParser()

    parser.add_option("-i", "--input", type="str", dest="input", help="Input urls file, one url by line")

    parser.add_option("-v", "--variables",
                        dest="variables",
                        type='str',
                        action='callback',
                        callback=get_variables_args,
                        help="If no input given, CHELSA TraCE21k variables to download. Possible options: dem, glz, bio1 to bio19")

    parser.add_option("-t", "--timesID",
                        dest="timesID",
                        type='str',
                        action='callback',
                        callback=get_timesID_args,
                        help="CHELSA_TraCE21k_ times IDs to download. Default: 20 (present) to -200 (LGM)")

    parser.add_option("-p", "--points", type="str", dest="points", default=None, help="Shapefile of spatial points around which a bounding box will be drawn to clip the CHELSA tif. Example: all DNA samples coordinates, or 4 coordinates defining a bounding box.")
    parser.add_option("-m", "--margin", type="float", dest="margin", default=0.0, help="Margin to add around the bounding box, in degrees.")
    parser.add_option("-d", "--dir", type="str", dest="output_dir", default = "CHELSA", help="Output directory for CHELSA files. Default: CHELSA.")
    parser.add_option("-c", "--clipped_dir", type="str", dest="clipped_dir", default = "CHELSA_clipped", help="Output directory for clipped CHELSA files. Default: CHELSA_clipped.")
    parser.add_option("-o", "--output-geotiff", type="str", dest="geotiff", default = "stacked.tiff", help="Produces a geotiff that ")
    parser.add_option("--cleanup", dest="cleanup", default = False, action = 'store_true', help="Remove downloaded CHELSA files, but keep clipped files.")
    parser.add_option("--no-cleanup", dest="cleanup", action = 'store_false', help="Keep downloaded CHELSA files on disk.")
    (options, args) = parser.parse_args(argv)
    try:
        return get_chelsa(
            inputFile = options.input,
            variables = options.variables,
            timesID = options.timesID,
            points = options.points,
            margin = options.margin,
            output_dir = options.output_dir,
            clipped_dir = options.clipped_dir,
            outputGeotiff = options.geotiff,
            cleanup = options.cleanup)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
