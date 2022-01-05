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
    parser.add_argument('-i', '--input_file', default='input/results-all.txt')
    parser.add_argument('-o', '--output_dir')
    parser.add_argument('-t', '--tiles_file')
    parser.add_argument('--skip_save', action='store_true')
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()

    args.input_file = Path(args.input_file)
    assert args.input_file.exists(), args.input_file

    args.output_dir = Path(args.output_dir)
    if not args.output_dir.exists():
        args.output_dir.mkdir()
        
    args.tiles_file = Path(args.tiles_file)
    assert args.tiles_file.exists(), f'Tiling grid index not found at {args.tiles_file}'
    
    return args

def load_fields(input_file, skip, nrows, column_names, delimiter='\t', encoding='utf-16', filter_fn=None):
    """Load field boundaries"""
    # Expects TSV (tab-separated values) data in the following form: FieldId\tPolygonWKT
    # WKT coordinates are in lat/long (WGS84 which is used by most GIS software)
    df = pd.read_csv(input_file, encoding=encoding, delimiter=delimiter, skiprows=skip, nrows=nrows, names=column_names)
    df = df.dropna()
    df["FieldId"] = df["FieldId"].astype(int)
    if filter_fn is not None:
        df = filter_fn(df)
    print('Parsing WKT...')
    gdf = gpd.GeoDataFrame(df, crs='EPSG:4326', geometry=gpd.GeoSeries.from_wkt(df["PolygonWKT"]))
    print(len(gdf), 'fields')
    return gdf

def load_tiles(input_file):
    """Load Sentinel-2 tiles"""
    # WKT coordinates are in lat/long (WGS84 which is used by most GIS software)
    print('Loading tiles from', input_file)
    if input_file.suffix == '.kml':
        gdf = gpd.read_file(input_file, driver='KML', crs='EPSG:4326')
    if input_file.suffix == '.json':
        gdf = gpd.read_file(input_file, driver='GeoJSON', crs='EPSG:4326')
    elif input_file.suffix == '.shp':
        gdf = gpd.read_file(input_file, crs='EPSG:4326')
    else:
        raise NotImplementedError(input_file.suffix)
    gdf = gdf.rename(columns={"Name": "TileName"})
    print(len(gdf), 'tiles')
    return gdf

if __name__ == '__main__':
    args = parse_args()

    # Add driver to export KML
    # KML can be displayed in Google Earth
    fiona.supported_drivers['KML'] = 'rw'
    gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'

    tile_df = load_tiles(args.tiles_file)

    skip = 1  # Skip header by default
    max_rows_per_chunk = 10000
    all_tilename_fieldid = None
    all_tilename_geometry = None
    i = 0
    with open(args.input_file, encoding='utf-16') as f:
        column_names = f.readline().strip().split('\t')
    print('Loading file', args.input_file)
    print('Max chunk size', max_rows_per_chunk)
    while True:
        print('Iteration', i)
        print('Skip', skip)
        fields_df = load_fields(args.input_file, skip, max_rows_per_chunk, column_names)
        if len(fields_df) == 0:
            print('Done')
            break
        skip += len(fields_df)
        join = gpd.sjoin(tile_df, fields_df, how="inner", op='intersects')
        print(len(join), 'rows in join')

        join_tilename_fieldid = join[["TileName", "FieldId"]].drop_duplicates()
        if all_tilename_fieldid is None:
            all_tilename_fieldid = join_tilename_fieldid
        else:
            all_tilename_fieldid = pd.concat([all_tilename_fieldid, join_tilename_fieldid]).drop_duplicates()
        
        join_tilename_geometry = join[["TileName", "geometry"]].drop_duplicates()
        if all_tilename_geometry is None:
            all_tilename_geometry = join_tilename_geometry
        else:
            all_tilename_geometry = pd.concat([all_tilename_geometry, join_tilename_geometry]).drop_duplicates()
        
        print(len(all_tilename_fieldid), 'tile-field pairs')
        print(len(all_tilename_geometry), 'unique tile geometry')

        del fields_df
        del join
        del join_tilename_geometry
        del join_tilename_fieldid
        i += 1
        if args.test:
            break

    if not args.skip_save:
        all_tilename_fieldid["FieldId"] = pd.to_numeric(all_tilename_fieldid["FieldId"])
        all_tilename_fieldid.to_csv(args.output_dir / 'tiles_to_fields.csv')
        all_tilename_geometry.to_file(args.output_dir / 'covering_tiles.json', driver='GeoJSON')
        all_tilename_geometry.to_file(args.output_dir / f'covering_tiles.kml', driver='KML')
        join_counts = all_tilename_fieldid.groupby(['TileName']).size().reset_index()
        join_counts.to_csv(args.output_dir / 'counts.csv')
