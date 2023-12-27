<img width="800" alt="Screenshot 2023-12-26 at 3 51 44 PM" src="https://github.com/masaishi/MBTiles_Segmentation/assets/1396267/d56dd189-2ab5-4abe-aa55-f59726a610e1">

# MBTiles_Segmentation

MBTiles_Segmentation is OSS Library to make YOLO segmentation datasets from MBTiles files. This project provides tools to generate image and label data for training and evaluating segmentation models.

## Table of Contents

- [Introduction](#introduction)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [License](#license)

## Introduction

MBTiles_Segmentation provides features the extraction of vector data from MBTiles files and the creation of image-label pairs, primarily designed for training and evaluating YOLO (You Only Look Once) models.

You can download map data in the MBTiles format from various sources, including MapTiler's dataset collection (https://data.maptiler.com/downloads/planet/).

The project consists of two main components: src/mbtiles_handler.py, which enables the handling of MBTiles files, and src/seg_dataset_creator.py, which generates image and label data suitable for YOLO-based object detection tasks.

## Getting Started

The notebook that actually ran is [example/getting_started.ipynb](example/getting_started.ipynb)

Follow these steps to get started with the MBTiles_Segmentation project:

1. **Install MBTiles_Segmentation:**
	 command:
		 ```
		 pip install MBTiles_Segmentation
		 ```

2. **Download the MBTiles File:**
   - Visit the MapTiler website at [https://data.maptiler.com/downloads/asia/japan/tokyo/](https://data.maptiler.com/downloads/asia/japan/tokyo/).
   - Download the `japan_tokyo.mbtiles` file, which contains map data for Tokyo, Japan.
	 - After downloading, move the `japan_tokyo.mbtiles` file into the `sample` folder of the project.

3. **Explore MBTiles Handler:**
   Command is `seg_mbtiles_handler` to explore the contents of the MBTiles file. Below are some example commands:

	- To get information about zoom level min and max:
		```
		seg_mbtiles_handler --mbtiles_path sample/japan_tokyo.mbtiles --zoom_minmax
		```

	- To get column min and max for a specific zoom level (e.g., zoom level 12):
		```
		seg_mbtiles_handler --mbtiles_path sample/japan_tokyo.mbtiles --column_minmax 12
		```

	- To get row min and max for a specific zoom level (e.g., zoom level 12):
		```
		seg_mbtiles_handler --mbtiles_path sample/japan_tokyo.mbtiles --row_minmax 12
		```

	- To get data for a specific tile (e.g., zoom level 12, column 123, row 456):
		```
		seg_mbtiles_handler --mbtiles_path sample/japan_tokyo.mbtiles --get_tile 10 907 619
		```

	- To get random tile data for a specific zoom level (e.g., zoom level 14):
		```
		seg_mbtiles_handler --mbtiles_path sample/japan_tokyo.mbtiles --get_random_tile 14
		```

	- To get area tiles based on a standard tile and zoom level (e.g., standard zoom level 10, column 907, row 619, and target zoom level 11):
		```
		seg_mbtiles_handler --mbtiles_path sample/japan_tokyo.mbtiles --get_area_tiles 10 907 619 11
		```

4. **Generate Dataset:**
   Command is `seg_mbtiles_creator` to generate image-label pairs for training and testing semantic segmentation models. Below is an example command:

	- To create a dataset in the `sample/japan_tokyo_dataset` folder, containing images and labels for training and validation, you can run the following command:
		```
		seg_mbtiles_creator --folder_path sample/japan_tokyo_dataset --mbtiles_path sample/japan_tokyo.mbtiles
		```

	- You can also specify the number of images to create for each zoom level and the validation data ratio using the `--each_image_num` and `--val_ratio` options, respectively.

Now you are ready to explore and use the MBTiles_Segmentation project to work with MBTiles map data and create segmentation datasets for training YOLO models.

## Usage

The notebook that actually ran is [example/usage.ipynb](example/usage.ipynb)

### [`MBTilesHandler`](src/MBTiles_Segmentation/mbtiles_handler.py)

#### Initialization
To initialize an `MBTilesHandler` object, provide the path to your MBTiles file and optional configuration parameters as follows:

```python
from MBTiles_Segmentation import MBTilesHandler

mbtile_path = "sample/japan_tokyo.mbtiles"
handler = MBTilesHandler(mbtile_path, drop_lines=False, drop_points=True, drop_polygons=True, min_num_objs=5)
```

- `drop_lines`: Set to `True` to exclude LineString and MultiLineString features (default: `False`).
- `drop_points`: Set to `True` to exclude Point and MultiPoint features (default: `True`).
- `drop_polygons`: Set to `True` to exclude Polygon and MultiPolygon features (default: `True`).
- `min_num_objs`: Minimum number of objects required for a valid tile (default: `5`).

#### Fetch Zoom Level Range
To get the range of available zoom levels in the MBTiles file, use the `get_zoom_minmax` function:

```python
zoom_min, zoom_max = handler.get_zoom_minmax()
print(f"Available zoom levels: {zoom_min} to {zoom_max}")
```

#### Fetch Column Range for a Zoom Level
To get the range of tile columns for a specific zoom level, use the `get_column_minmax` function:

```python
zoom_level = 12  # Replace with your desired zoom level
col_min, col_max = handler.get_column_minmax(zoom_level)
print(f"Available columns for zoom level {zoom_level}: {col_min} to {col_max}")
```

#### Fetch Row Range for a Zoom Level
To get the range of tile rows for a specific zoom level, use the `get_row_minmax` function:

```python
zoom_level = 12  # Replace with your desired zoom level
row_min, row_max = handler.get_row_minmax(zoom_level)
print(f"Available rows for zoom level {zoom_level}: {row_min} to {row_max}")
```

#### Fetch Tile Data
To fetch and decode the data of a specific tile, use the `get_tile` function by providing the zoom level, column, and row of the tile:

```python
zoom_level = 10  # Replace with your desired zoom level
tile_col = 907   # Replace with your desired column
tile_row = 619   # Replace with your desired row

tile_data = handler.get_tile(zoom_level, tile_col, tile_row)
if tile_data is not None:
    # Process the tile data, which will be returned as a DataFrame
    print(tile_data)
else:
    print("Tile not found or does not meet the minimum object requirement.")
```

#### Fetch a Random Tile
To fetch and decode a random tile from the MBTiles file, you can use the `get_random_tile` function for a specific zoom level:

```python
zoom_level = 12  # Replace with your desired zoom level

random_tile = handler.get_random_tile(zoom_level)
if random_tile is not None:
    # Process the random tile data, which will be returned as a DataFrame
    print(random_tile)
else:
    print("No valid random tile found.")
```

#### Fetch Area Tiles
To fetch and decode multiple tiles within a specified area, use the `get_area_tiles` function. You need to provide the standard zoom level, column, and row, as well as the target zoom level:

```python
zoom_std = 10   # Replace with your standard zoom level
col_std = 907   # Replace with your standard column
row_std = 619   # Replace with your standard row
zoom_target = 11  # Replace with your desired target zoom level

area_tiles = handler.get_area_tiles(zoom_std, col_std, row_std, zoom_target)
if area_tiles is not None:
    # Process the area tiles data, which will be returned as a list of DataFrames
    for tile_data in area_tiles:
        print(tile_data)
else:
    print("No valid area tiles found.")
```

### [`SegDatasetCreator`](src/MBTiles_Segmentation/seg_dataset_creator.py)

#### Initialization
To initialize a `SegDatasetCreator` object, provide the output folder path, path to the MBTiles file, and optional configuration parameters:

```python
from MBTiles_Segmentation import  SegDatasetCreator

folder_path = "sample/japan_tokyo_dataset2"
mbtiles_path = "sample/japan_tokyo.mbtiles"

# Initialize with optional color mapping and minimum object count
creator = SegDatasetCreator(output_folder, mbtile_path, min_num_objs=50)
```

- `color_mapping`: A dictionary that maps class names to colors (default: a predefined color mapping).
- `min_num_objs`: Minimum number of objects required for a valid tile (default: `10`).


#### Create Image
To create an image for a specific tile, use the `create_img` function by providing the tile data and the output file path:

```python
df = handler.get_random_tile(12)
creator.create_img(df, "../sample/random_tile.png")
```

#### Create YOLO Dataset
To create a YOLO dataset for a specific tile, use the `create_dataset` function by providing the tile data and the output file path:

```python
creator.create_dataset(each_image_num=10)
```

## License

This project is open-source and available under the [MIT License](LICENSE).
