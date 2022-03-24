#!/usr/bin/env python3
from dynamicspectrum.instruments.amateras import Amateras
from dynamicspectrum.instruments.orfees import Orfees
from dynamicspectrum.instruments.wind import Wind
from dynamicspectrum.instruments.goes import Goes
from dynamicspectrum.instruments.srh import SRH


class InstrumentFactory():
    """
    Class creates instance of instruments
    """
    @staticmethod
    def get_instrument(name, inst_download):
        if name == 'amateras':
            return Amateras(inst_download)

        elif name == 'wind1':
            return Wind('rad1', inst_download)

        elif name == 'wind2':
            return Wind('rad2', inst_download)

        elif name == 'orfees':
            return Orfees()

        elif name == 'goes':
            return Goes(inst_download)

        elif name == 'srh':
            return SRH()
