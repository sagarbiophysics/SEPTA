#!Python
import math
import numpy as np
import serialem as sem  # uncomment in serialem

import sem_default_var as defvar
# TS_functions


def ts_calculate_ds_ndx(ntilts, zerondx, groupsize, startdirection):
    ndx = np.zeros(ntilts)

    ndx[0] = zerondx
    i = 1  # tilt counter
    j = 1  # group counter
    direction = startdirection
    while i <= ntilts:

        incarray = np.arange(j, groupsize + j, 1)
        inc_1 = incarray * direction
        direction = -1 * direction
        inc_2 = incarray * direction
        # direction = -1 * direction
        inc = np.concatenate((inc_1, inc_2))

        batchsize = groupsize * 2

        if i + batchsize > ntilts - 1:
            incmax = (ntilts - 1) / 2
            inc = np.array([x for x in inc if abs(x) <= incmax])  # Check for any inc greater than incmax
            ndx[i:i + batchsize] = ndx[0] + inc
        else:
            ndx[i:i + batchsize] = ndx[0] + inc

        i = i + batchsize
        j = j + groupsize

    return ndx.astype(int)


def ts_calculate_dstrack_ndx(ntilts, zerondx, groupsize, startdirection):
    ndx = np.zeros(ntilts)

    ndx[0] = zerondx
    i = 1  # tilt counter
    j = 1  # group counter
    direction = startdirection
    while i <= ntilts:

        incarray = np.arange(j, groupsize + j, 1) - 1
        inc_1 = incarray * direction
        direction = -1 * direction
        inc_2 = incarray * direction
        # direction = -1 * direction
        inc = np.concatenate((inc_1, inc_2))

        batchsize = groupsize * 2

        if i + batchsize > ntilts - 1:
            incmax = (ntilts - 1) / 2 - 1
            inc = np.array([x for x in inc if abs(x) <= incmax])  # Check for any inc greater than incmax
            ndx[i:i + batchsize] = ndx[0] + inc
        else:
            ndx[i:i + batchsize] = ndx[0] + inc

        i = i + batchsize
        j = j + groupsize

    return ndx.astype(int)


def find_index(a, b):
    n = np.size(a)
    ndx = np.zeros(n)
    for i in range(1, n):
        ndx[i] = np.where(b == a[i])[0][0]

    return ndx.astype(int)


def ts_calculate_ds_angles_trackndx(starttilt, tiltrange, tiltstep, groupsize, startdirection):
    # global maxtilt
    maxtilt = 67  # Maximum allowed tilt (hard coded)

    tilts = np.arange(-tiltrange, tiltrange + tiltstep, tiltstep) + starttilt

    ntilts = np.size(tilts)
    zerondx = np.where(tilts == starttilt)[0]

    ndx = ts_calculate_ds_ndx(ntilts, zerondx, groupsize, startdirection)

    tilts = np.take(tilts, ndx)

    tilts_final = np.array([x for x in tilts if abs(x) <= maxtilt])  # Check for any tilts greater than tiltmax

    select_ndx = np.nonzero(np.in1d(tilts, tilts_final))[0]

    track_ndx = ts_calculate_dstrack_ndx(ntilts, zerondx, groupsize, startdirection)
    track_ndx_final = find_index(track_ndx[select_ndx], ndx[select_ndx])

    return tilts_final, track_ndx_final


def ts_calculate_ds_angles(starttilt, tiltrange, tiltstep, groupsize, startdirection):
    # global maxtilt
    maxtilt = 67  # Maximum allowed tilt (hard coded)

    tilts = np.arange(-tiltrange, tiltrange + tiltstep, tiltstep) + starttilt
    tilts

    ntilts = np.size(tilts)
    zerondx = np.where(tilts == starttilt)[0]

    ndx = ts_calculate_ds_ndx(ntilts, zerondx, groupsize, startdirection)
    tilts = np.take(tilts, ndx)

    tilts = np.array([x for x in tilts if abs(x) <= maxtilt])  # Check for any tilts greater than tiltmax

    return tilts


def ts_drift_track(AlignBuffer, driftcrit, drifttimes, driftinterval):
    # sem.T()
    # sem.AlignTo(AlignBuffer)
    sem.Delay(driftinterval)
    i = 0
    while i < drifttimes:
        sem.T()
        sem.AlignTo(AlignBuffer)
        (dx1, dy1, dx, dy, dx2d, y2) = sem.ReportAlignShift()  # CHECK CHECK
        dist = np.sqrt((dx * dx) + (dy * dy))
        rate = dist / driftinterval * 10
        print("Rate = " + str(rate) + "A/sec")
        if rate < driftcrit:
            print("Drift is low enough after shot " + str(i))
            break
        elif i < drifttimes:
            sem.Delay(driftinterval)
        else:
            print("Drift never got below " + str(driftcrit) + ": Skipping ...")
            break
        i += 1


