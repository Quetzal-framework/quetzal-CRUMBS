def request(
        inputFile=None,
        variables=None,
        timesID=None,
        points=None,
        margin=0.0,
        world_dir='chelsa-world',
        landscape_dir='chelsa-landscape',
        geotiff='chelsa-stacked.tif',
        cleanup=False
    ) -> None:
    """
    Downloads bio and orog variables from CHELSA-TraCE21k. 1km climate timeseries since the LGM
    and crop the world files to the spatial extent of given points. Possiblly converts the output into a geotiff file
    """

    print("- Quetzal-CRUMBS - CHELSA-TraCE21k data access for iDDC modeling")

    from . utils import (
        bounds_to_polygon,
        create_folders_if_dont_exist,
        expand_bio,
        generate_urls,
        read_urls,
        retrieve_variables,
        get_filename,
        download_and_clip,
        remove_chelsa_dir_if_empty,
        sort_nicely,
        to_vrt,
        to_geotiff
    )

    if points is not None:
        bounding_box = bounds_to_polygon(points, margin)
        print('    ... rasters will be cropped to bounding box infered from points:', bounding_box)

    create_folders_if_dont_exist(world_dir, landscape_dir)

    if inputFile is None:
        variables = expand_bio(variables)
        urls = generate_urls(variables, timesID)
    else:
        urls = read_urls(inputFile)
        variables = retrieve_variables(urls)

    assert len(urls) != 0 , "no URL generated or read in file."

    from os.path import exists

    clip_files = []
    for url in urls:
        clip_file = landscape_dir / get_filename(url)
        clip_files.append(str(clip_file))
        if not exists(clip_file): download_and_clip(url, world_dir, bounding_box, clip_file, cleanup)

    if cleanup is True: remove_chelsa_dir_if_empty(world_dir)

    if geotiff is not None:
        for variable in variables:
            matching = [s for s in clip_files if variable in s]
            filename = geotiff.rsplit('.', 1)[-2]  + "_" + variable
            VRT = to_vrt(sort_nicely(matching), filename + ".vrt"  )
            to_geotiff(VRT,  filename + ".tif")

    return None
