import numpy as np
from typing import List, Tuple

def camera_position_square_target(f : float,
                                  L : float,
                                  S : float,
                                  offset_n : float
                                  ) -> Tuple[float, float, float, float]:
    """
    input params:
        f : focal length
        L : target dimension
        S : sensor dimension
        offset_n :  offset along normal direction of object's plane-normal-vector
    return:
        (coord_n, coord_t, dist, angle)
        coord_n : camera's relative coordinate in normal direction of object's plane-normal-vector
        coord_t : camera's relative coordinate in tangential direction of object's plane-normal-vector
        dist : distance to object 
        angle_deg : angle between camera axis and object's plane-normal-vector
    """
    K = f*L/S
    dist = np.sqrt((K**2 + np.sqrt(K**4 - 4*(K*offset_n)**2))/2)
    coord_n = offset_n
    coord_t = np.sqrt(dist**2 - coord_n**2)
    angle = np.arctan2(coord_n, coord_t)
    angle_deg = np.rad2deg(angle)
    return (coord_n, coord_t, dist, angle_deg)

#def display_camera_position_square_target(L : float,
                                        #  )