def ts_tiltto(tiltangle, tiltbacklash):
    # tilt stage with backlash
    if tiltbacklash < 0:
        sem.TiltTo(tiltangle + tiltbacklash)
        # sem.TiltBy(tiltbacklash)
        sem.TiltTo(tiltangle)
    else:
        sem.TiltTo(tiltangle)


def ts_smart_tiltto(tiltangle, tiltbacklash):
    # tilt stage with backlash [determined automatically]
    tilt_current = sem.ReportTiltAngle()

    if tiltangle < tilt_current:
        sem.TiltTo(tiltangle + tiltbacklash)
        # sem.TiltBy(tiltbacklash)
        sem.TiltTo(tiltangle)
    else:
        sem.TiltTo(tiltangle)


def ts_autofocus(times):
    i = 0
    while i < times:
        sem.G()
        i += 1


def ts_tilt_zero():
    global StageX, StageY, focusplus, focusmin, ISxplus, ISxminus, ISyplus, ISyminus, driftcrit, drifttimes, driftinterval

    # drift and tracking
    sem.T()
    sem.Copy('A', 'K')
    sem.Copy('A', 'L')  # could be removed
    ts_drift_track('L', driftcrit, drifttimes, driftinterval)
    # autofocus
    ts_autofocus(3)

    # store defocus
    focusplus = sem.ReportTargetDefocus()  # CHECK CHECK
    focusmin = focusplus

    # acquire tilt image
    sem.R()
    sem.S()
    sem.Copy('A', 'M')
    sem.Copy('A', 'N')

    # store image shifts
    (ISxplus, ISyplus) = sem.ReportImageShift()[0:2]  # CHECK CHECK
    ISxminus = ISxplus
    ISyminus = ISyplus

    # tracking after just to be sure
    sem.T()
    sem.Copy('A', 'K')
    sem.Copy('A', 'L')

    # return focusplus,focusmin,ISxplus,ISxminus,ISyplus,ISyminus


def ts_tilt_plus():
    global StageX, StageY, focusplus, focusmin, ISxplus, ISxminus, ISyplus, ISyminus, driftcrit, drifttimes, driftinterval

    # reset stage XY
    sem.MoveStageTo(StageX, StageY)

    # set defocus and image shift
    sem.GoToLowDoseArea('R')
    sem.SetDefocus(focusplus)
    sem.SetImageShift(ISxplus, ISyplus)

    # drift and tracking
    sem.T()
    sem.AlignTo('K')  # could be removed
    ts_drift_track('K', driftcrit, drifttimes, driftinterval)

    # autofocus. Two rounds. Remove one G for single focus round.
    ts_autofocus(2)

    # store defocus
    focusplus = sem.ReportDefocus()  # CHECK CHECK

    # acquire tilt image
    sem.R()
    sem.S()

    # tracking after
    sem.AlignTo('M')
    sem.Copy('A', 'M')

    # store image shifts
    (ISxplus, ISyplus) = sem.ReportImageShift()[0:2]  # CHECK CHECK

    # tracking after just to be sure
    sem.T()
    sem.Copy('A', 'K')

    # return focusplus,ISxplus,ISyplus


def ts_tilt_minus():
    global StageX, StageY, focusplus, focusmin, ISxplus, ISxminus, ISyplus, ISyminus, driftcrit, drifttimes, driftinterval

    # reset stage XY
    sem.MoveStageTo(StageX, StageY)

    # set defocus and image shift
    sem.GoToLowDoseArea('R')
    sem.SetDefocus(focusmin)
    sem.SetImageShift(ISxminus, ISyminus)

    # drift and tracking
    sem.T()
    sem.AlignTo('L')  # could be removed
    ts_drift_track('L', driftcrit, drifttimes, driftinterval)

    # autofocus. Two rounds. Remove one G for single focus round.
    ts_autofocus(2)

    # store defocus
    focusmin = sem.ReportDefocus()  # CHECK CHECK

    # acquire tilt image
    sem.R()
    sem.S()

    # tracking after
    sem.AlignTo('N')
    sem.Copy('A', 'N')

    # store image shifts
    (ISxminus, ISyminus) = sem.ReportImageShift()[0:2]  # CHECK CHECK

    # tracking after just to be sure
    sem.T()
    sem.Copy('A', 'L')

    # return focusmin,ISxminus,ISyminus


