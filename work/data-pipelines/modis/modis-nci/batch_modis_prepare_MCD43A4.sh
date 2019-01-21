#!/bin/bash
for j in h{27..32}v{10..13};
  do python3 modisprepare.py --output /g/data/v10/AGDCv2/indexed_datasets/modis/MCD43A4.$j.yaml /g/data/u39/public/data/modis/lpdaac-tiles-c6/MCD43A4.006/*/*$j*xml;
      echo "completed $j";
done;    