# Dose symmetric tilt scheme v2 [first step to multishot!!] [Tested on 27122021]
# !Python
import math
import numpy as np
import serialem as sem  # uncomment in serialEM

# DoseSymmetricTomo_v2

########## SETTINGS ##########

starttilt = 0  # Starting tilt angle
tiltstep = 3  # stage tilt step in degrees
tiltrange = 60  # Tilt series range (+/- this angle value from the starting angle) [make sure it is multiple of tiltstep]

tiltbacklash = -3  # negative tilts will be backlashed, must be negative value!

driftcrit = 3  # Angstrom/second
driftinterval = 10  # wait time between drift measurements in seconds
drifttimes = 10  # maximum number of drift measurements before skipping

# advanced
startdirection = 1  # starting direction from the initial tilt angle
groupsize = 2  # tilt group size for dose symmetric tilt scheme
# maxtilt = 67 # Maximum allowed tilt angle (hard-coded at the moment)
########## END SETTINGS ##########


########## Calculate tiltangles and initialize tracking arrays ##########
(tilts, trackndx) = ts_calculate_ds_angles_trackndx(starttilt, tiltrange, tiltstep, groupsize, startdirection)
ntilts = np.size(tilts)  # number of tilts
focus = np.zeros(ntilts)
IS = np.zeros((ntilts, 2))

########## Initialize tracking buffers ##########
T_size = sem.ReportCameraSetArea('T')[0:2]
T_size = [int(T_size[0]), int(T_size[1])]
R_size = sem.ReportCameraSetArea('R')[0:2]
R_size = [int(R_size[0]), int(R_size[1])]

T_buf = np.zeros((ntilts, T_size[0], T_size[1]))
R_buf = np.zeros((ntilts, R_size[0], R_size[1]))

########## Perform operations at starting tilts ##########

# Connect to SerialEM
sem.ConnectToSEM()

# Run Euccentric rough and fine
sem.Eucentricity(3)

# Tilt to starting angle
ts_tiltto(tilts[0], tiltbacklash)

# Realign to navigator item
# sem.RealigToNavItem(1)

# store stage position
(StageX, StageY) = sem.ReportStageXYZ()[0:2]

# Acquire starting tilt [First tilt is kept out of the loop. In future this step will be used as preparation for multishot.]
ts_tilt_ds_zero(0, 0)

# prevent runaway focus
sem.AbsoluteFocusLimits(-10, 10)
sem.FocusChangeLimits(-5, 5)

########## Perform dose symmetric acquisition ##########

for i in range(1, ntilts):
    ts_smart_tiltto(tilts[i], tiltbacklash)
    # (focusmin,ISxminus,ISyminus) = ts_tilt_minus(tilts[i])
    ts_tilt_ds(i, trackndx[i])

########## Reset ##########

sem.TiltTo(0)
sem.ResetImageShift()
sem.SetDefocus(0) 