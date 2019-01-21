# coding=utf-8
"""
Ingest data from the command-line.
"""
from __future__ import absolute_import, division

import logging
import uuid
from xml.etree import ElementTree
import re
from pathlib import Path
import yaml
from dateutil import parser
from datetime import timedelta
import datetime
import rasterio.warp
import click
from osgeo import osr
import os
# image boundary imports
import rasterio
from rasterio.errors import RasterioIOError
import rasterio.features
import shapely.affinity
import shapely.geometry
import shapely.ops
import numpy as np
import time
from shapely import speedups
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon

import pprint
import multiprocess as mp


# IMAGE BOUNDARY CODE


def safe_valid_region(images, mask_value=None):
    try:
        return valid_region(images, mask_value)
    except (OSError, RasterioIOError):
        return None


def valid_region(images, mask_value=None):
    mask = None

    for fname in [images[0]]:
        # ensure formats match
        with rasterio.open(str(fname), 'r') as ds:
            transform = ds.transform
            img = ds.read(1)

            if mask_value is not None:
                new_mask = img & mask_value == mask_value
            else:
                new_mask = img != ds.nodata
            if mask is None:
                mask = new_mask
            else:
                mask |= new_mask

    nrows, ncols = mask.shape

    idx = np.nonzero(mask)
    pts = np.transpose(np.asarray([idx[0],idx[1]]))
    hull = ConvexHull(pts)

    pts = pts[hull.vertices,:]
    pts = pts.tolist()

    poly = Polygon([[p[1], p[0]] for p in pts])

    geom = poly

    # buffer by 1 pixel
    geom = geom.buffer(2, join_style=3, cap_style=3)

    # simplify with 1 pixel radius
    geom = geom.simplify(1)

    # intersect with image bounding box
    geom = geom.intersection(shapely.geometry.box(0, 0, mask.shape[1], mask.shape[0]))

    # transform from pixel space into CRS space
    geom = shapely.affinity.affine_transform(geom, (transform.a, transform.b, transform.d, transform.e, transform.xoff,
                                                    transform.yoff))

    output = shapely.geometry.mapping(geom)
    output['coordinates'] = _to_lists(output['coordinates'])
    return output


def _to_lists(x):
    """
    Returns lists of lists when given tuples of tuples
    """
    if isinstance(x, tuple):
        return [_to_lists(el) for el in x]

    return x


# END IMAGE BOUNDARY CODE

def band_name(sat, path):

    # MCD43A4.006_Nadir_Reflectance_Band1_2000091.tif
    # MCD43A4.006_BRDF_Albedo_Band_Mandatory_Quality_Band1_2000091.tif

    fname = path.stem
    fname = fname.lower().replace('reflectance', 'sr').replace('quality', 'qa')
    bname = re.findall('.._band.',fname)[-1]

    return bname


def get_projection(path):
    with rasterio.open(str(path)) as img:
        left, bottom, right, top = img.bounds
        return {
            'spatial_reference': str(str(getattr(img, 'crs_wkt', None) or img.crs.wkt)),
            'geo_ref_points': {
                'ul': {
                    'x': left,
                    'y': top
                },
                'ur': {
                    'x': right,
                    'y': top
                },
                'll': {
                    'x': left,
                    'y': bottom
                },
                'lr': {
                    'x': right,
                    'y': bottom
                },
            }
        }


def get_coords(geo_ref_points, spatial_ref):
    spatial_ref = osr.SpatialReference(spatial_ref)
    t = osr.CoordinateTransformation(spatial_ref, spatial_ref.CloneGeogCS())

    def transform(p):
        lon, lat, z = t.TransformPoint(p['x'], p['y'])
        return {'lon': lon, 'lat': lat}

    return {key: transform(p) for key, p in geo_ref_points.items()}


def populate_coord(doc):
    proj = doc['grid_spatial']['projection']
    doc['extent']['coord'] = get_coords(proj['geo_ref_points'], proj['spatial_reference'])


