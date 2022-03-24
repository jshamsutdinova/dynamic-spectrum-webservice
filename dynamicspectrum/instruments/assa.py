#!/usr/bin/env python3
""" The class for building dynamic radio spectrums """
import os
import numpy as np
from urllib.parse import urljoin
from astropy.io import fits
from datetime import datetime, date


def time_to_seconds(time):
    """ Convert time to seconds """
    timedelta = datetime.combine(date.min, time) - datetime.min
    seconds = timedelta.total_seconds()
    return seconds


class ASSA:
    """
    This class operates ASSA instrument data
    """
    def read_header(self, file_path):
        """ Read header of FITS file """
        header = fits.open(file_path)
        return header

    def read_file(self, file_path):
        """ Read file. Return array of data """
        file_data = fits.getdata(file_path, dtype=float)
        return file_data

    def convert_instrument_time(self, time, time_format):
        """ Convert time to seconds """
        date_time = datetime.strptime(time, time_format)
        timedelta = date_time - datetime(1900, 1, 1)
        seconds = timedelta.total_seconds()

        return seconds

    def get_observation_time(self, file_header):
        """ Get observation time of instrument """
        start_obs = file_header[0].header['TIME-OBS']
        end_obs = file_header[0].header['TIME-END']
        time_step = file_header[0].header['CDELT1']

        start_obs_sec = self.convert_instrument_time(start_obs, '%H:%M:%S.%f')
        end_obs_sec = self.convert_instrument_time(end_obs, '%H:%M:%S')

        return start_obs_sec, end_obs_sec, time_step

    @staticmethod
    def is_observation_time_within_interval(time_from, time_to, start_obs, end_obs):
        """ Determine instrument observation time is within a specified range """
        if time_from >= start_obs or time_to <= end_obs:
            return True
        elif time_from <= start_obs and time_to >= end_obs:
            return True

    @staticmethod
    def override_time_interval(time_from, time_to, start_obs, end_obs):
        """ Compare the range of user-selected time interval with observation time interval """
        if time_from < start_obs:
            time_from = start_obs
        if time_to > end_obs:
            time_to = end_obs
        return time_from, time_to

    def get_array_shape(self, start_obs, time_from, time_to, step):
        """ Get shape of AMATERAS array considering the midnight """
        until_mn = 86400 - start_obs
        start = round((time_from + until_mn) / step)
        end = round((time_to + until_mn) / step)

        return start, end

    def slice_array(self, array, start, end):
        """ Slice array for period of observation time """
        s = slice(start, end, 1)
        sliced_array = array[:, s]

        return sliced_array

    def change_image_contrast(self, array):
        """ Improve image visibility """
        array[385:402] = array[367:384]
        array[(array > 45)] = 45
        return array

    def create_data_dict(self, array, start_point, end_point):
        """ Create dictionary with parameters to build spectrum """
        data = {'array': array, 'ncols': [start_point, end_point]}
        return data

    def get_data(self, file_path, time_from, time_to):
        """ Performs actions to process data """
        header = self.read_header(file_path)

        start_obs, end_obs, step = self.get_observation_time(header)
        user_time_from = time_to_seconds(time_from)
        user_time_to = time_to_seconds(time_to)

        interval_is_within = self.is_observation_time_within_interval(user_time_from, user_time_to, start_obs, end_obs)
        if interval_is_within:
            time_from, time_to = self.override_time_interval(user_time_from, user_time_to, start_obs, end_obs)
