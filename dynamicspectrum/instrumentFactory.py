#!/usr/bin/env python3
from dynamicspectrum.dynamicspectrum.instruments.amateras import Amateras
from dynamicspectrum.dynamicspectrum.instruments.orfees import Orfees
from dynamicspectrum.dynamicspectrum.instruments.wind import Wind
from dynamicspectrum.dynamicspectrum.instruments.stereo import Stereo
from dynamicspectrum.dynamicspectrum.instruments.goes import Goes
from dynamicspectrum.dynamicspectrum.instruments.srh import SRH
from dynamicspectrum.dynamicspectrum.instruments.goes17 import Goes17


class InstrumentFactory:
    """
    Class creates instance of instruments
    """
    @staticmethod
    def get_instrument(name, stokes_parameter):
        if name == 'amateras':
            return Amateras(stokes_parameter)

        elif name == 'wind1':
            return Wind('rad1')

        elif name == 'wind2':
            return Wind('rad2')

        elif name == 'stereo':
            return Stereo()

        elif name == 'orfees':
            return Orfees(stokes_parameter)

        elif name == 'goes':
            return Goes()

        elif name == 'srh':
            return SRH()

        elif name == 'goes17':
            return Goes17()
