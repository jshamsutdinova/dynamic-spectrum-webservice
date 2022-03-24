import sys
import warnings
from datetime import datetime, time
from dynamicspectrum.builder import Builder


if not sys.warnoptions:
    warnings.simplefilter('ignore')

user_date = datetime(2019, 5, 29)
user_time_from = time(1, 30, 0)
user_time_to = time(2, 0, 0)
# spectrometer = ['stereo']
spectrometer = ['wind1', 'wind2']
spectropolarimeter = ['orfees']
# spectropolarimeter = ['amateras', 'orfees']
time_profile = ['goes']
parameter = 'I'

spectrum = Builder()
spectrum.combine_spectrum(user_date, user_time_from, user_time_to,
                          spectrometer, spectropolarimeter, time_profile, parameter)
