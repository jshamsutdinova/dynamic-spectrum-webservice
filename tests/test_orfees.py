"""DynamicSpectrum Test"""
from astropy.io import fits
from dynamicspectrum.instruments.orfees import Orfees


class TestOrfees:
    """ Test ORFEES instrument class """

    def test_should_read_file(self):
        response = Orfees().read_file('tests/dataset/int_orf20190410.fts')
        assert isinstance(response, fits.fitsrec.FITS_rec) is True

