def initialize_defaults():
    global driftcrit, drifttimes, driftinterval, startdirection, groupsize, tiltbacklash

    tiltbacklash = -1  # negative tilts will be backlashed, must be negative value!

    driftcrit = 3  # Angstrom/second
    driftinterval = 10  # wait time between drift measurements in seconds
    drifttimes = 10  # maximum number of drift measurements before skipping

    # advanced
    startdirection = 1  # starting direction from the initial tilt angle
    groupsize = 2  # tilt group size for dose symmetric tilt scheme
    # maxtilt = 67 # Maximum allowed tilt angle (hard-coded at the moment)
