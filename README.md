[README_CalcEst.md](https://github.com/user-attachments/files/28657498/README_CalcEst.md)
# Calculo-estoc-stico-
Código de la clase de calculo estocástico - UP Finanzas 2026
# Calculo-Estocastico

Repositorio de código para el curso de **Cálculo Estocástico**.

---

## Estructura

```
Calculo-Estocastico/
├── Codigo.py          ← Motor principal del Proyecto Final (Labs 1–5 + Proyecto 6)
├── donsker.jsx        ← Visualización interactiva del Teorema de Donsker (React)
└── levy_area_Z2.gif   ← Animación del Área de Lévy
```

---

## Archivos

### `Codigo.py` — Motor del Proyecto Final

Motor de cálculo completo del Proyecto Final. Genera datos sintéticos calibrados
a parámetros de AAPL, ejecuta cinco laboratorios y exporta figuras en PDF
junto con un archivo `results.json` con los resultados numéricos.

| Lab | Tema | Método |
|-----|------|--------|
| 1 | Estimación de un MBG con datos de una acción | MLE + Monte Carlo |
| 2 | Volatilidad realizada y ventanas móviles | Desv. estándar móvil anualizada |
| 3 | Opciones europeas vanilla | Monte Carlo + Black-Scholes |
| 4 | Opciones americanas (put) | Árbol binomial |
| 5 | Opciones parisinas down-and-out | Monte Carlo con reloj de permanencia |
| Proyecto 6 | Superficie de precio parisino V(H,D) | Monte Carlo, heatmap H × D |

**Dependencias:**
```bash
pip install numpy pandas matplotlib scipy
# Opcional para datos reales:
pip install yfinance
```

**Ejecución:**
```bash
python Codigo.py
```

Las figuras se guardan en `figs/` y los resultados numéricos en `results.json`.

---

### `donsker.jsx` — Visualización del Teorema de Donsker

Componente React que ilustra la convergencia en distribución del Teorema de Donsker (1951):

$$W_n(t) = \frac{S_{\lfloor nt \rfloor}}{\sqrt{n}} \xrightarrow{d} B(t) \quad n \to \infty$$

donde $S_k = \xi_1 + \cdots + \xi_k$ es una caminata aleatoria con $\xi_i \in \{-1,+1\}$
equiprobables y $B(t)$ es el movimiento browniano estándar.

**Funcionalidades:**
- Animación con control de velocidad (0.5×, 1×, 2×, 4×)
- Selector de $n \in \{100, 500, 1000, 5000\}$ para observar la convergencia
- Generación de nuevas muestras con rastros de trayectorias anteriores
- Indicador de valor instantáneo $W_n(t)$

**Requisitos:** React 18+, sin dependencias externas adicionales.

---

### `levy_area_Z2.gif` — Animación del Área de Lévy

Animación generada con `matplotlib` que ilustra el Área de Lévy de un proceso
estocástico bidimensional.

---

## Reproducibilidad

- `Codigo.py` usa semilla fija (`seed=20260526`) para resultados idénticos en cada ejecución.
- Los PDFs de entrega y datos pesados **no están en este repositorio** — residen en Google Drive.

---

## Curso

| | |
|---|---|
| Universidad | Universidad Panamericana |
| Curso | Cálculo Estocástico |
| Año | 2026 |
