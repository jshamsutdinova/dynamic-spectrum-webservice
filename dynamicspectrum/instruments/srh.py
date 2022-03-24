#!/usr/bin/env python3
""" The class for building dynamic radio spectrums """
import os
import numpy as np
from astropy.io import fits
from raodata.Data import Data
from dynamicspectrum.dynamicspectrum.instruments.time_profile import TimeProfile


class SRH(TimeProfile):
    """
    This class operates SRH data
    """
    def get_file(self, date):
        """
        Return file path of instrument in directory
        """
        # file_path = 'data/SRH/srh_cp_' + date.strftime('%Y%m%d') + '.fits'
        # print(file_path)
        files = Data().get_files('SRH', 'cp', date, date)
        for f in files:
            if not os.path.exists('data/SRH/'+f.name):
                f.save_to('data/SRH/'+f.name)
        file_path = os.path.join('data', 'SRH', f.name)
        return file_path

    def read_file(self, file_path):
        """
        Read file. Return array of data
        """
        file_data = fits.getdata(file_path, ext=2, dtype=np.float)
        return file_data

    def define_frequency_index(self, file_path):
        """
        Define index of frequency in array
        """
        file_data = fits.getdata(file_path, ext=1, dtype=np.float)
        freq_array = file_data['frequencies']
        freq_index = super().find_index(freq_array, 5700)

        return freq_index

    def get_time_data(self, file_data, index):
        """
        Return array of SRH time data for 5.7 GHz
        """
        return file_data['time'][index]

    def get_flux_data(self, file_data, index):
        """
        Return array of SRH flux data for 5.7 GHz
        """
        return file_data['I'][index]

    def is_observation_time_within_interval(self, time_from, time_to, start_obs, end_obs):
        """
        Determine instrument observation time is within a specified range
        """
        if time_from >= start_obs and time_to <= end_obs:
            return True
        elif start_obs <= time_from <= end_obs:
            return True
        elif start_obs <= time_to <= end_obs:
            return True
        elif time_from <= start_obs and time_to >= end_obs:
            return True

    def align_profile(self, flux, time):
        """
        Delete points close to zero
        """
        index = (np.where(flux <= 0.003))
        time = np.delete(time, index)
        flux = np.delete(flux, index)

        return flux, time

    def get_data(self, date, time_from, time_to):
        file_path = self.get_file(date)
        try:
            file_data = self.read_file(file_path)
            freq_index = self.define_frequency_index(file_path)
            time = self.get_time_data(file_data, freq_index)
            flux = self.get_flux_data(file_data, freq_index)

            time_from_sec = super().time_to_seconds(time_from)
            time_to_sec = super().time_to_seconds(time_to)

            is_within = self.is_observation_time_within_interval(
                time_from_sec, time_to_sec, time[0], time[-1])
            if is_within:
                start_index = super().find_index(time, time_from_sec)
                end_index = super().find_index(time, time_to_sec)

                time = time[start_index:end_index]
                flux = flux[start_index:end_index]

                flux, time = self.align_profile(flux, time)
            else:
                time = 0
                flux = 0

            data = super().create_data_dict(time, flux, time_from_sec, time_to_sec)

        except FileNotFoundError:
            data = self.create_data_dict(0, 0, 0, 0)
        return data
