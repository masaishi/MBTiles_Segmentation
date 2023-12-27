from setuptools import setup, find_packages

install_requires = [
	'pandas',
	'mapbox_vector_tile',
	'Pillow'
]

setup(
	name='MBTiles_Segmentation',
	author='Masamune Ishihara',
	author_email='mwishiha@ucsc.edu',
	description="A package for working with MBTiles and generating image-label pairs for semantic segmentation models.",
	long_description=open('README.md').read(),
	long_description_content_type='text/markdown',
	license='MIT License',
	url='https://github.com/masaishi/MBTiles_Segmentation',
	version='0.1.1',
	python_requires='>=3.6',
	install_requires=install_requires,
	package_dir={"": "src"},
	packages=find_packages("src"),
	entry_points={
		'console_scripts': [
			'seg_mbtiles_handler = MBTiles_Segmentation.mbtiles_handler:main',
			'seg_mbtiles_creator = MBTiles_Segmentation.seg_dataset_creator:main'
		],
	},
)