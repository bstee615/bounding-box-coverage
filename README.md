# Tile coverage

Calculate which tiles intersect with fields.

- `reader.py`: Read geography for fields and tiles, then calculate intersections.
- `intersections.py`: Calculate the total area and unioned area of sentinel-2 tiles to see how much is overlapping.
- `Tile_Coverage_Analytics.py`: Generate a plot for the distribution of fields in tiles. `hist.png` saves a plot generated from this script on 9/27.

To get data from SSMS, run `get_customers.sql` in Data Export mode. `screenshot-delimiter.png` and `screenshot-destination.png` show the important settings.
It will export as UTF-16 Little Endian with BOM AFAICT.