def ts_tilt_ds(currentndx, trackndx):
    global StageX, StageY, focus, IS, driftcrit, drifttimes, driftinterval, T_buf, R_buf, T_size, R_size

    # reset stage XY !! can be moved to main loop !!
    sem.MoveStageTo(StageX, StageY)

    # set defocus and image shift
    sem.GoToLowDoseArea('R')
    sem.SetDefocus(focus[trackndx])
    sem.SetImageShift(IS[trackndx][0], IS[trackndx][1])

    # drift and tracking
    sem.T()
    sem.PutImageInBuffer(T_buf[trackndx].astype('int16'), 'K', T_size[0], T_size[1])

    sem.AlignTo('K')  # could be removed
    ts_drift_track('K', driftcrit, drifttimes, driftinterval)

    # autofocus. Two rounds. Remove one G for single focus round.
    ts_autofocus(2)

    # store defocus
    focus[currentndx] = sem.ReportDefocus()  # CHECK CHECK !! DONE!

    # acquire tilt image
    sem.R()
    sem.S()

    # tracking after
    sem.PutImageInBuffer(R_buf[trackndx].astype('int16'), 'M', R_size[0], R_size[1])
    temp_R_buf = np.frombuffer(sem.bufferImage('A'), dtype=np.int16)
    R_buf[currentndx] = temp_R_buf.reshape(R_size[0], R_size[1])

    sem.AlignTo('M')

    # sem.Copy('A','M')

    # store image shifts
    IS_current = sem.ReportImageShift()
    # print(IS[0])
    (IS[currentndx][0], IS[currentndx][1]) = (IS_current[0], IS_current[1])  # CHECK CHECK

    # tracking after just to be sure
    sem.T()
    temp_T_buf = np.frombuffer(sem.bufferImage('A'), dtype=np.int16)
    T_buf[currentndx] = temp_T_buf.reshape(T_size[0], T_size[1])
    # sem.Copy('A', 'K')


def ts_tilt_ds_zero(currentndx, trackndx):
    global StageX, StageY, focus, IS, driftcrit, drifttimes, driftinterval, T_buf, R_buf, T_size, R_size

    # drift and tracking
    sem.T()
    temp_T_buf = np.frombuffer(sem.bufferImage('A'), dtype=np.int16)
    T_buf[currentndx] = temp_T_buf.reshape(T_size[0], T_size[1])

    sem.Copy('A', 'K')
    ts_drift_track('K', driftcrit, drifttimes, driftinterval)
    # autofocus
    ts_autofocus(3)

    # store defocus
    focus[currentndx] = sem.ReportTargetDefocus()  # CHECK CHECK

    # acquire tilt image
    sem.R()
    sem.S()
    temp_R_buf = np.frombuffer(sem.bufferImage('A'), dtype=np.int16)
    R_buf[currentndx] = temp_R_buf.reshape(R_size[0], R_size[1])
    # sem.Copy('A','M')
    # sem.Copy('A','N')

    # store image shifts
    IS_current = sem.ReportImageShift()
    (IS[currentndx][0], IS[currentndx][1]) = (IS_current[0], IS_current[1])  # CHECK CHECK

    # tracking after just to be sure
    sem.T()
    temp_T_buf = np.frombuffer(sem.bufferImage('A'), dtype=np.int16)
    T_buf[currentndx] = temp_T_buf.reshape(T_size[0], T_size[1])

    # sem.Copy('A', 'K')
    # sem.Copy('A', 'L')


def ts_dose_symmetric_tomo_v2(starttilt,tiltstep,tiltrange):
    # Global variables
    global StageX, StageY, focus, IS, T_buf, R_buf, T_size, R_size, driftcrit, drifttimes, driftinterval

    # default variables
    defvar.initialize_defaults()
    tiltbacklash = defvar.tiltbacklash # negative tilts will be backlashed, must be negative value!

    driftcrit = defvar.driftcrit  # Angstrom/second
    driftinterval = defvar.driftinterval  # wait time between drift measurements in seconds
    drifttimes = defvar.drifttimes  # maximum number of drift measurements before skipping

    # advanced
    startdirection = defvar.startdirection  # starting direction from the initial tilt angle
    groupsize = defvar.groupsize  # tilt group size for dose symmetric tilt scheme
    # maxtilt = defvar.maxtilt # Maximum allowed tilt angle (hard-coded at the moment)


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


    # Tilt to starting angle
    ts_tiltto(tilts[0], tiltbacklash)

    # Realign to navigator item
    sem.RealigToNavItem(1)

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