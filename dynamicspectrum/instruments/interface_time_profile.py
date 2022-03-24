#!/usr/bin/env python3
import numpy as np
from abc import ABCMeta, abstractmethod
from datetime import datetime, date


class TimeProfile(object):
    """
    Abstract class for processing data of time profile
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_file(self):
        pass

    @abstractmethod
    def read_file(self):
        pass

    @abstractmethod
    def get_time_data(self):
        pass

    @abstractmethod
    def get_flux_data(self):
        pass

    @abstractmethod
    def align_profile(self):
        pass

    @abstractmethod
    def get_data(self):
        pass

    def time_to_seconds(self, time):
        """
        Convert time to seconds
        """
        timedelta = datetime.combine(date.min, time) - datetime.min
        seconds = round(timedelta.total_seconds())
        return seconds

    def find_index(self, array, value):
        """ Find index of nearest value in array """
        index = (np.abs(array - value)).argmin()
        return index

    def create_data_dict(self, time, flux, start_point, end_point):
        """
        Create dictionary with parameters to build time profile
        """
        data = {}
        data['time'] = time
        data['flux'] = flux
        data['ncols'] = [start_point, end_point]

        return data
