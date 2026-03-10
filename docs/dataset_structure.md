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
│   ├── intrinsics/
│   │   ├── iid01/
│   │   │   ├── metadata.yaml
│   │   │   ├── timestamps.csv
│   │   │   ├── img0001.png
│   │   │   ├── img0002.png
│   │   ├── iid02/
│   │   ├── ...
│   ├── extrinsics/
│   │   ├── eid01/
│   │   │   ├── metadata.yaml
│   │   │   ├── timestamps.csv
│   │   │   ├── img0001.png
│   │   │   ├── ...
│   │   ├── eid02/
│   │   ├── ...
│   ├── targets/
│   │   ├── tid01/
│   │   │   ├── metadata.yaml
│   │   │   ├── timestamps.csv
│   │   │   ├── img0001.png
│   │   │   ├── ...
│   │   ├── tid02/
│   │   ├── ...
│   └── backgrounds/
│   │   ├── bid01/
│   │   │   ├── metadata.yaml
│   │   │   ├── timestamps.csv
│   │   │   ├── img0001.png
│   │   │   ├── ...
│   │   ├── bid02/
│   │   ├── ...
```

session metadata:

```
date: 2026-03-09
session_id: session01 
intrinsics_ids: [iid01, iid02, ...]
extrinsics_ids: [eid01, eid02, ...]
targets_ids: [tid01, tid02, ...]
backgrounds_ids: [bid01, bid02, ...]
```

intrinsics metadata:

```
date: 2026-03-09
session_id: session01
intrinsics_id: iid01
```

extrinsics metadata:
```
date: 2026-03-09
session_id: session01
extrinsics_id: eid01
intrinsics_ref:
    date: 2026-03-08
    session_id: session02
    intrinsics_id: iid01
```

targets metadata:
```
date: 20260309
session_id: session01
targets_id: tid01
intrinsics_ref:
    date: 20260308
    session_id: session02
    intrinsics_id: iid01
extrinsics_ref:
    date: 20260308
    session_id: session02
    extrinsics_id: eid01
backgrounds_ref:
    date: 20260308
    session_id: session02
    backgrounds_id: bid01
```

backgrounds metadata:
```
date: 20260309
session_id: session01
backgrounds_id: bid01
intrinsics_ref:
    date: 20260308
    session_id: session02
    intrinsics_id: iid01
extrinsics_ref:
    date: 20260308
    session_id: session02
    extrinsics_id: eid01
```

timestamp.csv files all have the same format:

```
file_id, file_name, date_str, timestamp_ms
1, img0001.png,20260308_114003_213, 1827409362482
...
```
    