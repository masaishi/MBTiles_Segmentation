import argparse
import sqlite3
import io
import gzip
import random
import pandas as pd
import mapbox_vector_tile as mvt
from typing import Tuple, Optional, List

from MBTiles_Segmentation import geometry_to_wkt

class MBTilesHandler:
	def __init__(self, mbtile: str, drop_lines: bool = False, drop_points: bool = True,
				drop_polygons: bool = True, min_num_objs: int = 5):
		r"""Initializes a MbtileUtils object.

		Args:
				mbtile (str): The path to the mbtile file.
		"""
		self.mbtile = mbtile
		self.con = sqlite3.connect(self.mbtile)
		self.drop_lines = drop_lines
		self.drop_points = drop_points
		self.drop_polygons = drop_polygons
		self.min_num_objs = min_num_objs
	
	def _fetch_tile_data(self, zoom_level: int, tile_column: int, tile_row: int) -> Optional[tuple[bytes]]:
		query = """
		SELECT tile_data
		FROM tiles
		WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?
		"""
		cur = self.con.cursor()
		cur.execute(query, (zoom_level, tile_column, tile_row))
		return cur.fetchone()

	def _decode_tile_data(self, tile_data: bytes) -> dict:
		with gzip.open(io.BytesIO(tile_data[0]), "rb") as f:
			tile = f.read()
		return mvt.decode(tile)

	def _format_features(self, decoded_data: dict) -> pd.DataFrame:
		features = []
		for layer_name, layer_content in decoded_data.items():
			for feature in layer_content['features']:
				feature.update(feature.pop('geometry', {}))
				feature.update(feature.pop('properties', {}))
				features.append(feature)
		df = pd.DataFrame(features)
		df['geometry'] = df.apply(lambda row: geometry_to_wkt(row['type'], row['coordinates']), axis=1)
		
		if self.drop_lines:
			df = df[~df['type'].isin(['LineString', 'MultiLineString'])]
		if self.drop_points:
			df = df[~df['type'].isin(['Point', 'MultiPoint'])]
		if self.drop_polygons:
			df = df[~df['type'].isin(['Polygon', 'MultiPolygon'])]
		
		return df

	def get_zoom_minmax(self) -> Tuple[int, int]:
		cur = self.con.cursor()
		cur.execute("SELECT min(zoom_level), max(zoom_level) FROM tiles")
		return cur.fetchone()
	
	def get_column_minmax(self, zoom_level: int) -> Tuple[int, int]:
		cur = self.con.cursor()
		cur.execute("SELECT min(tile_column), max(tile_column) FROM tiles WHERE zoom_level = ?", (zoom_level,))
		return cur.fetchone()

	def get_row_minmax(self, zoom_level: int) -> Tuple[int, int]:
		cur = self.con.cursor()
		cur.execute("SELECT min(tile_row), max(tile_row) FROM tiles WHERE zoom_level = ?", (zoom_level,))
		return cur.fetchone()

	def get_tile(self, zoom_level: int, tile_column: int, tile_row: int) -> Optional[pd.DataFrame]:
		r"""Fetch and decode tile data from a SQLite database.

		Args:
				zoom_level (int): The zoom level of the tile.
				tile_column (int): The column of the tile.
				tile_row (int): The row of the tile.

		Returns:
				pd.DataFrame: A DataFrame containing the features of the tile.
		"""
		tile_data = self._fetch_tile_data(zoom_level, tile_column, tile_row)
		if tile_data is None:
			return None

		decoded_data = self._decode_tile_data(tile_data)
		return self._format_features(decoded_data)

	def get_random_tile(self, zoom_level: int, minmax_col: Optional[Tuple[int, int]] = None,
						minmax_row: Optional[Tuple[int, int]] = None) -> Optional[pd.DataFrame]:
		r"""Fetch and decode a random tile from a SQLite database.

		Args:
				zoom_level (int): The zoom level of the tile.

		Returns:
				pd.DataFrame: A DataFrame containing the features of the tile.
		"""
		if minmax_col:
			min_col, max_col = minmax_col
		else:
			min_col, max_col = self.get_column_minmax(zoom_level)
		
		if minmax_row:
			min_row, max_row = minmax_row
		else:
			min_row, max_row = self.get_row_minmax(zoom_level)
		
		tile_column = random.randint(min_col, max_col)
		tile_row = random.randint(min_row, max_row)
		df = self.get_tile(zoom_level, tile_column, tile_row)
		if df is None or len(df) < self.min_num_objs:
			return self.get_random_tile(zoom_level)
		else:
			return df
	
	def get_area_tiles(self, zoom_level_std: int, tile_column_std: int, tile_row_std: int, zoom_level: int) -> List[pd.DataFrame]:
		zoom_diff = zoom_level - zoom_level_std
		dfs = []
		for col in range(tile_column_std * (2 ** zoom_diff), (tile_column_std + 1) * (2 ** zoom_diff)):
			for row in range(tile_row_std * (2 ** zoom_diff), (tile_row_std + 1) * (2 ** zoom_diff)):
				tile_df = self.get_tile(zoom_level, col, row)
				if tile_df is None or len(tile_df) < self.min_num_objs:
					continue
				dfs.append(tile_df)
		if len(dfs) == 0:
			return None
		else:
			return dfs

def parse_args(input_args=None):
	parser = argparse.ArgumentParser(description="MBTiles Handler")
	parser.add_argument("--mbtiles_path", type=str, default="sample/japan_tokyo.mbtiles", help="Path to the MBTiles file")
	parser.add_argument("--zoom_minmax", action="store_true", help="Get zoom level min and max")
	parser.add_argument("--column_minmax", type=int, help="Get column min and max for a specific zoom level")
	parser.add_argument("--row_minmax", type=int, help="Get row min and max for a specific zoom level")
	parser.add_argument("--get_tile", nargs=3, type=int, metavar=("ZOOM", "COL", "ROW"), help="Get tile data")
	parser.add_argument("--get_random_tile", type=int, metavar="ZOOM", help="Get random tile data for a specific zoom level")
	parser.add_argument("--get_area_tiles", nargs=4, type=int, metavar=("ZOOM_STD", "COL_STD", "ROW_STD", "ZOOM"), help="Get area tiles")

	if input_args is not None:
		args = parser.parse_args(input_args)
	else:
		args = parser.parse_args()
	return args

def main():
	args = parse_args()
	mbtile_handler = MBTilesHandler(args.mbtiles_path)
	if args.zoom_minmax:
		print(mbtile_handler.get_zoom_minmax())
	elif args.column_minmax:
		print(mbtile_handler.get_column_minmax(args.column_minmax))
	elif args.row_minmax:
		print(mbtile_handler.get_row_minmax(args.row_minmax))
	elif args.get_tile:
		print(mbtile_handler.get_tile(*args.get_tile))
	elif args.get_random_tile:
		print(mbtile_handler.get_random_tile(args.get_random_tile))
	elif args.get_area_tiles:
		print(mbtile_handler.get_area_tiles(*args.get_area_tiles))

if __name__ == "__main__":
	main()