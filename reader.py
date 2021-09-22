from io import StringIO
import pandas as pd
from osgeo import ogr
import tqdm
import json
import matplotlib.pyplot as plt
import fiona

fiona.supported_drivers['KML'] = 'rw'

filename = 'results-1000.txt'
df = pd.read_csv(filename, encoding='utf-16', delimiter='\t')
print(df.columns)
print('Values of IsBoundingBox:', df["IsBoundingBox"].value_counts())

# with open('sentinel-2-tiling-grid/sentinel-2-tiling-grid.geojson') as f:
#     sentinel_2_grid = ogr.CreateGeometryFromJson(f.read())
# print(sentinel_2_grid)
# file = ogr.Open("Sentinel-2-Shapefile-Index/sentinel_2_index_shapefile.shp")
# shape = file.GetLayer(0)
# #first feature of the shapefile
# feature = shape.GetFeature(0)
# first = feature.ExportToJson()
# with open('results-grid.geojson', 'w') as f:
#     f.write(first)
import geopandas as gpd
shapefile = gpd.read_file("Sentinel-2-Shapefile-Index/sentinel_2_index_shapefile.shp", crs='EPSG:4326')
# print(shapefile)
# shapefile.head().plot(cmap='tab20b')
# shapefile.plot(cmap='tab20b')
# plt.savefig('plot.png')

df = gpd.GeoDataFrame(df, crs='EPSG:4326', geometry=gpd.GeoSeries.from_wkt(df["PolygonWKT"]))
# print(df)
print(len(shapefile), 'tiles')
print(len(df), 'fields')
# df.head(25).plot(cmap='tab20b')
# plt.savefig('plot.png')

join = gpd.sjoin(shapefile, df, how="inner", op='intersects')
print(len(join), 'joined results')
gjoin = join.groupby('Name')
print(len(gjoin), 'unique tiles')

counts = join.groupby('Name').size().reset_index(name='counts')
counts.to_csv('counts.csv')

join.to_file('join.kml', driver='KML')

# geomcol =  ogr.Geometry(ogr.wkbGeometryCollection)
# for i, row in tqdm.tqdm(list(df.iterrows())):
#     is_box = row["IsBoundingBox"]
#     wkt = row["Polygon"]
#     poly = ogr.CreateGeometryFromWkt("POLYGON ((-91.443026396117133 43.066392969633611, -91.443026396117133 43.073219630727273, -91.451884627529083 43.073219630727273, -91.451884627529083 43.066392969633611, -91.443026396117133 43.066392969633611))")
#     if is_box == 0:
#         poly = poly.Boundary()
#     geomcol.AddGeometry(poly)


# output = geomcol.ExportToKML()
# out_filename = 'results-1000.kml'
# output = geomcol.ExportToJson()
# out_filename = 'results-1000.json'
# with open(out_filename, 'w') as f:
#     f.write(output)
