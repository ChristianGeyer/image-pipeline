# Preliminary Work Plan

This work plan is organized into **phases driven by dependencies**, progressing from geometric foundations to robust detection, refinement, scoring, and optional system integration.

---

## Phase 1 — Camera & Geometry (Foundational)

**Goal:** Establish a stable, unbiased geometric mapping from image pixels to target coordinates.

### 1.1 Camera selection & constraints
- Define minimum resolution needed (px/mm at target plane)
- Evaluate current camera against requirements
- Decide:
  - keep current camera, or
  - select an alternative (sensor size, lens, manual focus)

📌 **Decision point:** camera choice

---

### 1.2 Camera placement study
- Define possible camera positions (distance, angle)
- Compute pixel density for each configuration
- Evaluate trade-offs:
  - resolution vs ease of setup
  - field of view vs distortion

📌 **Output:** known, fixed geometry

---

### 1.3 Intrinsic calibration
- Capture calibration images (checkerboard / ChArUco)
- Estimate:
  - focal length
  - principal point
  - distortion coefficients
- Validate reprojection error

📌 **Core task — cannot skip**

---

### 1.4 Extrinsic calibration / homography
- Define target plane reference
- Compute homography
- Verify:
  - straight rings appear circular
  - known distances match expected values

📌 **Core task**

---

### 1.5 Image rectification pipeline
- Implement:
  - undistortion
  - perspective correction
- Validate on multiple images

📌 **Output:** rectified target image

---

### 1.6 Setup repeatability *(optional / later)*
- Investigate:
  - reuse of calibration
  - physical markers
  - mechanical constraints

⚠️ **Optimization task — not blocking Phase 2**

---

## Phase 2 — Dataset & Classical Baselines

**Goal:** Understand the data and establish geometry-only performance limits.

This phase is divided into:
- **Phase 2A:** controlled background (best-case validation)
- **Phase 2B:** natural background (robustness assessment)

---

### Phase 2A — Classical Baselines with Controlled Background

**Purpose:**  
Validate calibration and geometric accuracy under ideal conditions, and establish an upper bound on performance.

#### 2A.1 Image acquisition (controlled background)
- Use a known, uniform background color
- Capture:
  - clean targets
  - single bullets
  - controlled overlaps

📌 **Output:** controlled dataset

---

#### 2A.2 Target segmentation (classical)
- Thresholding / edge detection
- Morphological cleanup
- Extract target region

---

#### 2A.3 Bullet candidate extraction (classical)
- Threshold / edge-based detection
- Connected components
- Rough center estimation

---

#### 2A.4 Circle fitting baseline
- Implement:
  - algebraic circle fitting
  - geometric refinement
- Evaluate center error (px / mm)

📌 **Reference performance under ideal conditions**

---

#### 2A.5 Baseline error analysis
- Compute:
  - center error distribution
  - score error distribution
- Compare with ISSF tolerance

📌 **Establish best-case accuracy**

---

### Phase 2B — Classical Baselines with Natural Background

**Purpose:**  
Evaluate robustness and expose limitations of classical methods under realistic conditions.

#### 2B.1 Image acquisition (natural background)
- Use realistic target surroundings
- Capture:
  - worn targets
  - lighting variations
  - overlapping bullets

📌 **Output:** realistic dataset

---

#### 2B.2 Target segmentation (classical)
- Apply same methods as Phase 2A
- Analyze sensitivity to noise and illumination

---

#### 2B.3 Bullet candidate extraction (classical)
- Apply same detection pipeline
- Observe:
  - false positives
  - missed detections
  - parameter sensitivity

📌 **Expected low robustness**

---

#### 2B.4 Comparative analysis
- Compare results from Phase 2A and Phase 2B
- Document:
  - failure modes
  - sensitivity sources

📌 **Motivation for deep-learning detection**

---

## Phase 3 — CNN-Based Detection (Robustness Phase)

**Goal:** Achieve high recall and robustness, not final geometric precision.

### 3.1 Dataset labeling
- Label:
  - target bounding boxes
  - bullet bounding boxes
- Decide:
  - single bullet per box?
  - group overlapping bullets?

📌 **Decision point**

---

### 3.2 Target detector training
- Train CNN for target localization
- Evaluate:
  - recall
  - robustness to lighting and target damage

📌 **Should be relatively easy**

---

### 3.3 Bullet detector training
- Train CNN for bullet detection
- Focus on:
  - recall ≥ 0.99
- Evaluate PR curves

📌 **Core detection task**

---

### 3.4 Detection operating-point selection
- Analyze:
  - recall(c)
  - precision(c)
- Select:
  - high-recall operating threshold

📌 **Critical design decision**

---

## Phase 4 — Geometric Refinement & Overlap Handling

**Goal:** Convert robust detections into high geometric accuracy.

### 4.1 ROI extraction
- Crop detection outputs
- Normalize scale and orientation

---

### 4.2 Bullet segmentation within ROI
- Edge detection
- Binary mask creation
- Noise suppression

---

### 4.3 Overlap resolution *(if needed)*
- Distance transform
- Marker extraction
- Watershed segmentation

📌 **Conditional task**

---

### 4.4 Precise center extraction
- Contour extraction
- Robust circle fitting (Huber / IRLS)
- Sub-pixel refinement

📌 **Core accuracy task**

---

### 4.5 Accuracy evaluation
- Compare:
  - raw detection centers
  - refined centers
- Quantify improvement

📌 **Main technical contribution**

---

## Phase 5 — Scoring & Validation

**Goal:** Connect geometry to scoring correctness.

### 5.1 Scoring function
- Implement ISSF scoring logic
- Map distance → decimal score

---

### 5.2 Scoring error analysis
- Compute:
  - continuous score error
  - discrete score correctness
- Estimate:
  - probability of correct score

📌 **Key thesis metric**

---

### 5.3 Stress testing
- Test:
  - overlapping bullets
  - torn holes
  - edge cases

---

## Phase 6 — System Integration *(Late / Optional)*

**Goal:** Produce a working system; not core research.

### 6.1 Temporal differencing
- Detect new shots
- Trigger processing when needed

---

### 6.2 Main processing loop
- Integrate modules
- Ensure stability

---

### 6.3 Visualization
- Virtual target rendering
- Score display

---

### 6.4 Data storage *(optional)*
- Store:
  - bullet centers
  - scores
  - timestamps
