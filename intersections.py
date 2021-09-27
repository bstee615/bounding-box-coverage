
import geopandas as gpd
import pandas as pd
from reader import load_tiles

tiles_df = load_tiles('Sentinel-2-Shapefile-Index/sentinel_2_index_shapefile.shp')
tiles_df = tiles_df.to_crs('EPSG:3857')
assert tiles_df.crs.to_dict()['units'] == 'm'
print(len(tiles_df), 'tiles')
counts_df = pd.read_csv('output/counts.csv')
join = pd.merge(counts_df, tiles_df, left_on='Name', right_on='Name', how='inner')
print(len(join), 'rows in join')

tiles_area = tiles_df.area.sum()
print('Total Tile Area:', tiles_area / 1e6, 'km2')
union_tiles_df = tiles_df.unary_union
union_tiles_area = union_tiles_df.area
print(f'Union area: {union_tiles_area / 1e6} km2 ({union_tiles_area/tiles_area*100:.2f}% of total)')
