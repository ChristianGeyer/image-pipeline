# Calibration Pipeline

### 1-Create a charuco pattern

#### 1.1-Number of corners N

If Zhangs' method is used, each image must have at least 4 corners to resolve the 8 degrees of freedom of the homography of each image. Due to the distortion parameters, it is important to have more points so that less images are required to resolve the parameters. Also, it is not good when the corners are too close, so the number of points should be a trade off between information and quality of corner detection.

### 2-Corner Detection

Some algorithm must be able to detect the corners of a charuco pattern. To associate correctly with the world coordinates of the points, the aruco symbols must be used.

### 3-Intrinsic Calibration

Zhang's Method will be used to find the K and distortion coefficients.

#### 3.1-Number of calibration images

The number of calibration images I needed depends on the number of parameters being found (5 + 6*I + distortion_params) and the number of equations per image (2*I*N), where N is the number of corners per image

#### 3.2-Algorithm

Probably some opencv function already does the whole pipeline. We need to do zhang's method for an initial guess, then run a nonlinear least squares optimization of the reprojection error.

### 4-Extrinsic Calibration

Given the Xi world coordinates and the xi undistorted pixel coordinates, we find the optimal H in the least squares sense, using findHomography from opencv, which is minimizing the reprojection error (using iterative LM? or maybe using SVD somehow?). From H and K, we find [r1, r2, t] = K^-1*H.

### 5-World coordinates

We apply the reverse operation, going from pixel coordinates to world coordinates. We need to define the frame of the world coordinates in the plane of the object that we want to represent. Then, after discretizing that plane with some resolution similar to the previous resolution, we get the pixel values for each world coordinate by fetching a bilinear interpolation in the pixel space. 

