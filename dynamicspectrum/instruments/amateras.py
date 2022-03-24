#!/usr/bin/env python3
""" The class for building dynamic radio spectrums """
import os
import numpy as np
from urllib.parse import urljoin
from astropy.io import fits
from datetime import datetime
from dynamicspectrum.dynamicspectrum.instruments.spectrum import Spectrum
from dynamicspectrum.dynamicspectrum.download import Download


def is_obs_time_within_interval(time_from, time_to, start_obs, end_obs):
    """
    Determine selected time is within a observation time interval
    """
    if time_from < start_obs and time_from < end_obs and time_to <= end_obs:
        return True
    elif time_from < start_obs and time_from < end_obs < time_to:
        return True


class Amateras(Spectrum):
    """
    This class operates AMATERAS instrument data
    """
    def __init__(self, stokes):
        self.stokes = stokes

    def get_file_name(self, date):
        """ Return file name to download from instrument server """
        date_part = super().create_date_part(date)
        file_name = date_part + '_IPRT.fits'

        return file_name

    def get_file(self, date, base_url):
        """ Return downloaded file """
        file_name = self.get_file_name(date)
        file_path = os.path.join('data', 'AMATERAS', file_name)

        href = str(date.year) + '/' + file_name
        url = urljoin(base_url, href)

        Download().download_file('AMATERAS', file_path, url)

        return file_path

    def read_header(self, file_path):
        """
        Read header of FITS file
        """
        header = fits.open(file_path)   
        return header

    def read_file(self, file_path):
        """
        Read file. Return array of data
        """
        file_data = fits.getdata(file_path, dtype=float)
        RCP = (file_data[0, :, :])
        LCP = (file_data[1, :, :])

        return RCP, LCP

    def get_quiet_sun(self, header, base_url):
        """
        Get Quiet Sun values for two polarizations
        """
        file_name = header[0].header[35].split(" ")[-1]
        path = os.path.join('data', 'QuietSun', file_name)

        url = urljoin(base_url, file_name)
        Download().download_file('QuietSun', path, url)

        QS = np.loadtxt(path, delimiter='\t')
        qs_rcp = QS[:len(QS)//2]
        qs_lcp = QS[len(QS)//2:]

        return qs_rcp, qs_lcp

    def calibrate_data(self, side, QS):
        """
        Calibrate AMATERAS array with Quiet Sun values.
        Convert data from dB to normal format
        """
        i = 0
        for row in side:
            calibration = (row - QS[i + 100] + 3) / 10
            side[i] = calibration
            i += 1

        return side

    def convert_instrument_time(self, time):
        """
        Convert time to seconds
        """
        date_time = datetime.strptime(time, '%H:%M:%S.%f')
        timedelta = date_time - datetime(1900, 1, 1)
        seconds = timedelta.total_seconds()

        return seconds

    def get_observation_time(self, file_header):
        """
        Get observation time of instrument
        """
        start_obs = file_header[0].header['TIME-OBS']
        end_obs = file_header[0].header['TIME-END']
        time_step = file_header[0].header['CDELT1']

        start_obs_sec = self.convert_instrument_time(start_obs)
        end_obs_sec = self.convert_instrument_time(end_obs)

        return start_obs_sec, end_obs_sec, time_step

    def override_time_interval(self, time_to, end_obs):
        """
        Compare the range of user-selected time interval with observation time interval
        """
        if time_to > end_obs:
            time_to = end_obs
        return time_to

    def get_array_shape(self, start_obs, time_from, time_to, step):
        """
        Get shape of AMATERAS array considering the midnight
        """
        until_mn = 86400 - start_obs
        start = round((time_from + until_mn) / step)
        end = round((time_to + until_mn) / step)

        return start, end

    def slice_array(self, array, start, end):
        """
        Slice array for period of observation time
        """
        s = slice(start, end, 1)
        sliced_array = array[:, s]

        return sliced_array

    def get_polarized_component(self, component):
        """ Return polarized component"""
        sd = np.std(component)
        elem_in_row = component.shape[1]
        for row in component:
            avg = np.mean(row)
            for i in range(elem_in_row):
                diff = abs(row[i] - avg)
                if diff < 3*sd:
                    row[i] = 0

        return component

    def change_image_contrast(self, array):
        """
        Improve image visibility
        """
        array[385:402] = array[367:384]
        array[(array > 45)] = 45
        return array

    def get_polarization(self, lcp, rcp):
        """ Return polarization """
        lcp_v = self.get_polarized_component(lcp)
        rcp_v = self.get_polarized_component(rcp)

        return lcp_v - rcp_v

    def get_intensity(self, lcp, rcp):
        """ Return intensity """
        intensity = lcp + rcp
        self.change_image_contrast(intensity)

        return intensity

    def get_stokes_parameter(self, lcp, rcp):
        """ Calculate Stokes parameter """
        if self.stokes == "I":
            parameter = self.get_intensity(lcp, rcp)
        elif self.stokes == "V":
            parameter = self.get_polarization(lcp, rcp)

        return parameter

    def create_data_dict(self, array, start_point, end_point):
        """
        Create dictionary with parameters to build spectrum
        """
        data = {}
        data['array'] = array
        data['nrows'] = [750, 875]
        data['ncols'] = [start_point, end_point]

        return data

    def get_data(self, date, time_from, time_to):
        """
        Performs actions to process data
        """
        url = 'http://radio.gp.tohoku.ac.jp/db/IPRT-SUN/DATA2/'
        url_quiet_sun = 'http://radio.gp.tohoku.ac.jp/db/IPRT-SUN/CALIB/'

        try:
            file_path = self.get_file(date, url)
            header = self.read_header(file_path)

            start_obs, end_obs, step = self.get_observation_time(header)
            user_time_from = super().time_to_seconds(time_from)
            user_time_to = super().time_to_seconds(time_to)

            interval_is_within = is_obs_time_within_interval(
                            user_time_from, user_time_to, start_obs, end_obs)

            if interval_is_within and abs(end_obs - user_time_from) > 900 and\
               user_time_from < 25200:
                rcp_init, lcp_init = self.read_file(file_path)
                qs_rcp, qs_lcp = self.get_quiet_sun(header, url_quiet_sun)

                RCP = self.calibrate_data(rcp_init, qs_rcp)
                LCP = self.calibrate_data(lcp_init, qs_lcp)

                refined_time_to = self.override_time_interval(user_time_to, end_obs)
                start, end = self.get_array_shape(start_obs, user_time_from,
                                                  refined_time_to, step)
                cut_rcp = self.slice_array(RCP, start, end)
                cut_lcp = self.slice_array(LCP, start, end)

                final_array = self.get_stokes_parameter(cut_lcp, cut_rcp)

                grid_range_from = super().define_grid_range(user_time_from, user_time_from)
                grid_range_to = super().define_grid_range(refined_time_to, user_time_from)

                final_data = self.create_data_dict(final_array, grid_range_from,
                                                   grid_range_to)

            else:
                final_array = np.array([[]])
                final_data = self.create_data_dict(final_array, 0, 0)

        except FileNotFoundError:
            print('AMATERAS file is not found')
            final_array = np.array([[]])
            final_data = self.create_data_dict(final_array, 0, 0)

        return final_data
