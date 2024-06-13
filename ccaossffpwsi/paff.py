#!/usr/bin/env python
"""
Created on 2024-06-13 10:50:22
Module desc: Reader module for read multiple data sources
@author: m.sikarwar
"""
from pathlib import Path
from numpy import ndarray
import tifffile
import openslide
from typing import Callable

def read_by_ops():
    pass


class PAFF():

    def __init__(
            self, file_path: str | Path,
            tile_size: int = 224,
            reading_func: Callable = read_by_ops
    ) -> ndarray:
        self.file_path = file_path
        self.tile_size = tile_size
        self.reading_func = reading_func # a tiff or openslide object


    # @property
    # def imread(self) -> :
    #     self._imread =

    # @imread.setter
    # def imread(self, imread) -> None:
    #     self._imread = imread

    def convert():
        pass
