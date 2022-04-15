import serialem as sem
import numpy as np


def StandardFocus():
    print('Setting Eucentric Focus!')
    sem.GoToLowDoseArea('R')
    sem.SetEucentricFocus()


def checkdewarstatus(dewartime):
    i = 0
    while i < dewartime:
        iffilling = sem.AreDewarsFilling()
        if iffilling == 1:
            print('waiting 60 sec.....')
            time.sleep(60)
        else:
            print('Dewars are NOT filling!')
            break


def cycledefocus(df_low, df_high, delta):
    # Generate the defocus array
    defocii = np.arange(df_low, df_high + delta, delta)
    print(defocii)

    # Check current target defocus
    td = sem.ReportTargetDefocus()
    print(td)

    # Set next target defocus from the defocus array
    if np.any(defocii == td):

        # Generate new defocus ndx
        ndx = np.where(defocii == td)[0] + 1
        print(ndx)

        # cycle back if ndx is greater than the array size
        if ndx > np.size(defocii) - 1:
            ndx = 0

        td = defocii[ndx]

    else:
        # set Target defocus to the lower defocus value
        td = defocii[0]

    sem.SetTargetDefocus(td)

    sem.ReportTargetDefocus()


def mapgrids(ndx):
    # Check if ndx array is empty (empty == use all slots)
    ndx = np.array(ndx)  # enforce np.array
    if np.size(ndx) == 0:
        ndx = np.arrange(1, 13)

    # Loop over selected slots
    for ndx in ndx:
        # print(ndx)
        occupied = sem.ReportSlotStatus(ndx)  # Check if the slot is occupied.
        if occupied == 1:
            # Perfom grid mapping operation
            sem.Screenup()  # Screen Up, just to be sure!
            sem.LoadCartridge(ndx)  # Long operation: Load the cartridge position 'ndx'
            sem.MoveStageTo(0, 0, 0)  # Move stage to 0,0,0
            sem.SetColumnOrGunValve(1)  # Open Column valves
            sem.M()  # Acquire montage. !! NEEDS a prior montage setup
            sem.NewMap()  # New map from montage

    sem.CloseFile()  # Close the map file
    sem.SetColumnOrGunValve(0)  # Close Column Valves

# # Common_functions test
# checkdewarstatus(10)
# #cycledefocus(-2,-4,-0.2)
#
# sem.Exit()
