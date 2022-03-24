import numpy as np

class Polar:
    """
        This class tests polarization for AMATERAS (TEST!!!)
    """
    def standard_deviation (side):
        avg = np.mean(side)

        arr = []
        j = 0
        for string in range(1452): #count of string
            arr.append([])
            array = (side[:, string]) # array of value for each period of time

            for element in range(410): #count of elements in the array
                mean_array = array[element] - avg
                mean_array = np.power(mean_array, 2)
                arr[j].append(mean_array) #add values in list
            j += 1

        arr = np.array([np.array(xi) for xi in arr]) #convert list to array
        arr= arr.transpose() #transpose matrix. So we get array (410, )
        sum_arr = np.sum(arr)
        n, m = arr.shape
        sd = sum_arr/((n * m) - 1)
        sd = np.sqrt(sd)

        return sd


    def get_trend(side, sd):
        for i in range(1452):
            string = side[:, i]
            avg = np.mean(string)
            for elem in range(410):
                diff = abs(string[elem] - avg)
                if diff < sd:
                    string[elem] = 0
        return side
