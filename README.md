# Tile coverage

Calculate which tiles intersect with fields where a field can be any polygon.

- `reader.py`: Read geography for fields and tiles, then calculate intersections.
- `intersections.py`: Calculate the total area and unioned area of sentinel-2 tiles to see how much is overlapping.
- `Tile_Coverage_Analytics.py`: Generate a plot for the distribution of fields in tiles. `hist.png` saves a plot generated from this script on 9/27.

Data was queried from the database using [SSMS Export Wizard](https://docs.microsoft.com/en-us/sql/integration-services/import-export-data/import-and-export-data-with-the-sql-server-import-and-export-wizard). To get data from SSMS, run `get_customers.sql` on the database using the Export Wizard and save to a file. `screenshot-delimiter.png` and `screenshot-destination.png` show the important settings.
It will export as UTF-16 Little Endian with BOM AFAICT.
