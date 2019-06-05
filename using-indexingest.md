# Guide to Index, Prepare and Ingest for the Open Data Cube

This guide summarises:
- The index/prepare/ingest requirements for ODC
- Where to find existing index/prepare/ingest definitions
- How to write your own index/prepare/ingest definitions
- How to contribute your index/prepare/ingest definitions to the community

## Resources

* Diagramatic overview: https://datacube-core.readthedocs.io/en/latest/ops/overview.html
* Index: https://datacube-core.readthedocs.io/en/latest/ops/indexing.html
* Prepare: https://datacube-core.readthedocs.io/en/latest/ops/prepare_scripts.html
* Ingest: https://datacube-core.readthedocs.io/en/latest/ops/ingest.html

## Overview

There are three main components to index/prepare/ingext requirements for ODC.

1. Index - create a product definition that describes elements common to all data files and defines a product name that will be referenced in the datacube application code. Different product definitions will be required for differently formatted or structured data files.
> Indexing is for the 'raw' format as available from download or a data custodian. This includes initial product definition.
2. Prepare - create a (python) script that extracts file-specific information for each data file. Record this per-file information in a long structure YAML-format file, which is then indexed into the database against a specific product definition.
> Preparing is reading the raw format files to extract dimension extents and relevant file-specific metadata.
3. Ingest - optionally create a format tranformation definition that describes how to reformat and indexed dataset into a new format (copy). Ingesting is intended to be used to create data stuctures that are computationally preferred for a specific set of applications. An ingested datset creates a new product in the datacube. 
> Ingesting is for creating computional data structures from indexed data. This creates a new product.

## Index

### Product definition
Define metadata common to all the datasets belonging to the products

> These fields come from older notes and need to validated

* name
* description
* metadata_type
* metadata
    * [no info on the format of this]
    * used during indexing (if --auto-match options is used) to match datasets to products.
    * Platform: code
    * Instrument: name
    * Product_type
    * Format: name
* storage (optional)
    * common storage attributes of all the datasets. Optional but recommended
    * [ceos] used in the ingestion process to specify projection/tiling/file type
    * crs: EPSG:[code] or WKT string.
* resolution: latitude, longitude if the projection is geographic and x, y otherwise
* measurements
    * name
    * units
    * dtype: (u)int(8,16,32,64), float32, float64
    * nodata
    * spectral_definition (optional)
        * wavelength: [410, 411, 412]
        * response: [0.0261, 0.029, 0.0318]
    * flags_definition (optional)

Examples:
- https://github.com/opendatacube/datacube-core/blob/develop/datacube/model/schema/dataset-type-schema.yaml
- datacube-core > docs/config_samples/dataset_types

```
datacube product add [path-to-product-definition-yaml]
```

## Prepare

> These fields have been partly validated against the data.dea.gov.au example below.

* id: UUID
* creation_dt
* product_type: ard
* platform: code  # Must match with product definition
* instrument: name  # Must match with product definition
* extent
    * center_dt
    * coord
        * ll
            * lat
            * lon
        * lr
            * lat
            * lon
        * ul
            * lat
            * lon
        * ur
            * lat
            * lon
* format: ‘NetCDF’, ‘HDF’, 'GeoTiff'
* grid_spatial
    * projection
        * geo_ref_points
            * ll
                * x
                * y
            * lr
                * x
                * y
            * ul
                * x
                * y
            * ur
                * x
                * y
        * spatial_reference: PROJCS[...]
        * valid_data (optional): Only needs to be roughly correct. Prefer simpler geometry over accuracy.
            * coordinates
            * [list of points]
            * type" Polygon
* image
    * bands
        * "band_name_1"
            * layer: 1
            * path: relative file path
        * "band_name_2"
            * layer: 1
            * path: relative file path
* lineage
    * source_datasets
        * level1:
            * id: b7d01e8c-1cd2-11e6-b546-a0000100fe80
            * product_type: level1
            * creation_dt: 2016-05-18 08:09:34
            * platform: { code: LANDSAT_5 }
            * instrument: { name: TM }
            * format: { name: GeoTIFF }
            * ...
    * algorithm (optional)
        * name: brdf
        * version: '2.0'
        * doi: http://dx.doi.org/10.1109/JSTARS.2010.2042281
    * parameters:
        * aerosol: 0.078565
    * machine (optional)
        * hostname: r2200
        * uname: 'Linux r2200 2.6.32-573.22.1.el6.x86_64 #1 SMP Wed Mar 23 03:35:39 UTC 2016 x86_64'
        * runtime_id: d052fcb0-1ccb-11e6-b546-a0000100fe80
        * software_versions:
            * eodatasets:
                * repo_url: https://github.com/GeoscienceAustralia/eo-datasets.git
                * version: '0.4'
    * ancillary (optional)
        * ephemeris:
* algorithm_information (check how/if this is diffeent to lineage)
* processing_level: Level-2
* system_information
* title_id

Examples:
- Prepare script(s)
- https://github.com/opendatacube/datacube-core/blob/develop/datacube/model/schema/dataset-type-schema.yaml
- https://data.dea.ga.gov.au/L2/sentinel-2-nrt/S2MSIARD/2019-06-04/S2A_OPER_MSI_ARD_TL_EPAE_20190604T011841_A020619_T56LQM_N02.07/ARD-METADATA.yaml

A prepare script  creates yaml(s) in the path-to-dataset directory.
```
datacube dataset add --auto-match <path-to-dataset>
```

Notes:
- Field names with spaces or hyphens are generally discouraged, i.e. "sentinel-1", "ingestion Date"
- Paths to the measurement data can be relative; this enables moving of datasets to new locations easier, i.e. no re-creation of the product yaml

## Ingest

> These fields come from older notes and need to validated

* source_type
* output_type: human-readable identifer, must be unique
* description (optional)
* location: directory to write output storage units.
* file_path_template
    * HARD_CODED!!!
    * time_format = '%Y%m%d%H%M%S%f'
        * tile_index=tile_index,
        * start_time=to_datetime(sources.time.values[0]).strftime(time_format),
        * end_time=to_datetime(sources.time.values[-1]).strftime(time_format),
        * version==config['taskfile_version']
* global_attributes
* storage
    * driver
    * crs: EPSG code or WKT.
    * tile_size
    * origin: If coordinates are for top-left corner, ensure that the latitude or y dimension of tile_size is negative so tile indexes count downward.
    * resolution: Negative values flip the axis.
    * chunking
    * dimension_order: currently ignored
* measurements: Mapping of the input measurement names as specified in the Dataset Metadata Document to the per-measurement ingestion parameters
    * dtype: (u)int(8,16,32,64), float32, float64
    * resampling_method: nearest, cubic, bilinear, cubic_spline, lanczos, average.
    * name: NetCDF variable
    * nodata (optional)

Examples:
- docs/config_samples

```
datacube ingest -c [configuration_file]
```

