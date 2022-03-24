"""DynamicSpectrum Test"""
from datetime import time
from dynamicspectrum.instruments.instrument import Instrument


class TestInstrument:
    """ Test Instrument class """

    def test_should_convert_time_to_seconds(self):
        response = Instrument().time_to_seconds(time(4, 46, 30))
        expected_time_sec = 17190
        assert response == expected_time_sec

    def test_should_define_grid_range(self):
        response = Instrument().define_grid_range(25400.0, 15000)
        expected_grid_point = 10400
        assert response == expected_grid_point
