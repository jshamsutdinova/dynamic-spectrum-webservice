#!/usr/bin/env python3
""" The class for building dynamic radio spectrums """
import os
import fnmatch
import numpy as np
from astropy.io import fits
from skimage.transform import resize
from datetime import datetime
from dynamicspectrum.dynamicspectrum.instruments.spectrum import Spectrum


class Orfees(Spectrum):
    """
    This class operates ORFEES instrument
    """
    def __init__(self, stokes):
        self.stokes = stokes

    def get_file(self, date):
        """
        Return file path of instrument
        """
        date_str = date.strftime("%Y-%m-%d")
        date_part = "".join(date_str.split('-'))
        for root, dirs, files in os.walk('data/'):
            for name in files:
                if fnmatch.fnmatch(name, 'int_orf' + date_part + '*.fts'):
                    path = os.path.join(root, name)
                    return path

    def read_file(self, file_path):
        """
        Read file. Return array of data
        """
        file_data = fits.getdata(file_path, ext=2)

        return file_data

    def combine_bands(self, file_data, bands):
        """
        Combime bands. Return array of data
        """
        size_time, = file_data.shape
        instr_data = np.array([])
        first_iteration = True

        for b in bands:
            band = resize(file_data[b], (size_time, 200), anti_aliasing=True)
            if first_iteration:
                instr_data = band
                first_iteration = False
            else:
                instr_data = np.concatenate(([instr_data, band]), axis=1)

        return instr_data[:, :].T

    def get_stokes_parameter(self, file_data):
        """ Define Stokes Parameter """
        if self.stokes == "I":
            bands = ['STOKESI_B1', 'STOKESI_B2', 'STOKESI_B3', 'STOKESI_B4', 'STOKESI_B5']
            data = self.combine_bands(file_data, bands)
        elif self.stokes == "V":
            bands = ['STOKESV_B1', 'STOKESV_B2', 'STOKESV_B3', 'STOKESV_B4', 'STOKESV_B5']
            data = self.combine_bands(file_data, bands)
            # data = self.get_polarization(array)

        return data

    def get_polarization(self, array):
        """ Return polarized component"""
        sd = np.std(array)
        elem_in_row = array.shape[1]
        for row in array:
            avg = np.mean(row)
            for i in range(elem_in_row):
                diff = abs(row[i] - avg)
                if diff < sd:
                    row[i] = 0

        return array

    def get_observation_time(self, file_path):
        """
        Get observation time of instrument
        """
        file_header = fits.getheader(file_path, ext=0)

        start_obs = file_header['TIME-OBS']
        end_obs = file_header['TIME-END']
        step = fits.getheader(file_path, ext=2)['EXPTIME']

        start_obs_sec = self.convert_instrument_time(start_obs)
        end_obs_sec = self.convert_instrument_time(end_obs)

        return start_obs_sec, end_obs_sec, step

    @staticmethod
    def convert_instrument_time(time):
        """
        Convert time to seconds
        """
        date_time = datetime.strptime(time, '%H:%M:%S:%f')
        timedelta = date_time - datetime(1900, 1, 1)
        seconds = timedelta.total_seconds()

        return seconds

    def is_observation_time_within_interval(self, time_from, time_to, start_obs, end_obs):
        """
        Determine instrument observation time is within a specified range
        """
        if time_from >= start_obs or time_to <= end_obs:
            return True
        elif time_from <= start_obs and time_to >= end_obs:
            return True

    def override_time_interval(self, time_from, time_to, start_obs, end_obs):
        """
        Check the user-selected time interval for data availability
        """
        if time_from < start_obs:
            time_from = start_obs
        if time_to > end_obs:
            time_to = end_obs

        return time_from, time_to

    def get_array_shape(self, start_obs, time_from, time_to):
        """
        Get shape of ORFEES array considering the time observation
        """
        start_array = round((time_from - start_obs))
        end_array = round((time_to - start_obs))

        return start_array, end_array

    def slice_array(self, array, start, end, step):
        """
        Slice array for period of observation time
        """
        start = round(start / step)
        end = round(end / step)

        s = slice(start, end, 1)
        sliced_array = array[:, s]

        return sliced_array

    def change_image_contrast(self, array):
        """
        Improve image visibility
        """
        array = np.power(array, 0.5)
        array[(array > 10)] = 10
        array[(array < 4)] = 4
        array[(array > 950)] = 10
        array[(array == 1000)] = 0.1
        array[(array > 10.65)] = 10.65
        array = np.power(array, 3)

        array[920:943] = array[897:920]
        array[720:800] = array[800:880]
        array[600:720] = array[800:920]
        array[438:452] = array[424:438]
        array[437] = array[436]
        array[451] = array[453]
        array[380:392] = array[368:380]
        array[596:599] = array[593:596]
        array[950:998] = array[902:950]
        array[297:307] = array[287:297]
        array[299:302] = array[296:299]
        array[289:292] = array[286:289]
        array[176:184] = array[168:176]
        array[144:147] = array[141:144]
        array[130:133] = array[127:130]
        array[134:137] = array[131:134]
        array[120:123] = array[117:120]
        array[140] = array[139]
        array[138] = array[139]
        array[137] = array[136]
        array[183] = array[182]
        array[175] = array[174]
        array[124] = array[122]
        array[991] = array[990]
        array[126] = array[125]
        array[115] = array[114]
        array[157] = array[156]
        array[134] = array[133]
        array[131] = array[130]
        array[128] = array[129]
        array[123] = array[122]
        array[19] = array[18]
        array[127] = array[126]
        array[145] = array[144]
        array[18:19] = array[17:18]
        array[126:128] = array[124:126]
        array[129:132] = array[126:129]

        return array

    def create_data_dict(self, array, start_point, end_point):
        """ Create dictionary with parameters to build spectrum """
        data = {'array': array, 'nrows': [750, 1000], 'ncols': [start_point, end_point]}
        print('orfees', start_point, end_point)
        return data

    def get_data(self, date, time_from, time_to):
        """
        Performs actions to process data
        """
        file_path = self.get_file(date)
        try:
            file_data = self.read_file(file_path)
            instr_data = self.get_stokes_parameter(file_data)

            start_obs, end_obs, step = self.get_observation_time(file_path)
            user_time_from = self.time_to_seconds(time_from)
            user_time_to = self.time_to_seconds(time_to)

            interval_is_within = self.is_observation_time_within_interval(
                            user_time_from, user_time_to, start_obs, end_obs)

            if interval_is_within and abs(end_obs - user_time_from) >= 900:
                refined_time_from, refined_time_to = self.override_time_interval(
                                        user_time_from, user_time_to, start_obs, end_obs)
                start, end = self.get_array_shape(start_obs, refined_time_from,
                                                  refined_time_to)
                final_array = self.slice_array(instr_data, start, end, step)

                final_array = self.change_image_contrast(final_array)

                grid_range_from = self.define_grid_range(refined_time_from,
                                                         user_time_from)
                grid_range_to = self.define_grid_range(refined_time_to, user_time_from)
                final_data = self.create_data_dict(final_array, grid_range_from,
                                                   grid_range_to)

            else:
                final_array = np.array([[]])
                final_data = self.create_data_dict(final_array, 0, 0)

        except ValueError:
            print('ORFEES file is not found')
            final_array = np.array([[]])
            final_data = self.create_data_dict(final_array, 0, 0)

        return final_data
