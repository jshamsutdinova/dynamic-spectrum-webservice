#!/usr/bin/env python3
""" The class for building dynamic radio spectrums """
from astropy.io import fits
from datetime import datetime, date
import matplotlib.pyplot as plt


class Goes17:

    @staticmethod
    def time_to_seconds(time):
        """ Convert time to seconds """
        timedelta = datetime.combine(date.min, time) - datetime.min
        seconds = round(timedelta.total_seconds())
        return seconds

    def get_data(self, date, time_from, time_to):
        time_from_sec = self.time_to_seconds(time_from)
        time_to_sec = self.time_to_seconds(time_to)
        date_part = date.strftime('%Y%m%d')
        file_path = 'data/GOES/goes17_' + date_part + '.fits'
        print(file_path)
        file_data = fits.getdata(file_path, dtype=float)

        xrs_a = file_data[0]
        xrs_b = file_data[1]
        time_value = file_data[2]

        data = {'time': time_value, 'flux': xrs_b, 'ncols': [time_from_sec, time_to_sec]}

        # plt.figure(num=2)
        # plt.plot(data['time'], data['flux'], color='red')

        return data
