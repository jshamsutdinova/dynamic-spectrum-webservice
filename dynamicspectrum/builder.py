#!/usr/bin/env python3
import os
import errno
import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.colors
from datetime import datetime, date
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import FixedLocator, FixedFormatter
from dynamicspectrum.dynamicspectrum.instrumentFactory import InstrumentFactory
from dynamicspectrum.dynamicspectrum import exceptions


class Builder:
    """
    Class builds dynamic spectrum
    """
    def __init__(self):
        self.factory = InstrumentFactory()
        self.fig = plt.figure(num=1, figsize=(8, 6))

    def get_instrument_data(self, date_event, time_from, time_to, instruments, stokes):
        """
        Create instance of instrument, get data and add to the array
        """
        calculated_data = {}
        for instrument in instruments:
            instr_instance = self.factory.get_instrument(instrument, stokes)
            instr_data = instr_instance.get_data(date_event, time_from, time_to)
            calculated_data[instrument] = instr_data

        return calculated_data

    def time_to_seconds(self, time_value):
        """ Convert time to seconds """
        timedelta = datetime.combine(date.min, time_value) - datetime.min
        seconds = timedelta.total_seconds()

        return seconds

    def create_time_axis_label(self, time_from, time_to):
        """ Create array to label time for X axis """
        time_diff = (time_to - time_from)
        if time_diff < 1800:
            seconds_label = np.arange(time_from, time_to+1, 300)
        elif 1800 <= time_diff <= 3600:
            seconds_label = np.arange(time_from, time_to+1, 600)
        elif 3600 < time_diff < 18000:
            seconds_label = np.arange(time_from, time_to+1, 1800)
        elif 18000 <= time_diff < 43200:
            seconds_label = np.arange(time_from, time_to+1, 3600)
        elif time_diff >= 43200:
            seconds_label = np.arange(time_from, time_to+1, 7200)
        else:
            seconds_label = np.arange(time_from, time_to+1, time_diff)

        time_axis = np.array([])
        for seconds in seconds_label:
            time_label = time.strftime('%H:%M', time.gmtime(seconds))
            time_axis = np.append(time_axis, time_label)

        return time_axis

    def define_columns_of_grid(self, start, end):
        """ Define columns to build Grid """
        return end - start

    def create_general_plot(self, grid, date, time_axis):
        """ Create plot with subscriptions """
        axis = self.fig.add_subplot(grid[0:, 0])
        axis.patch.set_alpha(0)
        axis.set_title(date.strftime("%Y-%m-%d"), pad=20)
        axis.set_ylabel('Frequency (MHz)')
        axis.set_xlabel('Time (UT)')
        axis.set_xticklabels(time_axis)
        axis.xaxis.set_major_locator(ticker.LinearLocator(time_axis.shape[0]))
        axis.xaxis.set_minor_locator(ticker.AutoMinorLocator(5))
        axis.yaxis.set_major_formatter(FixedFormatter([1000.0, 100.0, 1.0, 0.1]))
        axis.yaxis.set_major_locator(FixedLocator([0, 0.25, 0.52, 0.75]))

        return axis

    def set_axis(self, grid, nrows, ncols):
        """
        Set axis for instruments on the same frequency
        """
        if ncols[0] > ncols[1] or ncols[0] == ncols[1]:
            axis = self.fig.add_subplot(grid[0, 0])
        else:
            axis = self.fig.add_subplot(grid[nrows[0]:nrows[1], ncols[0]:ncols[1]])
        return axis

    def display_intensity(self, axis, array):
        """ Display intensity spectrum """
        axis.imshow(array, cmap='gray_r', aspect='auto', interpolation='bilinear')
        axis.set(yticks=[])
        axis.set(xticks=[])
        axis.set_frame_on(False)

        return axis

    def display_polarization(self, axis, array, instr):
        """ Display polarization spectrum """
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ['grey', 'black'])
        if instr == 'amateras':
            norm = plt.Normalize(-1, 1)
            axis.imshow(array, cmap=cmap, norm=norm, aspect='auto',
                        interpolation='bilinear')
        elif instr == 'orfees':
            axis.imshow(array, cmap=cmap, aspect='auto', interpolation='bilinear')
        axis.set(yticks=[])
        axis.set(xticks=[])
        axis.set_frame_on(False)

        return axis

    def display_goes(self, grid, data, columns):
        """ Display correlation plot of GOES time profile """
        axis = self.fig.add_subplot(grid[500:700, :columns])
        # axis = self.fig.add_subplot(grid[1:700, :columns])
        print('here')
        goes = axis.twinx().twiny()
        goes.plot(data['time'], data['flux'], color='red')
        goes.set_yscale('log')
        goes.set_xlim(data['ncols'][0], data['ncols'][1])
        goes.set(yticks=[])
        goes.set(xticks=[])
        goes.set_yticks([], minor=True)
        goes.spines['top'].set_color('#aeabab')

        return goes

    def display_srh(self, grid, data, columns):
        """
        Display correlation plot of SRH time profile
        """
        axis = self.fig.add_subplot(grid[750:1000, :columns])
        srh = axis.twinx().twiny()
        srh.plot(data['time'], data['flux'], color='green')
        srh.set_xlim(data['ncols'][0], data['ncols'][1])
        srh.set(yticks=[])
        srh.set(xticks=[])
        srh.spines['top'].set_color('#aeabab')

        return srh

    def add_spectrometer(self, grid, instr_data):
        """ Create axis and plot of spectrometer spectrum """
        for instr in instr_data.keys():
            axis = self.set_axis(grid, instr_data[instr]['nrows'],
                                 instr_data[instr]['ncols'])
            self.display_intensity(axis, instr_data[instr]['array'])
            self.add_label(axis, instr)

    def add_spectropolarimeter(self, grid, instr_data, stokes_parameter):
        """ Build spectrum of AMATERAS and ORFEES """
        for instr in instr_data.keys():
            axis = self.set_axis(grid, instr_data[instr]['nrows'],
                                 instr_data[instr]['ncols'])
            if stokes_parameter == 'I':
                self.display_intensity(axis, instr_data[instr]['array'])
            elif stokes_parameter == 'V':
                self.display_polarization(axis, instr_data[instr]['array'], instr)

    def add_time_profile(self, grid, instr_data, columns):
        """
        Add correlation plot to spectrum
        """
        for instr in instr_data.keys():
            if instr == 'goes':
                self.display_goes(grid, instr_data['goes'], columns)
            elif instr == 'srh':
                self.display_srh(grid, instr_data['srh'], columns)
            elif instr == 'goes17':
                self.display_goes(grid, instr_data['goes17'], columns)

    def add_label(self, axis, name):
        """ Add instrument name to plot """
        axis.set_ylabel(name.upper(), rotation=270, labelpad=30, size=9)
        axis.yaxis.set_label_position('right')
        return axis

    def add_spectropolarimeter_label(self, grid, columns):
        """ Added background and label to 100-500 MHz diapazon"""
        axis = self.fig.add_subplot(grid[750:1000, :columns])
        axis.set_ylabel('AMATERAS/ORFEES', rotation=270, labelpad=30, size=9)
        axis.yaxis.set_label_position('right')
        axis.spines['top'].set_visible(False)
        axis.set_facecolor('#aeabab')
        axis.set(yticks=([]))
        axis.set(xticks=([]))

        return axis

    def add_empty_background(self, grid, nrows, ncols, color):
        """
        Create empty background
        """
        axis = self.fig.add_subplot(grid[nrows[0]:nrows[1], :ncols])
        axis.set_facecolor(color)
        axis.set(yticks=[])
        axis.set(xticks=[])
        axis.spines['top'].set_visible(False)
        axis.spines['bottom'].set_visible(False)

        return axis

    def combine_spectrum(self, date_event, time_from, time_to, spectrometer,
                         spectropolarimeter, time_profile, stokes):
        """
        Create dynamic spectrum for certain period of time
        """
        spectrometer_data = self.get_instrument_data(
            date_event, time_from, time_to, spectrometer, stokes)
        spectropolarimeter_data = self.get_instrument_data(
            date_event, time_from, time_to, spectropolarimeter, stokes)
        time_profile_data = self.get_instrument_data(
            date_event, time_from, time_to, time_profile, stokes)
        start_axis = round(self.time_to_seconds(time_from))
        end_axis = round(self.time_to_seconds(time_to))
        all_columns = self.define_columns_of_grid(start_axis, end_axis)
        time_axis = self.create_time_axis_label(start_axis, end_axis)

        plt.subplots_adjust(hspace=0, wspace=0)
        grid_general = GridSpec(1000, 1, figure=self.fig)
        grid = GridSpec(1000, all_columns, figure=self.fig)

        self.add_spectrometer(grid, spectrometer_data)
        self.add_spectropolarimeter_label(grid, all_columns)
        self.add_spectropolarimeter(grid, spectropolarimeter_data, stokes)
        self.add_time_profile(grid, time_profile_data, all_columns)

        self.add_empty_background(grid, [480, 500], all_columns, '#e5e0e0')
        self.add_empty_background(grid, [700, 750], all_columns, '#aeabab')

        self.create_general_plot(grid_general, date_event, time_axis)

        figure = self.save_figure(date_event, time_from, time_to, stokes)

        plt.show()

        return figure

    def save_figure(self, date, time_from, time_to, stokes_parameter):
        """ Save figure in the folder """
        date_part = date.strftime('%Y%m%d')
        time_from_part = time_from.strftime('%H%M')
        time_to_part = time_to.strftime('%H%M')
        fig_name = date_part + '_' + time_from_part + '_' + time_to_part +\
            '_' + stokes_parameter + '.jpg'
        folder = 'plots/'

        if not os.path.exists(folder):
            try:
                os.mkdir(folder)
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise exceptions.CannotCreateDirectory("Can not create Plots folder")
        file_path = os.path.join(folder, fig_name)

        return self.fig.savefig(file_path, dpi=self.fig.dpi)
