# import the py-EM module and make its functions available
import pyEM as em
from pathlib import Path

# Inputs
navfile = "D:/users/Sagar/serialEM_tests_25122021/python-tests/16012022/nav_5.nav"
record_map = 'record'  # TEMPLATE map

# Read Navigator file into dictionary
navlines = em.loadtext(navfile)
allitems = em.fullnav(navlines)

# Parse items set to Acquire
acq = filter(lambda item: item.get('Acquire'), allitems)
acq = list(filter(lambda item: item['Acquire'] == ['1'], acq))

# Parse record template
(recorditem, junk) = em.nav_item(navlines, record_map)
if recorditem == []:
    raise Exception('ERROR!  No reference map with label "' + record_map + '" specified!')
record_merge = em.mergemap(recorditem)
r_header = record_merge['mergeheader']


# Find anchor map [map on which positions were drawn]
# print(on1[0]['DrawnID'])
anchor = filter(lambda item: item.get('MapID'), allitems)
anchor = list(filter(lambda item: item['MapID'] == on1[0]['DrawnID'], anchor))

# store stage position
(StageX,StageY) = sem.ReportStageXYZ()[0:2]
print(StageX)
print(StageY)
print(float(outnav1[1]['StageXYZ'][1]))
StageDif_X = float(outnav1[1]['StageXYZ'][0])-float(anchor[0]['StageXYZ'][0])
StageDif_Y = float(outnav1[1]['StageXYZ'][1])-float(anchor[0]['StageXYZ'][1])
print(StageDif_X,StageDif_Y)

# store stage position
(StageX,StageY) = sem.ReportStageXYZ()[0:2]

print(StageX)
print(StageY)

sem.ReportImageShift()

sem.ImageShiftByStageDiff(StageDif_X,StageDif_Y,2,1)
sem.V()
sem.R()

sem.ReportImageShift()
