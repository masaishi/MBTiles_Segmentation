import argparse
import os
import random
import shutil
import glob
from PIL import Image, ImageDraw

from MBTiles_Segmentation import MBTilesHandler 

DEFAULT_COLOR_MAPPING = {
	'minor': '#FF5733',    # Red
	'service': '#3399FF',  # Blue
	'tertiary': '#33FF57', # Green
	'rail': '#FF33FF',     # Magenta
	'primary': '#FF9900',  # Orange
	'secondary': '#9900FF',# Purple
	'motorway': '#FF0000', # Bright Red
	'trunk': '#33FFFF',    # Cyan
	'path': '#FFFF33',     # Yellow
	'taxiway': '#33FF99',  # Teal
	'river': '#0066FF'     # Blue
}
DEFAULT_NUM_OBJS = 10

class SegDatasetCreator:
	def __init__(self, folder_path: str, mbtiles_path: str, color_mapping: dict = DEFAULT_COLOR_MAPPING, min_num_objs: int = DEFAULT_NUM_OBJS):
		self.folder_path = folder_path
		self.mbtiles_path = mbtiles_path
		self.color_mapping = color_mapping
		self.mbtiles_handler = MBTilesHandler(mbtiles_path)
		self.min_num_objs = min_num_objs

	def create_directories(self):
		if os.path.exists(self.folder_path):
			raise Exception(f"The folder already exists: {self.folder_path}")
	
		os.makedirs(self.folder_path)
		for folder in ["images", "labels"]:
			os.system(f"mkdir {self.folder_path}/{folder}")
			for name in ["train", "val"]:
				os.system(f"mkdir {self.folder_path}/{folder}/{name}")

	def create_yaml(self):
		with open(f"{self.folder_path}/dataset.yaml", "w") as f:
			f.write(f"path: {self.folder_path}\n")
			f.write(f"train: images/train\n")
			f.write(f"val: images/val\n")
			f.write(f"\n")
			f.write(f"names:\n")
			for i, class_name in enumerate(self.color_mapping.keys()):
				f.write(f"  {i}: {class_name}\n")

	def _change_color(self, color: str, amount: float) -> str:
		return color + hex(int(amount * 255))[2:].upper().zfill(2)
	
	def _draw_line(self, draw, color, coordinates):
		line_coords = [(int(x / 4), int(y / 4)) for (x, y) in coordinates]
		line_coords = [coord for coord in line_coords if coord[0] >= 0 and coord[0] <= 1024 and coord[1] >= 0 and coord[1] <= 1024]
		if len(line_coords) == 0:
			return

		for coord in line_coords:
			draw.ellipse((coord[0] - 2, coord[1] - 2, coord[0] + 2, coord[1] + 2), fill=color)
		draw.line(line_coords, fill=color, width=1)

	def create_img(self, df, output_path: str):
		img = Image.new('RGB', (1024, 1024), color='white')
		draw = ImageDraw.Draw(img)

		new_df = df[df['class'].isin(self.color_mapping.keys())]
		for idx, row in new_df.iterrows():
			if row['type'] == 'LineString':
				self._draw_line(draw, self.color_mapping[row['class']], row['coordinates'])
			elif row['type'] == 'MultiLineString':
				for line in row['coordinates']:
					self._draw_line(draw, self.color_mapping[row['class']], line)
		img.save(output_path)

	def _class_to_idx(self, class_name: str) -> int:
		for idx, name in enumerate(self.color_mapping.keys()):
			if name == class_name:
				return idx
		return -1

	def create_label(self, df, output_path: str):
		new_df = df[df['class'].isin(self.color_mapping.keys())]

		with open(output_path, 'w') as txt_file:
			for idx, row in new_df.iterrows():
				if row['type'] == 'LineString':
					coordinates = [(x / 1024, y / 1024) for (x, y) in row['coordinates']]
					coordinates = [coord for coord in coordinates if coord[0] >= 0 and coord[0] <= 1 and coord[1] >= 0 and coord[1] <= 1]
					if len(coordinates) == 0:
						continue
					txt_file.write(f"{self._class_to_idx(row['class'])} {' '.join(map(str, [c for coords in coordinates for c in coords]))}\n")
				elif row['type'] == 'MultiLineString':
					for line in row['coordinates']:
						coordinates = [(x / 1024, y / 1024) for (x, y) in line]
						coordinates = [coord for coord in coordinates if coord[0] >= 0 and coord[0] <= 1 and coord[1] >= 0 and coord[1] <= 1]
						if len(coordinates) == 0:
							continue
						txt_file.write(f"{self._class_to_idx(row['class'])} {' '.join(map(str, [c for coords in coordinates for c in coords]))}\n")
			
	def create_dataset(self, zoom_range: list[int, int] = [11, 14], each_image_num: int = 50, val_ratio: float = 0.2): 
		self.create_directories()
		self.create_yaml()

		for zoom_level in range(zoom_range[0], zoom_range[1] + 1):
			for i in range(each_image_num):
					df = self.mbtiles_handler.get_random_tile(zoom_level)
					if len(df) < self.min_num_objs:
						continue
					self.create_img(df, f"{self.folder_path}/images/train/{zoom_level}_{i}.png")
					self.create_label(df, f"{self.folder_path}/labels/train/{zoom_level}_{i}.txt")
		
		for file in random.sample(glob.glob(f"{self.folder_path}/images/train/*"), int(each_image_num * val_ratio)):
			file_name = file.split('/')[-1].split('.')[0]
			shutil.move(f"{self.folder_path}/images/train/{file_name}.png", f"{self.folder_path}/images/val/{file_name}.png")
			shutil.move(f"{self.folder_path}/labels/train/{file_name}.txt", f"{self.folder_path}/labels/val/{file_name}.txt")


def parse_args(input_args=None):
	parser = argparse.ArgumentParser(description="Segmentation Dataset Creator")
	parser.add_argument("--folder_path", type=str, default="sample/japan_tokyo_dataset", help="Path to the output folder")
	parser.add_argument("--mbtiles_path", type=str, default="sample/japan_tokyo.mbtiles", help="Path to the MBTiles file")
	parser.add_argument("--each_image_num", type=int, default=50, help="Number of images to create for each zoom level")
	parser.add_argument("--val_ratio", type=float, default=0.2, help="Validation data ratio")

	if input_args is not None:
		args = parser.parse_args(input_args)
	else:
		args = parser.parse_args()
	return args

def main():
	args = parse_args()
	creator = SegDatasetCreator(args.folder_path, args.mbtiles_path)
	creator.create_dataset(each_image_num=args.each_image_num, val_ratio=args.val_ratio)

if __name__ == "__main__":
	main()