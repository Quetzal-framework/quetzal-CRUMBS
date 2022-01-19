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

def generate_url(variables, timesID):
    """ Generate the expected CHELSA TraCE21k urls given the variables and the time IDS to retrieve.
    """
    implemented = ['dem', 'glz', *['bio' + str(i) for i in range(1, 19,1)]]
    if(set(variables).issubset(set(implemented))):
        if(set('dem').issubset(set(variables))):
            for timeID in timesID :
                url = "https://os.zhdk.cloud.switch.ch/envicloud/chelsa/chelsa_V1/chelsa_trace/orog/CHELSA_TraCE21k_dem_"+ str(timeID) + "_V1.0.tif"
                yield url
        if(set('glz').issubset(set(variables))):
            for timeID in timesID :
                url = "https://os.zhdk.cloud.switch.ch/envicloud/chelsa/chelsa_V1/chelsa_trace/orog/CHELSA_TraCE21k_glz_"+ str(timeID) + "_V1.0.tif"
                yield url
        bioset = set(variables) - set(['dem','glz'])
        if( len(bioset) >= 1 ) :
            for bio in bioset:
                for timeID in timesID :
                    url = "https://os.zhdk.cloud.switch.ch/envicloud/chelsa/chelsa_V1/chelsa_trace/bio/CHELSA_TraCE21k_" + bio + "_"+ str(timeID) + "_V1.0.tif"
                    yield url
    else:
        raise ValueError(variable_string, ": not implemented. Implemented CHELSA variables are:", implemented)

def to_vrt(inputFiles, outputFile='stacked.vrt'):
    """ Converts the list of input files into an output VRT file, that can be converted to geoTiff
    """
    vrt_file = outputFile
    images = inputFiles
    gdal.BuildVRT(vrt_file, images, separate=True, callback=gdal.TermProgress_nocb)
    vrt_options = gdal.BuildVRTOptions(separate=True, callback=gdal.TermProgress_nocb, resampleAlg='average')
    my_vrt = gdal.BuildVRT(vrt_file, images , options=vrt_options)
    my_vrt = None
    return(vrt_file)

def to_geotiff(vrt, outputFile='stacked.tif'):
    """ Converts the VRT files to a geotiff file
    """
    ds = gdal.Open(vrt)
    ds = gdal.Translate(outputFile, ds)
    ds = None

def get_chelsa(inputFile, variables, timesID, points=None, margin=0.0, output_dir=None, clipped_dir=None, variable_string=None, cleanup=False):
    """ Downloads bio and orog variables from CHELSA-TraCE21k –
        1km climate timeseries since the LG and clip to spatial extent of sampling points, converting the output into a geotiff file
    """
    if(points is not None):
        shapes = fiona.open(points)
        bbox = to_polygon(*shapes.bounds, margin)

    # Creating folders if does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(clipped_dir):
        os.makedirs(clipped_dir)

    if(inputFile is not None):
        # read URLS from input file
        input = open(inputFile, 'r')
        urls = input.readlines()
    else :
        # generate url from anticipated URL CHELSA pattern
        urls = generate_url(variables, timesID)

    for url in urls:
        clipped_file = clipped_dir.strip() + "/" + url.rsplit('/', 1)[-1].strip()
        if not exists(clipped_file):
            chelsafile = get_chelsa(url.strip(), output_dir.strip())
            clip(chelsafile, bbox, clipped_file)
            if cleanup == True: os.remove(chelsafile)

    # Removing empty directory if cleanup
    if len(os.listdir(output_dir)) == 0:
        os.rmdir(output_dir)
    else:
        print("Directory", output_dir, "is not empty and will not be deleted.")

    clipped_files = next(walk(clipped_dir), (None, None, []))[2]  # [] if no file
    images = [output_dir + '/' + str(f) for f in clipped_files]
    to_geotiff(to_vrt(sort_nicely(images)))

def main(argv):
    parser = OptionParser()
    parser.add_option("-i", "--input", type="str", dest="input", help="Input urls file, one url by line")
    parser.add_option("-v", "--variables", nargs="*", default=['dem'], type="str", dest="variables", help="CHELSA_TraCE21k_ variables to download: dem, glz, bio1-19")
    parser.add_option("-t", "--timesID", nargs="*", default=range(20,-200,-1), type="int", dest="timesID", help="CHELSA_TraCE21k_ times IDs to download: 20 (present) to -200 (LGM)")
    parser.add_option("-p", "--points", type="str", dest="points", default=None, help="Shapefile of spatial points around which a boundin box will be drawn to clip the CHELSA tif. Usually DNA samples coordinates, but can be a box too.")
    parser.add_option("-m", "--margin", type="float", dest="margin", default=0.0, help="Margin to add around the bounding box, in degrees")
    parser.add_option("-d", "--dir", type="str", dest="output_dir", default = "CHELSA", help="Output directory for CHELSA files")
    parser.add_option("-c", "--clipped_dir", type="str", dest="clipped_dir", default = "CHELSA_clipped", help="Output directory for clipped CHELSA files")
    parser.add_option("--cleanup", dest="cleanup", default = False, action = 'store_true', help="Remove downloaded CHELSA files, but keep clipped files")
    parser.add_option("--no-cleanup", dest="cleanup", action = 'store_false', help="Keep downloaded CHELSA files on disk")
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
            cleanup = options.cleanup)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
