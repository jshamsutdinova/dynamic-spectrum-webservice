"""DynamicSpectrum Test"""
import numpy as np
from astropy.io import fits
from datetime import time
from dynamicspectrum.instruments.goes import Goes


class TestGoes:
    """ Test GOES instrument class """

    def test_should_read_file(self):
        response = Goes().read_file('tests/dataset/go1420190410.fits')
        assert isinstance(response, fits.fitsrec.FITS_rec) is True

    def test_should_convert_time_to_seconds(self):
        response = Goes().time_to_seconds(time(5, 5, 30))
        expected_time_sec = 18330
        assert response == expected_time_sec

    def test_should_get_time_data(self):
        file_data = Goes().read_file('tests/dataset/go1420190410.fits')
        response = Goes().get_time_data(file_data)
        assert type(response) is np.ndarray

    def test_should_get_flux_data(self):
        file_data = Goes().read_file('tests/dataset/go1420190410.fits')
        response = Goes().get_flux_data(file_data)
        assert type(response) is np.ndarray

    def test_should_find_index_to_cut_array(self):
        array = np.array([1, 2, 3, 4, 5, 6, 7, 8])
        response = Goes().find_index(array, 5)
        expected_index = 4
        assert response == expected_index

    def test_should_align_profile(self):
        time_array = np.array([1, 2, 3, 4, 5, 6, 7, 8])
        flux_array = np.array([3, 2, 4, 5, 0, 4, 0, 3])
        response = Goes().align_profile(time_array, flux_array)
        expected_time_array = np.array([1, 2, 3, 4, 6, 8])
        expected_flux_array = np.array([3, 2, 4, 5, 4, 3])
        assert (response[0] == expected_time_array).all()
        assert (response[1] == expected_flux_array).all()

        time_array = np.array([])
        flux_array = np.array([])
        response = Goes().align_profile(time_array, flux_array)
        expected_time_array = np.array([])
        expected_flux_array = np.array([])
        assert (response[0] == expected_time_array).all()
        assert (response[1] == expected_flux_array).all()

    def test_should_create_dictionary(self):
        time_array = np.array([1, 2, 3])
        flux_array = np.array([3, 2, 4])
        start_point = 0
        end_point = 10
        response = Goes().create_data_dict(time_array, flux_array, start_point, end_point)
        assert type(response['time']) is np.ndarray
        assert type(response['flux']) is np.ndarray
        assert type(response['ncols']) is list

    def test_should_get_data(self):
        pass
