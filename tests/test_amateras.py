"""DynamicSpectrum Test"""
import numpy as np
from datetime import datetime, time
from dynamicspectrum.instruments.amateras import Amateras, is_obs_time_within_interval


class TestAmateras:
    """ Test AMATERAS instrument class """

    def test_should_get_file_path(self):
        date = datetime(2019, 4, 10)
        response = Amateras().get_file_path(date)
        assert response == 'data/AmaterasFile/20190410_IPRT.fits'

    def test_should_read_header(self):
        response = Amateras().read_header('tests/dataset/20190410_IPRT.fits')
        assert len(response) == 1

    def test_should_read_file(self):
        response = Amateras().read_file('tests/dataset/20190410_IPRT.fits')
        assert type(response[0]) is np.ndarray
        assert type(response[1]) is np.ndarray

    def test_should_get_quiet_sun_values(self):
        date = datetime(2019, 4, 10)
        response = Amateras().get_quiet_sun(date)
        assert type(response[0]) is np.ndarray
        assert type(response[1]) is np.ndarray

    def test_should_calibrate_data(self):
        date = datetime(2019, 4, 10)
        side = Amateras().read_file('tests/dataset/20190410_IPRT.fits')
        qs_value = Amateras().get_quiet_sun(date)
        response = Amateras().calibrate_data(side[0], qs_value[0])
        assert response.shape == side[0].shape

    def test_should_convert_instrument_time(self):
        response = Amateras().convert_instrument_time('21:31:44.000')
        assert response == 77504

    def test_should_get_observation_time(self):
        header = Amateras().read_header('tests/dataset/20190410_IPRT.fits')
        response = Amateras().get_observation_time(header)
        expected_time_from = 77828
        expected_time_to = 28173
        expected_time_step = 1.17321
        assert response[0] == expected_time_from
        assert response[1] == expected_time_to
        assert response[2] == expected_time_step

    def test_should_check_is_obs_time_within_interval(self):
        response = is_obs_time_within_interval(18000, 28800, 77828, 28173)
        assert response is True

        response = is_obs_time_within_interval(0, 35000,  77828, 28173)
        assert response is True

        response = is_obs_time_within_interval(60000, 80000, 77828, 28173)
        assert response is None

        response = is_obs_time_within_interval(35000, 55000, 77828, 28173)
        assert response is None

    def test_should_ovveride_time_interval(self):
        response = Amateras().override_time_interval(30000, 25000)
        assert response == 25000

        response = Amateras().override_time_interval(15000, 25000)
        assert response == 15000

    def test_should_get_array_shape(self):
        response = Amateras().get_array_shape(77000, 0, 20000, 1.05)
        assert response == (8952, 28000)

    def test_should_slice_array(self):
        array = np.array([[1, 2, 3, 4], [5, 6, 7, 8]])
        response = Amateras().slice_array(array, 1, 3)
        assert (response == np.array([[2, 3], [6, 7]])).all()

    def test_should_change_image_contrast(self):
        pass

    def test_should_create_dictionary(self):
        array = np.array([[1, 2, 3, 4], [5, 6, 7, 8]])
        response = Amateras().create_data_dict(array, 0, 5)
        assert type(response) == dict
        assert len(response) == 3

    def test_should_get_data(self):
        response = Amateras().get_data(datetime(2019, 4, 10), time(5, 00, 0),
                                       time(8, 00, 0))
        assert type(response) == dict
        assert response['array'].shape == (410, 8671)

        response = Amateras().get_data(datetime(2019, 4, 10), time(20, 00, 0),
                                       time(22, 00, 0))
        assert type(response) == dict
        assert response['array'].shape == (1, 0)

        # with pytest.raises(FileNotFoundError):
            # Amateras().get_data(datetime(2019, 5, 10), time(20, 00, 0), time(22, 00, 0))
