#!/usr/bin/env python3
""" The class for building dynamic radio spectrums """
import os
import numpy as np
import scipy.io as sp
from urllib.parse import urljoin
from dynamicspectrum.dynamicspectrum.instruments.spectrum import Spectrum
from dynamicspectrum.dynamicspectrum.download import Download


class Wind(Spectrum):
    """
    This class operates WIND instrument
    """

    START_OBS = 0
    END_OBS = 86460

    def __init__(self, receiver):
        self.receiver = receiver

    def get_file_name(self, date):
        """ Return file name to download from instrument server """
        date_part = super().create_date_part(date)

        if self.receiver == 'rad1':
            file_name = date_part + '.R1'
        elif self.receiver == 'rad2':
            file_name = date_part + '.R2'

        return file_name

    def get_file(self, date, base_url):
        """ Return file path of instrument """
        file_name = self.get_file_name(date)
        # root_path = os.path.abspath((os.path.join(os.path.dirname(__file__), '..', '..', '..')))
        if self.receiver == 'rad1':
            path = os.path.join('data', 'WIND1', file_name)
            href = 'rad1/' + str(date.year) + '/rad1/' + file_name
        elif self.receiver == 'rad2':
            path = os.path.join('data', 'WIND2', file_name)
            href = 'rad2/' + str(date.year) + '/rad2/' + file_name

        url = urljoin(base_url, href)
        Download().download_file('WIND', path, url)

        return path

    def read_file(self, file_path):
        """
        Read file. Return array of data
        """
        file_data = sp.readsav(file_path)
        instr_data = file_data["arrayb"]

        return instr_data

    def override_time_interval(self, time_from, time_to):
        """
        Check the user-selected time interval for data availability
        """
        if time_from < self.START_OBS:
            time_from = self.START_OBS
        elif time_to > self.END_OBS:
            time_to = self.END_OBS

        return time_from, time_to

    def slice_array(self, array, start, end):
        """
        Slice array for period of observation time
        """
        step = 1440 / array.shape[1] * 60
        start = round(start / step)
        end = round(end / step)
        s = slice(start, end, 1)
        sliced_array = array[:, s]

        return sliced_array

    def change_image_contrast(self, spectrum):
        """
        Improve image visibility
        """
        array = spectrum.copy()
        if self.receiver == 'rad1':
            array[(array > 5)] = 5
            array[(array < 0.9)] = 0.9
        elif self.receiver == 'rad2':
            array[(array > 1.2)] = 1.2
            array[(array < 1)] = 1
            array = np.power(array, 2)

        return array

    def create_data_dict(self, array, start_point, end_point):
        """
        Create dictionary with parameters to build spectrum
        """
        data = {'array': array, 'ncols': [start_point, end_point]}
        print('wind', start_point, end_point)
        if self.receiver == 'rad1':
            data['nrows'] = [1, 480]
        elif self.receiver == 'rad2':
            data['nrows'] = [500, 700]

        return data

    def get_data(self, date, time_from, time_to):
        """
        Performs actions to process data
        """
        file_path = self.get_file(date, 'https://solar-radio.gsfc.nasa.gov/data/wind/')
        try:
            instr_data = self.read_file(file_path)

            user_time_from = super().time_to_seconds(time_from)
            user_time_to = super().time_to_seconds(time_to)

            refined_time_from, refined_time_to = self.override_time_interval(
                user_time_from, user_time_to)

            final_array = self.slice_array(instr_data, refined_time_from, refined_time_to)
            final_array = self.change_image_contrast(final_array)

            grid_range_from = super().define_grid_range(refined_time_from, user_time_from)
            grid_range_to = super().define_grid_range(refined_time_to, user_time_from)

            final_data = self.create_data_dict(final_array, grid_range_from,
                                               grid_range_to)

        except FileNotFoundError:
            final_array = np.array([[]])
            final_data = self.create_data_dict(final_array, 0, 0)

        return final_data
