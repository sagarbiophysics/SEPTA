def initialize():
    global StageX, StageY, focus, IS, driftcrit, drifttimes, driftinterval, T_buf, R_buf, T_size, R_size
    StageX = []
    StageY = []
    focus = []
    IS = []
    driftcrit = 3  # Angstrom/second
    driftinterval = 10  # wait time between drift measurements in seconds
    drifttimes = 10  # maximum number of drift measurements before skipping

    T_buf = []
    R_buf = []
    T_size = []
    R_size =[]

