#!/usr/bin/env python3
""" The class for building dynamic radio spectrums """
import os
from urllib.parse import urljoin
from scipy.io import readsav
from dynamicspectrum.dynamicspectrum.instruments.spectrum import Spectrum
from dynamicspectrum.dynamicspectrum.download import Download


class Stereo(Spectrum):
    """
    This class operates Stereo instrument data
    """

    START_OBS = 0
    END_OBS = 86400

    def get_file_name(self, date):
        """ Return file name to download from instrument server """
        date_part = super().create_date_part(date)
        file_name = 'swaves_average_' + date_part + '_a.sav'

        return file_name

    def get_file(self, date, base_url):
        """ Return downloaded file """
        file_name = self.get_file_name(date)
        root_path = os.path.abspath((os.path.join(os.path.dirname(__file__), '..', '..', '..')))
        file_path = os.path.join(root_path, 'data', 'STEREO', file_name)

        href = str(date.year) + '/' + file_name
        url = urljoin(base_url, href)

        Download().download_file('STEREO', file_path, url)

        return file_path

    def read_file(self, file_path):
        """ Read file. Return array of data """
        file_data = readsav(file_path)
        spectrum = file_data["spectrum"].T

        return spectrum

    def override_time_interval(self, time_from, time_to):
        """ Check the user-selected time interval for data availability """
        if time_from < self.START_OBS:
            time_from = self.START_OBS
        elif time_to > self.END_OBS:
            time_to = self.END_OBS

        return time_from, time_to

    def slice_array(self, array, start, end):
        """ Slice array for period of observation time """
        start = round(start / 60)
        end = round(end / 60)
        s = slice(start, end, 1)
        sliced_array = array[:, s]

        return sliced_array

    def change_image_contrast(self, spectrum):
        """ Improve image visibility """
        array = spectrum.copy()
        array[(array > 5)] = 5
        array[(array < 0.9)] = 0.9

        return array

    def create_data_dict(self, array, start_point, end_point):
        """ Create dictionary with parameters to build spectrum """
        data = {}
        data['array'] = array
        data['ncols'] = [start_point, end_point]
        data['nrows'] = [1, 700]

        return data

    def get_data(self, date, time_from, time_to):
        """ Performs actions to process data """
        url = "https://solar-radio.gsfc.nasa.gov/data/stereo/new_summary/"
        try:
            file_path = self.get_file(date, url)
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
            print('STEREO file is not found')

        return final_data
