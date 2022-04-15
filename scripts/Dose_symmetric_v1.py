# Dose symmetric tilt scheme v1 [simple: based on original serialEM implementations] [Tested on 26122021]
# !Python
import math
import numpy as np

# import serialem as sem     # uncomment in serialEM

# ScriptName DoseSymmetricTomo_v1
# include TS_functions


# Roll Buffers A-> H.
# Uses LowDose
# Run eucentric rough and fine
# Track plus K
# Track min  L
# Record plus M
# Record min  N

########## SETTINGS ##########

starttilt = 0  # Starting tilt angle
tiltstep = 3  # stage tilt step in degrees
tiltrange = 21  # Tilt series range (+/- this angle value from the starting angle) [make sure it is multiple of tiltstep]

tiltbacklash = -3  # negative tilts will be backlashed, must be negative value!

Driftcrit = 3  # Angstrom/second
Driftinterval = 10  # wait time between drift measurements in seconds
Drifttimes = 10  # maximum number of drift measurements before skipping

# advanced
startdirection = 1  # starting direction from the initial tilt angle
groupsize = 2  # tilt group size for dose symmetric tilt scheme
# maxtilt = 67 # Maximum allowed tilt angle (hard-coded at the moment)


########## END SETTINGS ##########


########## Calculate tiltangle array ##########

tilts = ts_calculate_ds_angles(starttilt, tiltrange, tiltstep, groupsize, startdirection)
ntilts = np.size(tilts)  # number of tilts

########## Perform operations at starting tilts ##########

# Run Euccentric rough and fine
# sem.Eucentricity(3)

# Tilt to starting angle
ts_tiltto(tilts[0], tiltbacklash)

# Realign to navigator item
# sem.RealigToNavItem(1)

# store stage position
(StageX, StageY) = sem.ReportStageXYZ()[0:2]

# Acquire starting tilt
ts_tilt_zero()

# prevent runaway focus
sem.AbsoluteFocusLimits(-10, 10)
sem.FocusChangeLimits(-5, 5)

########## Perform dose symmetric acquisition ##########

for i in range(1, ntilts):
    if tilts[i] > starttilt:
        ts_tiltto(tilts[i], 0)
        # (focusplus,ISxplus,ISyplus) = ts_tilt_plus(tilts[i])
        ts_tilt_plus()

    else:
        ts_tiltto(tilts[i], tiltbacklash)
        # (focusmin,ISxminus,ISyminus) = ts_tilt_minus(tilts[i])
        ts_tilt_minus()

########## Reset ##########

sem.TiltTo(0)
sem.ResetImageShift()
sem.SetDefocus(0)
