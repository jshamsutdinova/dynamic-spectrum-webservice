import numpy as np


class Polarization:
    """
        This class processes data of AMATERAS for getting polarization
    """

    def standard_deviation(self, side):
        """Get standard deviation """
        avg = np.mean(side)
        n, m = side.shape
        array = np.array([[0 for x in range(m)] for y in range(n)])
        i = 0

        for row in side:
            mean_array = row - avg
            mean_array = np.power(mean_array, 2)
            array[i] = mean_array
            i += 1

        sum_array = np.sum(array)
        sd = sum_array/((n * m) - 1)
        sd = np.sqrt(sd)

        return sd

    def get_trend(self, side):
        """Get new array relative to standard deviation """
        row, column = side.shape
        sd = self.standard_deviation(side)
        for i in range(column):
            string = side[:, i]
            avg = np.mean(string)

            for j in range(row):
                diff = abs(string[j] - avg)
                if diff < sd:
                    string[j] = 0

        return side