def crazy_parse(timestr):
    try:
        return parser.parse(timestr)
    except ValueError:
        if not timestr[-2:] == "60":
            raise
        return parser.parse(timestr[:-2] + '00') + timedelta(minutes=1)


def prep_dataset(fields, path):

    processing_level = 'MCD43A4.006'
    product_type = 'MCD43A4.006'
    satellite = 'TERRA/AQUA'
    instrument = 'MODIS'
    ground_station = 'NA'

    #acquisition_date = doc.find('.//acquisition_date').text.replace("-", "")
    #scene_center_time = doc.find('.//scene_center_time').text[:8]
    #center_dt = crazy_parse(acquisition_date + "T" + scene_center_time)
    #aos = crazy_parse(acquisition_date + "T" + scene_center_time) - timedelta(seconds=(24 / 2))
    #los = aos + timedelta(seconds=24)

    # getting the list of all images
    images_list = []
    for file in os.listdir(str(path)):
        if file.endswith(".tif") and ("band" in file.lower()):
            images_list.append(os.path.join(str(path), file))

    if len(images_list) == 0:
        return

    acqdate = (images_list[0].split('_')[-1]).split('.tif')[0]
    yyyymmdd =  datetime.datetime(int(acqdate[0:4]), 1, 1) + datetime.timedelta(int(acqdate[4:]) - 1)
    creation_dt = yyyymmdd.strftime('%Y-%m-%d %H:%M:%S')

    aos = creation_dt
    los = creation_dt

    start_time = aos
    end_time = los

    # getting the paths to each of the band datasets
    images = {band_name(satellite, im_path): {'path': str(im_path.relative_to(path))} for im_path in path.glob('*.tif')}

    #getting the projection details
    projdict = get_projection(path / next(iter(images.values()))['path'])

    projdict['valid_data'] = safe_valid_region(images_list)

    # generating the .yaml document
    doc = {
        'id': str(uuid.uuid4()),
        'processing_level': processing_level,
        'product_type': product_type,
        'creation_dt': creation_dt,
        'platform': {
            'code': satellite
        },
        'instrument': {
            'name': instrument
        },
        'acquisition': {
            'groundstation': {
                'code': ground_station,
            },
            'aos': aos,
            'los': los,
        },
        'extent': {
            'from_dt': creation_dt,
            'to_dt': creation_dt,
            'center_dt': creation_dt
        },
        'format': {
            'name': 'GeoTiff'
        },
        'grid_spatial': {
            'projection': projdict
        },
        'image': {

            'bands': images
        },
        'lineage': {
            'source_datasets': {}
        }
    }

    populate_coord(doc)
    return doc


def prepare_datasets(nbar_path):

    # format of local file name
    # MCD43A4.006_Nadir_Reflectance_Band1_2000091.tif
    # MCD43A4.006_BRDF_Albedo_Band_Mandatory_Quality_Band1_2000091.tif

    fields = {}

    nbar = prep_dataset(fields, nbar_path)
    return (nbar, nbar_path)

def create_doc_dataset(dataset):

    print ('Processing ' + dataset)
    path = Path(dataset)

    logging.info("Processing %s", path)
    documents = prepare_datasets(path)

    dataset, folder = documents
    yaml_path = str(folder.joinpath('agdc-metadata.yaml'))
    logging.info("Writing %s", yaml_path)
    with open(yaml_path, 'w') as stream:
        yaml.dump(dataset, stream)

    return


@click.command(help="Prepare MODIS datasets for ingestion into the Data Cube.")
@click.argument('datasets', type=click.Path(exists=True, readable=True, writable=True), nargs=-1)
def main(datasets):


    t0 = time.time()

    cores = 18 # mp.cpu_count()

    #datasets = ['/g/data1/k88/MODIS_C/MCD43A4.006/2000091/']i
    pool = mp.Pool(processes=cores)

    res = pool.map(create_doc_dataset, datasets)

    t1 = time.time()

    print('Processed in {0:.1f} seconds'.format(t1-t0))

    return


if __name__ == "__main__":
    main()
