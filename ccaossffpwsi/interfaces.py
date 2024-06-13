#!/usr/bin/env python
"""
Created on 2024-06-13 12:18:32
Module desc:
@author: m.sikarwar, c.walsh, j.roche, andrew, emran
"""
from abc import ABC, abstractmethod
from typing import Callable, List, Tuple
from pathlib import Path
from tqdm.contrib.concurrent import thread_map
import numpy as np
import ctypes 
import openslide as ops

class Abstract_Reader(ABC):
    """"
    Abstract class for reading data from a file.
    """
    # @abstractmethod
    # def read_image(self):
    #     pass

    # @abstractmethod
    # def validate_file(self):
    #     """"
    #     A function that will check that the file is the correct format/type for the reader.
    #     """
    #     pass

    # @abstractmethod
    # def get_metadata(self) -> dict:
    #     """
    #     A function that will return the available meta-data for the image as a dict.
    #     """
    #     pass

    @abstractmethod
    def generate_coordinates(self) -> List[Tuple[int]]:
        pass


SLIDE_ARR = None

def read_tile_multithreading(args:Tuple):
    global SLIDE_ARR
    coords, file_path, read_fn = args
    target_tile = read_fn(file_path, coords)
    SLIDE_ARR[coords[0]:coords[1], coords[2]:coords[3], :] = target_tile

def read_by_openslide(file_path, coords):
    slide = ops.Openslide(file_path)
    tile_size = abs(int(coords[3]-coords[2]))

    tile = slide.read_region((coords[1], coords[0]), 0, (tile_size, tile_size))
    return tile
    

class Reader(Abstract_Reader):

    def __init__(
            self,
            tile_size: int = 224,
            reading_method: Callable = read_by_openslide,
    ) -> None:
        self.tile_size = tile_size
        self.reading_method = reading_method
        self.max_workers = 16

    def get_metadata(self, file_path):
        slide = ops.OpenSlide(file_path)
        metadata = {
            "shape": slide.dimensions,
            "level_count": slide.level_count,
            "level_dimensions": slide.level_dimensions,
            "level_downsamples": slide.level_downsamples,
            "properties": slide.properties
        }
        return metadata

    def read_image(self, file_path: str | Path) -> np.ndarray:
        global SLIDE_ARR

        metadata = self.get_metadata(file_path) # stored as row, column, num_channels
        slide_shape = metadata["shape"]
        # generate list of arguments for reading tiles
        coordinates = self.generate_coordinates(slide_shape)

        args = [(coord, file_path, self.reading_method) for coord in coordinates]

        #execute in parallel
        SLIDE_ARR = np.full(slide_shape, 255)

        thread_map(read_tile_multithreading, args, chunksize=1, max_workers=self.max_workers)

        
        return SLIDE_ARR

        
    def generate_coordinates(self, slide_shape, bounds=None) -> List[Tuple[int]]:
        """Generate coordinates for tesselation

        Args:
            slide_shape (Tuple[int]): Shape of the slide

        Returns:
            List[Tuple[int]]: List of coordinates
        """
        y_start = 0
        x_start = 0
        y_end = slide_shape[0]
        x_end = slide_shape[1]

        if bounds is not None:
            y_start = bounds[0]
            x_start = bounds[2]
            y_end = bounds[1]
            x_end = bounds[3]

        coordinates = []
        for row in range(y_start, y_end, self.tile_size[0]):
            for col in range(x_start, x_end, self.tile_size[1]):
                if row + self.tile_size[0] > y_end:
                    row = y_end - self.tile_size[0]
                if col + self.tile_size[1] > x_end:
                    col = x_end - self.tile_size[1]

                coordinates.append((row, row+self.tile_size[0], col, col+self.tile_size[1]))

        return coordinates
