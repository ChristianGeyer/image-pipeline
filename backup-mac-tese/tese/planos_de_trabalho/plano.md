# Plano de trabalho - sistema automático de pontuação de alvos de tiro desportivo

## 0 - Requisitos do sistema

### 0.1 - Definir requisitos de exatidão do sistema

* Definir métricas operacionais para avaliar o sistema.
* Definir valores objetivo para as métricas.
* Traduzir métricas operacionais para exatidão espacial

### 0.2 - Condições operacionais do sistema

* Definir os cenários possíveis de operação
    * número de impactos máximo
    * alvo sair e entrar do enquadramento da câmara

## 1 - Câmara

### 1.1 - Resolução da câmara

* Traduzir exatidão espacial para resolução da câmara

### 1.2 - Posicionamento da câmara

* Definir o posicionamento ótimo da câmara de forma a minimizar erros óticos

### 1.3 - Calibração Intrínseca

* Design das imagens de calibração
    * padrão de xadrez
    * ChAruCo
* Definir protocolo de calibração
    * Sequência de ações
    * ficheiros gerados
    * validação da calibração

### 1.4 - Calibração Extrínseca

* Criar calibração extrínseca automática
    * ficheiros gerados
    * validação

### 1.5 - Distorção e Perspetiva

* Criar módulo que retira a distorção das imagens e transforma a perspetiva para plano frontal

## 2 - Coordenadas centro do alvo

### 2.1 - CNN para localização da região preta do alvo

* Yolo
* arquitetura customizada

### 2.2 - Segmentação da região preta do alvo

* métodos clássicos:
    * remover ruído
    * Thresholds
    * morfológicos
    * contornos

### 2.3 - Determinar centro do alvo

* Bounding box
* Análise de momentos (centro de massa)
* Hough Transform
* Regressão de círculo
    * mínimos quadrados linear (solução fechada)
    * função de custo geométrica, problema não linear, métodos iterativos

## 3 - Centros dos impactos

### 3.1 - CNN para localização dos aglomerados de impactos

* Yolo
* Faster R-CNN
* arquitetura customizada

### 3.2 - Segmentação de impactos sobrepostos

* Watershed
* Pesquisar outros

### 3.3 - Segmentação de impactos isolados

* semelhante ao ponto 2.2
* métodos clássicos:
    * remover ruído
    * Thresholds
    * morfológicos
    * contornos

### 3.4 - Determinar centro dos impactos

* semelhante ao ponto 2.3
* Bounding box
* Análise de momentos (centro de massa)
* Hough Transform
* Regressão de círculo
    * mínimos quadrados linear (solução fechada)
    * função de custo geométrica, problema não linear, métodos iterativos

## 4 - Pontuação

### 4.1 - Coordenadas relativas

* Direto

### 4.2 - Pontuação

* Pontuação contínua
* Pontuação decimal
* Casos marginais (impacto a tocar num círculo)

## 5 - Evolução temporal do sistema

### 5.1 - Máquina de estados

* Máquina de estados a descrever estados possíveis de imagem
    * sem alvo
    * novo alvo
    * número de impactos
    * alvo antigo / alvo novo

### 5.2 - Subtração temporal de imagens

* Deteção de novos impactos por subtração de imagens

## 6 - Tratamento de alvos

### 6.1 - Recolha de alvos para CNN

* Protocolo de criação de alvos
    * alvos dos 3 tipos
    * até 8 impactos
    * parar na primeira sobreposição de impactos

### 6.2 - Recolha de sequência temporal 

* Simular vários cenários para testar o comportamento temporal da máquina de estados / testar subtração temporal

## 7 - Dados 

* Definir dados a armazenar
* Definir estrutura da base de dados

## 8 - Alvo Virtual

* criar aplicação desenho de um alvo virtual com impactos, com as informações relevantes em forma de tabelas.


## 9 - Supporte, Proteção, Hardware

* Comprar / Desenhar suporte da câmara com as posições desejadas
* Suportar proteção da câmara
* Usar cabos usb 

