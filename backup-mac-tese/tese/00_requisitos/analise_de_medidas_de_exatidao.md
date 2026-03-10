## 0.1 - Métricas de exatidão

### 1.1 - Concordância da pontuação decimal (Agreement A)

* Avaliada em comparação com um sistema de pontuação já existente.
* $A_{\Delta}$: Taxa de concordância com diferença menor ou igual a $\Delta$.
* Concordâncias relevantes: $A_{0.0}, A_{0.1}$

### 1.2 - Exatidão da pontuação contínua (Error E)

* Assumir erro não enviesado
* $E_{max}$: Distribuição homogénea do erro no intervalo $ e \in [-E_{max}, E_{max}]$

### 1.3 - Erro de localização em píxeis (Error E)

* $E_{max}^{px} = E_{optics}^{px} + E_{alg}^{px}$
* $E_{max}^{px}$: Erro de localização total em píxeis
* $E_{optics}^{px}$: Erro ótico de localização em píxeis (imagem desfocada, distorção)
* $E_{alg}^{px}$: Erro algorítmico de localização em píxeis
* $E_{optics}^{px} \approx (1..2)px$
* $E_{alg}^{px} < 1px$
* $E_{max}^{px} \approx 2px$