#!/usr/bin/env python3
from abc import ABCMeta, abstractmethod
from datetime import datetime, date


class Instrument(object):
    """
    Abstract class for instruments
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_file(self):
        pass

    @abstractmethod
    def read_file(self):
        pass

    @abstractmethod
    def override_time_interval(self):
        pass

    @abstractmethod
    def slice_array(self):
        pass

    @abstractmethod
    def change_image_contrast(self):
        pass

    @abstractmethod
    def create_data_dict(self):
        pass

    @abstractmethod
    def get_data(self):
        pass

    def create_date_part(self, date):
        """
        Create the date part of file name
        """
        date_str = date.strftime("%Y-%m-%d")
        date_part = "".join(date_str.split('-'))

        return date_part

    def time_to_seconds(self, time):
        """
        Convert time to seconds
        """
        timedelta = datetime.combine(date.min, time) - datetime.min
        seconds = timedelta.total_seconds()

        return seconds

    def define_grid_range(self, instr_time, start_point):
        """ Define points of instrument range on the grid """
        return round(instr_time - start_point)
