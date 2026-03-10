# ATCS - Automatic Target Classification System

### Introduction

1. Show the title of the dissertation.

2. Summarize the **motivation** and the **goal**.

### State of the Art

1. Take aways from the accuracy analysis.

2. classical methods

3. deep-learning CNN methods

### System Structure

1. Image Processing Pipeline

---

### Script

### Slides

1. 

I will review the state of the art research made for the development of an Automatic Target Classification System.

* title
* name
* supervisor

2. 

The accuracy requirements of sport shooting are established by the ISSF - International Sport Shooting Federation. Many real time automatic scoring systems exist and are being used by the community. The solutions have high accuracy, but the technologies involved have a high cost and need specialized hardware.

Some amateur clubs don't have any real time automatic scoring system implemented. There is a need for a low cost alternatice that achieves enough scoring accuracy.

* list of existing technologies
* ISSF - International Sport Shooting Federation
* high precision for high cost

Improved text:



3.

Vision-based systems offer an alternative that trades off cost and precision. The targets of study will be the ISSF official paper targets for the 10m-air-rifle and 10m-air-pistol disciplines. The 10m-air-rifle dimensions are smaller and represent the bottleneck of precision requirements.

* figure with camera placement
* figures of both targets

4.

An accuracy analysis was made to understand the accuracy requirements of any scoring system. The results showed that the combination of decimal scoring resolution with the small physical size of 10m-air-rifle targets demad very high precision systems.

* image with the error model, and the convolution
* table with precision-accuracy values (precision as the maximum continuous scoring error, accuracy as the percentage of correct scores)

5.

The classical approaches analyse the image geometry and pixel intensities. One typical pipeline consists of performing thresholds, doing morphological operations, finding connected components, extracting contours and fitting a circle to the contour points using moment analysis or circle regression. Watershed is used to segment overlaping bullets. Hough Circle Transform can be used to find circles in an image. Images from a video stream may be subtracted, which is temporal differencing and helps detect new bullets. 

These approaches show high precision for well conditioned images, but show sensitivity to noise and image imperfections. They also rely heavily on parameter tuning, and usually work under specific conditions, showing a lack of robustness and generalisation.

* List of the concepts involved in classical pipelines.
* high precision for well conditioned images
* rely on parameter tuning
* lack of robustness and generalisation

6. 

Deep-Learning approaches use CNN - Convolutional Neural Networks - and can be trained to perform detection, segmentation or even regression. The main architectures for detection fall into one of the two categories of 1 stage vs 2 stage detectors. 1 stage detectors, like the Yolov8 architecture, show good precision and fast inference times, whereas 2 stage detectors like Faster R-CNN show higher precision but slower inference times. 

The geometric precision of deep-learning approaches is usually poor and not sufficient for the scoring requirements. The detection task is performed in a robust, generic way, being superior to classical methods. 

* 1 stage: Yolov8
* 2 stage: Faster R-CNN
* good for detection: robust, generic

7.

The proposed structure of the image processing subsystem starts with the image acquisition. The camera placement and settings have to be decided, and algorithms for correcting perspective and distortion have to be implemented.

The image analysis is divided into two branches, 1 for te target center and the other for the bullet centers. Localization/Detection will be done by a deep-learning approach. The overlapping bullets may be resolved using watershed. Geometric refinement will be done using classical approaches like contour extraction and cicle regression, or hough circles ttransform.

At the end, relative coordinates of each bullet will be extracted and used to compute each bullet's score. The information is going to be sent to the Database and to the visualization module to show a virtual target to the athlete.  

* Figure showing the modules of the image processing subsystem

# Preliminary Work Plan

### Camera

* 1.0 Camera resolution: If current camera being used does not have the adequate characteristics, search a better camera that facilitates different setups and callibration process, and also has enough resolution.

* 1.1 Camera Position and Camera settings: How to maximize the pixel density while having a an easy way to setup the camera

* 1.2 Camera Callibration: Callibration Images, Undistortion, Perspective Correction

* 1.3 Protocol for easy setup: How to quickly position the camera without loosing callibration. Big problem: Taking multiple callibration images is time consuming. How to make 2 setups using the same manual camera?

