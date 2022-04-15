#!Python
import math
import numpy as np
import serialem as sem


# ScriptName Geometry_functions

def axisangle2quaternion(axis, angle):
    ## axisangle2quaternion
    # A function to convert an axis-angle rotation to a rotation quaternion.
    # Quaternion is in the JPL format: [x,y,z,w];

    # Normalize axis
    n_axis = axis / math.sqrt(sum(np.square(axis)))
    print(n_axis)
    # Sine of angle
    s = math.sin(math.radians(angle / 2))

    # Quaternion
    q = np.zeros((4))
    print(q)
    q13 = n_axis * s
    q[0:3] = q13
    q[3] = math.cos(math.radians(angle / 2))

    return q


def quaternion2matrix(q):
    ## quaternion2matrix
    # A function to convert a quaternion to a rotation matrix. The quaternion
    # should be supplied in JPL format [x,y,z,w].

    # Convert

    # Initialize and fill rotation matrix
    mat = np.zeros((3, 3));
    mat[0, 0] = 1 - (2 * ((q[1]) ** 2) + (q[2] ** 2))
    mat[1, 0] = (2 * q[0] * q[1]) + (2 * q[3] * q[2])
    mat[2, 0] = (2 * q[0] * q[2]) - (2 * q[3] * q[1])
    mat[0, 1] = (2 * q[0] * q[1]) - (2 * q[3] * q[2])
    mat[1, 1] = 1 - (2 * ((q[0] ** 2) + (q[2] ** 2)))
    mat[2, 1] = (2 * q[1] * q[2]) + (2 * q[3] * q[0])
    mat[0, 2] = (2 * q[0] * q[2]) + (2 * q[3] * q[1])
    mat[1, 2] = (2 * q[1] * q[2]) - (2 * q[3] * q[0])
    mat[2, 2] = 1 - (2 * ((q[0] ** 2) + (q[1] ** 2)))

    return mat


def quaternion_normalize(q):
    ## quaternion_normalize
    # A function to normalize quaternions, based on the principle that for a
    # unit quaternion, ||q|| = 1.

    # Normalize

    magnitude = math.sqrt(sum(np.square(q)))
    norm_q = q / magnitude

    return norm_q


# # quaternion test
#
# axis = np.array([0,1,0])
# angle = -30
# q = axisangle2quaternion(axis,angle)
# print(axis,q)
# axis = np.array([0,1,1])
# angle = 30
# q = axisangle2quaternion(axis,angle)
# print(axis,q)
# norm_q = quaternion_normalize(q)
# print(norm_q)
# mat = quaternion2matrix(q)
# print(mat)



