#!/usr/bin/env python3
""" The class for building dynamic radio spectrums """
import os
import numpy as np
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from astropy.io import fits
from dynamicspectrum.dynamicspectrum.instruments.time_profile import TimeProfile
from dynamicspectrum.dynamicspectrum.download import Download


class Goes(TimeProfile):
    """
    This class operates GOES data
    """
    def get_file_name(self, date, url):
        """ Parse web-site to return file name """
        date_str = date.strftime("%Y-%m-%d")
        date_part = "".join(date_str.split('-'))

        url_path = url + str(date.year) + '/'
        response = requests.get(url_path)
        soap = BeautifulSoup(response.text, 'lxml')
        records = soap.find_all('a')
        for rec in records:
            if rec.text.find(date_part) > 0:
                file_name = rec.text
                return file_name

    def get_file(self, date, base_url):
        """
        Return file path of instrument in directory
        """
        file_name = self.get_file_name(date, base_url)
        file_path = os.path.join('data', 'GOES', file_name)

        href = str(date.year) + '/' + file_name
        url = urljoin(base_url, href)

        Download().download_file('GOES', file_path, url)

        return file_path

    def read_file(self, file_path):
        """
        Read file. Return array of data
        """
        file_data = fits.getdata(file_path, ext=2, dtype=float)
        return file_data

    def get_time_data(self, file_data):
        """
        Return array of GOES time data
        """
        return file_data['Time'].T

    def get_flux_data(self, file_data):
        """ Return array of GOES flux data """
        return file_data['Flux'][:, :, 0].T

    def align_profile(self, time, flux):
        """ Delete points close to zero """
        if not time.size == 0:
            null_value_index = self.find_index(flux, 0)
            index = (np.where(flux == flux[null_value_index]))
            time = np.delete(time, index)
            flux = np.delete(flux, index)

        return time, flux

    def get_data(self, date, time_from, time_to):
        try:
            file_path = self.get_file(date, 'https://hesperia.gsfc.nasa.gov/goes/')
            file_data = self.read_file(file_path)
            time = self.get_time_data(file_data)
            flux = self.get_flux_data(file_data)

            time_from_sec = super().time_to_seconds(time_from)
            time_to_sec = super().time_to_seconds(time_to)

            start_index = super().find_index(time, time_from_sec)
            end_index = super().find_index(time, time_to_sec)

            time = time[start_index:end_index]
            flux = flux[start_index:end_index]

            time, flux = self.align_profile(time, flux)

            data = super().create_data_dict(time, flux, time_from_sec, time_to_sec)

        except Exception as e:
            data = self.create_data_dict(0, 0, 0, 0)

        return data
