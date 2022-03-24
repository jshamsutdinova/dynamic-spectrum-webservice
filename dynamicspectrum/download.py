#!/usr/bin/env python3
import os
import urllib.request
import errno
from progress.bar import ChargingBar
from dynamicspectrum.dynamicspectrum import exceptions


class SingletonMeta(type):
    """ Metaclass for Singleton """

    _instances = {}

    def __call__(cls, *args, **kwds):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwds)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Download(metaclass=SingletonMeta):
    """
    This class downloads files from data servers
    """
    def __init__(self):
        self.create_folders()

    @staticmethod
    def download_file(instrument, file_path, url):
        """
        Download file if does not exist. Saves to local folder
        """
        if not os.path.exists(file_path):
            try:
                _file = urllib.request.urlopen(url)
                record = _file.read()
                bar = ChargingBar(instrument + ' file is downloaded', max=100)
                for i in range(100):
                    with open(file_path, 'wb') as _f:
                        _f.write(record)
                    _f.close()
                    bar.next()
                bar.finish()
            except (BaseException,):
                print('file no')
                pass

    @staticmethod
    def create_folders():
        """ Create folders if they don't exist """
        # root_path = os.path.abspath((os.path.join(os.path.dirname(__file__), '..', '..')))
        if not os.path.exists('data/'):
            os.mkdir('data/')

        folders = ['AMATERAS', 'WIND1', 'WIND2', 'STEREO', 'ORFEES', 'GOES', 'SRH',
                   'QuietSun']
        for folder in folders:
            if not os.path.exists(os.path.join('data', folder)):
                try:
                    os.mkdir(os.path.join('data', folder))
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise exceptions.CannotCreateDirectory("Can not create directory")
