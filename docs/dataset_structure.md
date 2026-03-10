date : 2026-03-09

version: v0

### tree structure special symbols

```
│   
├──
└── 
│   ├──
│   └──  
│   │   ├──
│   │   └──  
│   │   │   ├──
│   │   │   └── 
```

# Dataset Structure

```
Datasets/20260309/
├── session01/
│   ├── metadata.yaml
│   ├── patterns/
│   │   ├── pid01/
│   │   │   ├── metadata.yaml
│   │   │   ├── derived/
│   │   │   │   ├── metadata.yaml
│   │   │   │   ├── pattern.png
│   │   │   │   └── pattern_A4.pdf
│   │   ├── ...
│   ├── cameras/
│   │   ├── cid01/
│   │   │   └── metadata.yaml
│   │   ├── ...
│   ├── intrinsics/
│   │   ├── iid01/
│   │   │   ├── metadata.yaml
│   │   │   ├── timestamps.csv
│   │   │   ├── img0001.png
│   │   │   ├── ...
│   │   │   ├── derived/
│   │   │   │   └── intrinsics.yaml
│   │   ├── iid02/
│   │   ├── ...
│   ├── extrinsics/
│   │   ├── eid01/
│   │   │   ├── metadata.yaml
│   │   │   ├── timestamps.csv
│   │   │   ├── img0001.png
│   │   │   ├── ...
│   │   │   ├── derived/
│   │   │   │   └── extrinsics.yaml
│   │   ├── eid02/
│   │   ├── ...
│   ├── targets/
│   │   ├── tid01/
│   │   │   ├── metadata.yaml
│   │   │   ├── timestamps.csv
│   │   │   ├── img0001.png
│   │   │   ├── ...
│   │   │   ├── derived/
│   │   │   │   ├── undistorted/
│   │   │   │   ├── perspective_corrected/
│   │   ├── tid02/
│   │   ├── ...
│   └── backgrounds/
        ├── bid01/
        │   ├── metadata.yaml
        │   ├── timestamps.csv
        │   ├── img0001.png
        │   ├── ...
        │   ├── derived/
        │   │   ├── undistorted/
        │   │   ├── perspective_corrected/
        ├── bid02/
        ├── ...
```

session metadata:

```
date: 2026-03-09
session_id: session01 
pattern_ids: [pid01, pid02, ...]
camera_ids: [cid01, cid02, ...]
intrinsics_ids: [iid01, iid02, ...]
extrinsics_ids: [eid01, eid02, ...]
targets_ids: [tid01, tid02, ...]
backgrounds_ids: [bid01, bid02, ...]
```

pattern metadata:

```
pattern_id: pid01
pattern_type: charuco

squaresX: 7
squaresY: 7
square_len_mm: 15
marker_len_mm: 10
aruco_dict: DICT_4X4_1000
```
camera metadata:

```
camera_id: cid01
wmax: 4656
hmax: 3496
wreq: 4208
hreq: 3120
rotation_deg: 90
x_is_mirrored: True
x_should_be_mirrored: False
y_is_mirrored: True
y_should_be_mirrored: False
fps: 10
index: 0
```

intrinsics metadata:

```
date: 2026-03-09
session_id: session01
intrinsics_id: iid01
pattern_ref:
    date: 2026-03-07
    session_id: session01
    pattern_id: pid01
camera_ref:
    date: 2026-03-09
    session_id: session02
    camera_id: cid01
image:
    w: 3120
    h: 4208
    transformed: True
```

extrinsics metadata:
```
date: 2026-03-09
session_id: session01
extrinsics_id: eid01
pattern_ref:
    date: 2026-03-07
    session_id: session01
    pattern_id: pid01
camera_ref:
    date: 2026-03-09
    session_id: session02
    camera_id: cid01
intrinsics_ref:
    date: 2026-03-08
    session_id: session02
    intrinsics_id: iid01
image:
    w: 3120
    h: 4208
    transformed: True
```

targets metadata:
```
date: 2026-03-09
session_id: session01
targets_id: tid01
intrinsics_ref:
    date: 2026-03-08
    session_id: session02
    intrinsics_id: iid01
extrinsics_ref:
    date: 2026-03-08
    session_id: session02
    extrinsics_id: eid01
backgrounds_ref:
    date: 2026-03-08
    session_id: session02
    backgrounds_id: bid01
image:
    w: 3120
    h: 4208
    transformed: True
```

backgrounds metadata:
```
date: 2026-03-09
session_id: session01
backgrounds_id: bid01
intrinsics_ref:
    date: 2026-03-08
    session_id: session02
    intrinsics_id: iid01
extrinsics_ref:
    date: 2026-03-08
    session_id: session02
    extrinsics_id: eid01
image:
    w: 3120
    h: 4208
    transformed: True
```

timestamp.csv files all have the same format:

```
file_id, file_name, date_str, timestamp_ms
1,img0001.png,20260308_114003_213,1827409362482
...
```
    