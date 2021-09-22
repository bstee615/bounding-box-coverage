"""
Read geographic data for fields and tiles.
Determine how many tiles are needed to cover all the fields.
Assume all coordinates are in EPSG:4326 (World Geodetic System 1984, WGS84) lat/long.
"""

import pandas as pd
import fiona
import argparse
from pathlib import Path
import geopandas as gpd

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', default='input/results-1000.txt')
    parser.add_argument('-o', '--output_dir', default='output')
    parser.add_argument('-s', '--shapefile_dir', default='Sentinel-2-Shapefile-Index')
    args = parser.parse_args()

    args.input_file = Path(args.input_file)
    assert args.input_file.exists(), args.input_file

    args.output_dir = Path(args.output_dir)
    if not args.output_dir.exists():
        args.output_dir.mkdir()
        
    args.shapefile_dir = Path(args.shapefile_dir)
    assert args.shapefile_dir.exists(), f'Tiling grid index not found at {args.shapefile_dir}, please get it from https://github.com/justinelliotmeyers/Sentinel-2-Shapefile-Index.git'
    
    return args

def load_fields(input_file):
    """Load field boundaries"""
    # Expects TSV (tab-separated values) data in the following form:
    # FieldId	IsBoundingBox	PolygonWKT
    # <int>	    <1 or 0>    	<WKT string>
    print('Loading fields from', input_file)
    df = pd.read_csv(input_file, encoding='utf-16', delimiter='\t')
    gdf = gpd.GeoDataFrame(df, crs='EPSG:4326', geometry=gpd.GeoSeries.from_wkt(df["PolygonWKT"]))
    print(len(gdf), 'fields')
    return gdf

def load_tiles(input_file):
    """Load Sentinel-2 tiles"""
    print('Loading tiles from', input_file)
    gdf = gpd.read_file(input_file, crs='EPSG:4326')
    print(len(gdf), 'tiles')
    return gdf

if __name__ == '__main__':
    args = parse_args()

    # Add driver to export KML
    # KML can be displayed in Google Earth
    fiona.supported_drivers['KML'] = 'rw'

    fields_df = load_fields(args.input_file)
    tile_df = load_tiles(args.shapefile_dir / "sentinel_2_index_shapefile.shp")

    print('Joining...')
    join = gpd.sjoin(tile_df, fields_df, how="inner", op='intersects')
    join_by_name = join.groupby('Name')
    join_counts = join_by_name.size().reset_index(name='counts').sort_values(by=['Name'])
    print(len(join), 'joined results')
    print(len(join_by_name), 'unique tiles')

    join_counts.to_csv(args.output_dir / 'counts.csv')
    join.to_file(args.output_dir / 'covering_tiles.kml', driver='KML')
