import numpy as np
import time
from skimage.transform import resize

class Spectrum:

    def get_calibration_value(array, QS):
        """
             Calibrate array with Quiet Sun values for AMATERAS
        """
        array = array.astype(float)
        i = 0
        for row in array:
            calibration = (row - QS[i + 100] + 3) / 10
            array[i] = calibration
            i += 1

        return array


    def extra_space(array, color, size, side='buttom'):
        """
            Add empty area to array
        """
        #array = array.transpose()
        row, column = array.shape
        empty_area = [[color for x in range(size)] for y in range(column)] # Create array with the same values
        empty_area = np.asarray(empty_area)

        if (side == 'buttom'):
            new_array = np.concatenate((array, empty_area.T), axis=0)
        if (side == 'top'):
            new_array = np.concatenate((empty_area.T, array), axis=0)

        return new_array

    def increment_array(array, color, size):
        """
            Add empty area to array
        """
        #array = array.transpose()
        row, column = array.shape
        empty_area = [[color for x in range(size)] for y in range(column)] # Create array with the same values
        empty_area = np.asarray(empty_area)

        return empty_area


    def slice_array(start, stop, array):
        """
            Slice array for period of observation time
        """
        s = slice(start, stop, 1)
        cut_array = array[:,s]

        return cut_array


    def get_observation_period():
        """
            Input observation period of time
        """
        time_from = input('Enter start time in HH:MM:SS format: ')
        time_to = input('Enter end time in HH:MM:SS format: ')


    def label_time(time_from, time_to):
        """
            Create array with time for label axis
        """
        step = (time_to - time_from) / 3
        seconds = np.arange(time_from, time_to + 1, step) # Array with time in seconds 
        array = np.array([])
        for sec in seconds:
            t = time.strftime('%H:%M:%S', time.gmtime(sec))
            array = np.append(array, t)

        return array

    def time_tickets(time_from, time_to):
        """
            Determine tickets for plot
        """
        time_diff = index_to - index_from
        if time_diff > 4000:
            tickets = round((index_to - index_from)/1200) #сделать условие, если sec больше какого-то числа, то делим, например, на 1200
        else:
            tickets = round((index_to - index_from)/300)

        return tickets

    def build_amateras_array(array, time):
        """
            Add data for AMATERAS array for period of time
        """
        row, column = array.shape
        value = time - column
        extra_area = [[0 for x in range(value)] for y in range(row)] # Create array with the same values
        extra_area = np.asarray(extra_area)
        full_array = np.append(array, extra_area, axis=1)

        return full_array

    def rebin(a, new_shape):
        """
            Expend an array
        """
        M, N = a.shape
        m, n = new_shape
        if m<M:
            return a.reshape((m,M//m,n,N//n)).mean(3).mean(1)
        else:
            return np.repeat(np.repeat(a, m//M, axis=0), n//N, axis=1)
