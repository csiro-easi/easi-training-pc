#!/bin/bash
for j in h{30..30}v{12..12};
  do python3 modisprepare.py --output ~/output/indexed_datasets/modis/MCD43A4.$j.yaml /data/modis/lpdaac-tiles-c6/MCD43A4.006/*/*$j*xml;
      echo "completed $j";
done;    