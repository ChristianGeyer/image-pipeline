from target_scoring.geometry import camera_position_square_target
import numpy as np

def main():
    f = 50 # focal length in mm
    L = 100 # target dimension in mm
    Smax = 5.37 # largest sensor dimension in mm
    Smin = 4.04 # smallest sensor dimension in mm
    offset_n = 500
    coord_n, coord_t, dist, angle_deg = camera_position_square_target(f, L, Smin, offset_n)
    print(f"coord_n: {coord_n},\ncoord_t: {coord_t},\ndist: {dist},\nangle_deg: {angle_deg}")

    target_offset = 200

    tripod_sidelen = 720
    tripod_offset = tripod_sidelen / 2 * np.tan(np.deg2rad(30))

    print()
    print(f"final pos: {offset_n} mm to the side, {np.round(coord_t + tripod_offset + target_offset, 0)}mm forward.")


if __name__ == "__main__":
    main()