* 1.4 Camera support: How will the camera be fixed?

### Target-Bullet Pipeline

2.1 Prepare a dataset to detect the target

2.2 Train models

2.3 Implement Segmentation using classical methods

2.4 Implement Center extraction using classical methods, or circle regression

### Bullet Pipeline

3.1 Prepare a dataset to detect bullets: Decide if overlapping bullets should be separated or grouped into 1 object. Decide if detection already classifies number of overlapping bullets.

3.2 Implement Segmentation using classical methods: Might need the Watershed algorithm if 1 object contains multiple bullets.

3.3 Implement Center extraction using classical methods, or circle regression. (might be different from 2.4 to optimize for bullets)

### Scoring

4.1 Implement scoring function

### Main Program

5.1 Function to detect if a new target appeared.

5.2 Function to detect new bullets: This is where temporal differencing might help

5.3 Main loop to call the modules implemented to keep detecting and scoring incoming bullets.

### Database

6.1 Develop a Relational Model for the Database: What values should be stored, how should competition results be stored, ...

### Virtual Target

7.1 Implement a visualisation of the target

### Hardware and Communications

8.1 Decide the structure of the Communications: How will different parts of the system communicate with each other? Cables? Wifi? Which components communicate?

8.2 Protocols: How will messages be structured to be sent between different components of the system? Which function must be implemented to send and receive information? What configuration will we use, master slave, publisher subscriber, ...?



# Script

### Slide 1

Na minha dissertação, vou desenvolver um sistema de classificação automática de alvos para tiro desportivo.

### Slide 2

As regras e os requisitos técnicos de sistemas de pontuação de alvos de tiro desportivo são estabelecidas pela ISSF, a federação internacional de tiro desportivo.

Existem várias soluções de pontuação automática que atingem a exatidão requirida pela ISSF. No entanto, as tecnologias usadas são de alto custo e envolvem hardware especializado.

Surge então a necessidade de desevolver uma alternativa de baixo custo que consiga atingir um nivel de exatidão suficiente.

### Slide 3

A alternativa vai ser implementada por um sistema baseado em visão, usando uma câmara industrial de baixo custo ligada a um computador. O objetivo é desenvolver um sistema que reaja em tempo real e que atinga a exatidão necessária.

Os alvos de estudo vão ser os alvos das disciplinas de carabina de ar a 10m e de pistola de ar a 10m.

### Slide 4

Foi feita uma análise dos requisitos de exatidão para qualquer sistema de pontuação. Verificou-se que para obter taxas de acerto de pontuação elevadas, os requisitos de exatidão envolvem dimensões bem abaixo do milímetro. O alvo que exige este nível de exatidão é o de carabina-de-ar a 10m devido à sua dimensão reduzida.

### Slide 5

Os métodos clássicos de visão por computador foram estudados. Estes métodos mostram ser adequados para imagens em condições boas, conseguindo obter alta exatidão. No entanto, exigem calibração de vários parâmetros definidos de forma heuristica, e não são robustos, mostrando erros quando as condições das imagens se desviam das condições esperadas.

### Slide 6

A tarefa de pontuação de alvos pode ser subdividida em deteção, onde se localiza os objetos, e em segmentação, onde se determina o contorno dos objetos. Os métodos baseados em deep-learning e em redes convolucionais mostram ser adequados para a tarefa de deteção, atingindo alto nível de precisão para recall elevado, sendo muito robustos. A segmentação não atinge a exatidão necessária para os requisitos ISSF.

### Slide 7

A robustez dos métodos baeados em deep-learning e a exatidão geométrica dos métodos clássicos sugerem o desenvolvimento de uma solução híbrida. Foi elaborado um diagrama de blocos a representar a pipeline sugerida para o sistema de processamento de imagem. Após obter a imagem, as tarefas de deteção e segmentação/regressão são divididas, e serão implementados os algoritmos adequados para cada tipo de tarefa. Após extrair as coordenadas do centro do alvo e dos centros das balas, é calculada a pontuação, e enviada para subsistemas 
de armazenamento de dados e de visualização.







