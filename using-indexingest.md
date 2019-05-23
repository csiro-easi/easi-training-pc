# Guide to Index, Prepare and Ingest for the Open Data Cube

This guide summarises:
- The index/prepare/ingest requirements for ODC
- Where to find existing index/prepare/ingest definitions
- How to write your own index/prepare/ingest definitions
- How to contribute your index/prepare/ingest definitions to the community

## Resources

Diagramatic overview: https://datacube-core.readthedocs.io/en/latest/ops/overview.html

Index: https://datacube-core.readthedocs.io/en/latest/ops/indexing.html

Prepare: https://datacube-core.readthedocs.io/en/latest/ops/prepare_scripts.html

Ingest: https://datacube-core.readthedocs.io/en/latest/ops/ingest.html

## Overview

There are three main components to index/prepare/ingext requirements for ODC.

1. Index - create a product definition that describes elements common to all data files and defines a product name that will be referenced in the datacube application code. Different product definitions will be required for differently formatted or structured data files.
2. Prepare - create a (python) script that extracts file-specific information for each data file. Record this per-file information in a long structure YAML-format file, which is then indexed into the database against a specific product definition.
3. Ingest - optionally create a format tranformation definition that describes how to reformat and indexed dataset into a new format. Ingesting is intended to be used to create data stuctures that are computationally preferred for a specific set of applications. An ingested datset creates a new product in the datacube. 

> Indexing is for the 'raw' format as available from download or a data custodian. This includes initial product definition.

> Preparing is reading the raw format files to extract dimension extents and relevant file-specific metadata.

> Ingesting is for creating computional data structures from indexed data. This creates a new product.

## Index

Examples:
- TBD

## Prepare

Examples:
- TBD

## Ingest

Examples:
- TBD

