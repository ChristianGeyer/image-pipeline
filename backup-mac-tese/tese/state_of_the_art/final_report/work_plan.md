# Preliminary Work Plan

## Phase 1 - Camera and geometry

**Goal:** Extract images for image processing pipeline

### 1.1 Camera constraints and placement
- define minimum camera resolution (px/mm)
- define camera placement for both target types
- define camera lens settings for both target types
- evaluate current camera against requirements

**decision:** keep/change camera?

### 1.2 Intrinsic calibration
- design calibration images (checkboard / ArUco)
- capture callibration images
- implement intrinsic calibration
    - fx, fy, cx, cy
    - distortion coeficients
- validate reprojection error

**core task**

### 1.3 Extrinsic calibration 
- automatic capture of calibration image
- implement extrinsic calibration
    - homography

**core task**

### 1.4 Image rectification
- implement
    - undistortion
    - perspective correction
        - centered image
        - set px/mm
- validate extrinsic calibration image
- validate multiple target images

**core task**

### 1.5 Setup repeatability
- investigate ways to facilitate setup of
    - lens configuration
    - camera placement

**optional task**

---

## Phase 2A - Classical Baselines with Controlled Background and ideal conditions

### 2A.1 image acquisition (controlled background)
- use known, uniform background
- use ideal targets:
    - single bullet






