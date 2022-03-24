import numpy as np


class Polarization:
    """
        This class processes data of AMATERAS for getting polarization
    """

    def get_trend(self, side):
        """Get new array relative to standard deviation """
        row, column = side.shape
        sd = np.std(side)
        for i in range(column):
            string = side[:, i]
            avg = np.mean(string)

            for j in range(row):
                diff = abs(string[j] - avg)
                if diff < sd:
                    string[j] = 0

        return side
