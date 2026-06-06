# -*- coding: utf-8 -*-
"""
Motor de cálculo del Proyecto Final de Cálculo Estocástico.
Genera datos, ejecuta los 5 laboratorios y el Proyecto 6, produce figuras
y vuelca todos los resultados numéricos a results.json para el informe LaTeX.

NOTA SOBRE DATOS:
  Para garantizar reproducibilidad sin conexión, las figuras del informe se
  construyen con una serie sintética calibrada a parámetros realistas de una
  acción tecnológica. El bloque cargar_datos() incluye el código yfinance
  comentado: al ejecutarlo con internet se descargan precios reales de AAPL.
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from scipy.stats import norm

# ---------------------------------------------------------------------------
# Estilo de figuras (estética académica sobria, consistente con el informe)
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150,
    "font.family": "serif", "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "dejavuserif",
    "font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11,
    "axes.grid": True, "grid.alpha": 0.30, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#444444", "savefig.bbox": "tight",
    "legend.frameon": False, "figure.autolayout": False,
})
AZUL   = "#1f3b6e"
NARANJA= "#c8651b"
VERDE  = "#2e7d4f"
VINO   = "#8a2846"
GRIS   = "#666666"
MORADO = "#5a4a8a"
FIG = "/home/claude/proyecto/figs"

R = {}  # diccionario de resultados

# ===========================================================================
# 0. DATOS
# ===========================================================================
N_DIAS_ANIO = 252

def cargar_datos(ticker="AAPL", anios=3, seed=20260526):
    """
    Devuelve una serie de precios ajustados diarios.

    --- Versión datos reales (descomentar con conexión a internet) ---
    import yfinance as yf
    df = yf.download(ticker, period=f"{anios}y", auto_adjust=True)
    precios = df["Close"].dropna()
    return precios

    --- Versión sintética reproducible (la usada para este informe) ---
    Se genera un GBM con volatilidad variable en el tiempo (dos episodios
    turbulentos) para que el laboratorio de volatilidad realizada muestre
    'clustering' realista.
    """
    rng = np.random.default_rng(seed)
    n = int(anios * N_DIAS_ANIO)
    dt = 1.0 / N_DIAS_ANIO
    # Deriva anual base (log-deriva del MBG)
    mu = 0.22
    # Volatilidad anual variable: base 0.18 con dos repuntes (estrés de mercado)
    t = np.arange(n)
    sig = np.full(n, 0.18)
    sig += 0.26 * np.exp(-0.5 * ((t - 0.42 * n) / (0.045 * n)) ** 2)   # crisis 1
    sig += 0.16 * np.exp(-0.5 * ((t - 0.80 * n) / (0.035 * n)) ** 2)   # crisis 2
    sig += 0.03 * np.sin(2 * np.pi * t / 60.0)                         # ondulación
    Z = rng.standard_normal(n)
    log_ret = (mu - 0.5 * sig ** 2) * dt + sig * np.sqrt(dt) * Z
    precios = 150.0 * np.exp(np.cumsum(log_ret))
    fechas = pd.bdate_range("2023-05-26", periods=n)
    return pd.Series(precios, index=fechas, name=ticker)

precios = cargar_datos()
R["data"] = {
    "ticker": "AAPL (serie sintética calibrada)",
    "n_obs": int(len(precios)),
    "fecha_ini": str(precios.index[0].date()),
    "fecha_fin": str(precios.index[-1].date()),
    "S_ini": float(precios.iloc[0]),
    "S_fin": float(precios.iloc[-1]),
}

# ===========================================================================
# LABORATORIO 1: Estimación de un MBG con datos de una acción
# ===========================================================================
log_ret = np.log(precios / precios.shift(1)).dropna()
m_hat = float(log_ret.mean())            # media diaria de log-retornos
s_hat = float(log_ret.std(ddof=1))       # desv. estándar diaria
# Anualización (fórmulas del documento, sec. 15.4.1)
sigma_hat = float(np.sqrt(N_DIAS_ANIO) * s_hat)
mu_hat = float(N_DIAS_ANIO * m_hat + 0.5 * N_DIAS_ANIO * s_hat ** 2)

R["lab1"] = {"m_diaria": m_hat, "s_diaria": s_hat,
             "mu_anual": mu_hat, "sigma_anual": sigma_hat}

# Simulación de trayectorias del MBG calibrado a partir del último precio
S0 = float(precios.iloc[-1])
dt = 1.0 / N_DIAS_ANIO
H_horizonte = 252                      # un año hacia adelante
n_sim = 200
rng = np.random.default_rng(7)
sim = np.zeros((n_sim, H_horizonte + 1))
sim[:, 0] = S0
for k in range(1, H_horizonte + 1):
    Z = rng.standard_normal(n_sim)
    sim[:, k] = sim[:, k - 1] * np.exp((mu_hat - 0.5 * sigma_hat ** 2) * dt
                                       + sigma_hat * np.sqrt(dt) * Z)

# Figura 1a: serie histórica
fig, ax = plt.subplots(figsize=(8.4, 3.6))
ax.plot(precios.index, precios.values, color=AZUL, lw=1.1)
ax.set_title("Serie histórica de precios ajustados (3 años)")
ax.set_xlabel("Fecha"); ax.set_ylabel("Precio $S_t$")
fig.savefig(f"{FIG}/lab1_serie.pdf"); plt.close(fig)

# Figura 1b: histograma de log-retornos vs normal
fig, ax = plt.subplots(figsize=(8.4, 3.6))
ax.hist(log_ret.values, bins=60, density=True, color=AZUL, alpha=0.55,
        edgecolor="white", linewidth=0.3, label="log-retornos diarios")
xs = np.linspace(log_ret.min(), log_ret.max(), 400)
ax.plot(xs, norm.pdf(xs, m_hat, s_hat), color=NARANJA, lw=2,
        label=r"$\mathcal{N}(\hat m,\hat s^2)$ ajustada")
ax.set_title("Distribución empírica de log-retornos diarios")
ax.set_xlabel("log-retorno diario"); ax.set_ylabel("densidad")
ax.legend()
fig.savefig(f"{FIG}/lab1_hist.pdf"); plt.close(fig)

# Figura 1c: trayectorias simuladas con bandas
horizonte_idx = np.arange(H_horizonte + 1)
q05 = np.quantile(sim, 0.05, axis=0)
q50 = np.quantile(sim, 0.50, axis=0)
q95 = np.quantile(sim, 0.95, axis=0)
banda_teo = S0 * np.exp(mu_hat * horizonte_idx * dt)
fig, ax = plt.subplots(figsize=(8.4, 3.8))
for k in range(40):
    ax.plot(horizonte_idx, sim[k], color=AZUL, alpha=0.10, lw=0.7)
ax.fill_between(horizonte_idx, q05, q95, color=NARANJA, alpha=0.18,
                label="banda Monte Carlo 5%--95%")
ax.plot(horizonte_idx, q50, color=NARANJA, lw=2, label="mediana simulada")
ax.plot(horizonte_idx, banda_teo, color=VINO, lw=1.6, ls="--",
        label=r"crecimiento esperado $S_0 e^{\hat\mu t}$")
ax.set_title("Trayectorias simuladas del MBG a un año")
ax.set_xlabel("días bursátiles hacia adelante"); ax.set_ylabel("precio simulado")
ax.legend(loc="upper left")
fig.savefig(f"{FIG}/lab1_sim.pdf"); plt.close(fig)

# ===========================================================================
# LABORATORIO 2: Volatilidad realizada y ventanas móviles
# ===========================================================================
ventanas = [21, 63, 126]
colores_v = {21: NARANJA, 63: AZUL, 126: VERDE}
vol_movil = {}
for w in ventanas:
    vol_movil[w] = log_ret.rolling(w).std(ddof=1) * np.sqrt(N_DIAS_ANIO)

# Volatilidad realizada acumulada en cada ventana (resumen)
R["lab2"] = {
    "vol_media_w21": float(vol_movil[21].mean()),
    "vol_media_w63": float(vol_movil[63].mean()),
    "vol_media_w126": float(vol_movil[126].mean()),
    "vol_max_w21": float(vol_movil[21].max()),
    "vol_min_w21": float(vol_movil[21].min()),
    "fecha_max_w21": str(vol_movil[21].idxmax().date()),
}

fig, ax = plt.subplots(figsize=(8.4, 3.9))
for w in ventanas:
    ax.plot(vol_movil[w].index, vol_movil[w].values * 100,
            color=colores_v[w], lw=1.3, label=f"ventana {w} días")
ax.axhline(sigma_hat * 100, color=GRIS, ls=":", lw=1.2,
           label=fr"$\hat\sigma$ global = {sigma_hat*100:.1f}%")
ax.set_title("Volatilidad realizada anualizada (ventanas móviles)")
ax.set_xlabel("Fecha"); ax.set_ylabel("volatilidad anualizada (%)")
ax.legend(ncol=2)
fig.savefig(f"{FIG}/lab2_vol.pdf"); plt.close(fig)

# ===========================================================================
# Parámetros comunes para valuación de opciones (calibrados con los labs)
# ===========================================================================
S0_op = 100.0          # precio inicial normalizado
K      = 100.0         # strike at-the-money
r      = 0.04          # tasa libre de riesgo anual
T      = 1.0           # vencimiento (años)
sigma  = round(sigma_hat, 4)   # volatilidad calibrada en Lab 1/2
R["opc_param"] = {"S0": S0_op, "K": K, "r": r, "T": T, "sigma": sigma}

# ---------------------------------------------------------------------------
# Black-Scholes cerrado (call y put)
# ---------------------------------------------------------------------------
def black_scholes(S0, K, r, sigma, T, tipo="call"):
    d1 = (np.log(S0 / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if tipo == "call":
        return S0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S0 * norm.cdf(-d1)

# ===========================================================================
# LABORATORIO 3: Valuación Monte Carlo de una opción europea
# ===========================================================================
def mc_europea(S0, K, r, sigma, T, n_paths, tipo="call", seed=11):
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal(n_paths)
    ST = S0 * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
    if tipo == "call":
        payoff = np.maximum(ST - K, 0.0)
    else:
        payoff = np.maximum(K - ST, 0.0)
    desc = np.exp(-r * T) * payoff
    precio = float(desc.mean())
    se = float(desc.std(ddof=1) / np.sqrt(n_paths))
    return precio, se, ST

n_paths_eu = 200_000
call_mc, call_se, ST_muestra = mc_europea(S0_op, K, r, sigma, T, n_paths_eu, "call")
put_mc,  put_se,  _          = mc_europea(S0_op, K, r, sigma, T, n_paths_eu, "put", seed=12)
call_bs = float(black_scholes(S0_op, K, r, sigma, T, "call"))
put_bs  = float(black_scholes(S0_op, K, r, sigma, T, "put"))

R["lab3"] = {
    "n_paths": n_paths_eu,
    "call_mc": call_mc, "call_se": call_se, "call_bs": call_bs,
    "call_ic_low": call_mc - 1.96 * call_se, "call_ic_high": call_mc + 1.96 * call_se,
    "put_mc": put_mc, "put_se": put_se, "put_bs": put_bs,
    "put_ic_low": put_mc - 1.96 * put_se, "put_ic_high": put_mc + 1.96 * put_se,
    "paridad_lhs": call_mc - put_mc,
    "paridad_rhs": S0_op - K * np.exp(-r * T),
}

# Convergencia del estimador Monte Carlo (call)
ns = np.array([500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000])
rng = np.random.default_rng(99)
Zbig = rng.standard_normal(int(ns.max()))
STbig = S0_op * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Zbig)
poff = np.exp(-r * T) * np.maximum(STbig - K, 0.0)
est = np.array([poff[:n].mean() for n in ns])
err = np.array([poff[:n].std(ddof=1) / np.sqrt(n) for n in ns])

fig, ax = plt.subplots(figsize=(8.4, 3.8))
ax.errorbar(ns, est, yerr=1.96 * err, fmt="o-", color=AZUL, ecolor=NARANJA,
            elinewidth=1.2, capsize=3, lw=1.2, ms=4, label="estimador MC $\\pm$ IC 95%")
ax.axhline(call_bs, color=VINO, ls="--", lw=1.6,
           label=f"Black--Scholes = {call_bs:.4f}")
ax.set_xscale("log")
ax.set_title("Convergencia del estimador Monte Carlo (call europea)")
ax.set_xlabel("número de trayectorias $M$ (escala log)")
ax.set_ylabel("precio estimado de la call")
ax.legend()
fig.savefig(f"{FIG}/lab3_conv.pdf"); plt.close(fig)

# Figura payoffs terminales
fig, ax = plt.subplots(figsize=(8.4, 3.6))
ax.hist(ST_muestra, bins=80, density=True, color=AZUL, alpha=0.45,
        edgecolor="white", linewidth=0.2, label="densidad simulada de $S_T$")
ax.axvline(K, color=VINO, ls="--", lw=1.4, label=f"strike $K={K:.0f}$")
ax.set_title("Distribución terminal simulada de $S_T$ bajo $\\mathbb{Q}$")
ax.set_xlabel("precio terminal $S_T$"); ax.set_ylabel("densidad")
ax.legend()
fig.savefig(f"{FIG}/lab3_ST.pdf"); plt.close(fig)

# ===========================================================================
# LABORATORIO 4: Opción americana con Longstaff-Schwartz
# ===========================================================================
def simular_gbm(S0, r, sigma, T, n_steps, n_paths, seed=21):
    rng = np.random.default_rng(seed)
    dt = T / n_steps
    S = np.empty((n_paths, n_steps + 1))
    S[:, 0] = S0
    incr = np.exp((r - 0.5 * sigma ** 2) * dt
                  + sigma * np.sqrt(dt) * rng.standard_normal((n_paths, n_steps)))
    S[:, 1:] = S0 * np.cumprod(incr, axis=1)
    return S

def lsm_put_americana(S0, K, r, sigma, T, n_steps, n_paths, seed=21):
    dt = T / n_steps
    df = np.exp(-r * dt)
    S = simular_gbm(S0, r, sigma, T, n_steps, n_paths, seed)
    payoff = np.maximum(K - S, 0.0)
    V = payoff[:, -1].copy()                 # valor en el vencimiento
    for t in range(n_steps - 1, 0, -1):
        V *= df                              # valor de continuación realizado (a t)
        itm = payoff[:, t] > 0
        if itm.sum() > 0:
            X = S[itm, t]
            A = np.column_stack([np.ones_like(X), X, X ** 2])   # base 1, S, S^2
            beta, *_ = np.linalg.lstsq(A, V[itm], rcond=None)
            cont = A @ beta                  # valor de continuación estimado
            ejercer = payoff[itm, t] > cont
            Vi = V[itm].copy()
            Vi[ejercer] = payoff[itm, t][ejercer]
            V[itm] = Vi
    precio = float((V * df).mean())
    se = float((V * df).std(ddof=1) / np.sqrt(n_paths))
    return precio, se

n_steps_am = 100
n_paths_am = 100_000
put_am, put_am_se = lsm_put_americana(S0_op, K, r, sigma, T, n_steps_am, n_paths_am)
put_eu_bs = float(black_scholes(S0_op, K, r, sigma, T, "put"))
prima_temprano = put_am - put_eu_bs

R["lab4"] = {
    "n_steps": n_steps_am, "n_paths": n_paths_am,
    "put_americana": put_am, "put_am_se": put_am_se,
    "put_europea": put_eu_bs, "prima_ejercicio": prima_temprano,
    "prima_pct": 100 * prima_temprano / put_eu_bs,
}

# Frontera de ejercicio: cruce de la parábola de continuación con el valor de
# ejercicio (K - S).  Para cada t resolvemos  K - S = b0 + b1 S + b2 S^2.
def frontera_lsm(S0, K, r, sigma, T, n_steps, n_paths, seed=33):
    dt = T / n_steps
    df = np.exp(-r * dt)
    S = simular_gbm(S0, r, sigma, T, n_steps, n_paths, seed)
    payoff = np.maximum(K - S, 0.0)
    V = payoff[:, -1].copy()
    frontera = np.full(n_steps + 1, np.nan)
    frontera[-1] = K                       # en el vencimiento se ejerce todo ITM
    for t in range(n_steps - 1, 0, -1):
        V *= df
        itm = payoff[:, t] > 0
        if itm.sum() > 100:
            X = S[itm, t]
            A = np.column_stack([np.ones_like(X), X, X ** 2])
            beta, *_ = np.linalg.lstsq(A, V[itm], rcond=None)
            b0, b1, b2 = beta
            # b2 S^2 + (b1+1) S + (b0 - K) = 0
            a, b, c = b2, b1 + 1.0, b0 - K
            if abs(a) > 1e-9:
                disc = b * b - 4 * a * c
                if disc >= 0:
                    raices = [(-b + np.sqrt(disc)) / (2 * a),
                              (-b - np.sqrt(disc)) / (2 * a)]
                    val = [rt for rt in raices if 0.3 * K < rt < K]
                    if val:
                        frontera[t] = max(val)
            ejercer = payoff[itm, t] > (A @ beta)
            Vi = V[itm].copy()
            Vi[ejercer] = payoff[itm, t][ejercer]
            V[itm] = Vi
    return frontera

front = frontera_lsm(S0_op, K, r, sigma, T, n_steps_am, 120000)
tgrid = np.linspace(0, T, n_steps_am + 1)
fr = pd.Series(front)
fr = fr.interpolate(limit_direction="both")              # rellena huecos
front_s = fr.rolling(9, min_periods=1, center=True).mean().values
R["lab4"]["frontera_t0"] = float(front_s[1])
R["lab4"]["frontera_tT"] = float(K)

fig, ax = plt.subplots(figsize=(8.4, 3.9))
ax.plot(tgrid[1:], front_s[1:], color=VINO, lw=2,
        label=r"frontera de ejercicio $S^*(t)$")
ax.axhline(K, color=GRIS, ls="--", lw=1.2, label=f"strike $K={K:.0f}$")
ax.fill_between(tgrid[1:], 60, front_s[1:], color=VINO, alpha=0.10)
ax.text(0.45, 70, "ejercer la put", color=VINO, fontsize=10)
ax.text(0.50, 94, "mantener viva la opción", color=AZUL, fontsize=10)
ax.set_ylim(60, 102)
ax.set_title("Frontera libre estimada de una put americana (Longstaff--Schwartz)")
ax.set_xlabel("tiempo $t$ (años)"); ax.set_ylabel("precio del subyacente $S_t$")
ax.legend(loc="lower right")
fig.savefig(f"{FIG}/lab4_frontera.pdf"); plt.close(fig)

# ===========================================================================
# LABORATORIO 5 y PROYECTO 6: Opción parisina y reloj de barrera
# ===========================================================================
# Down-and-out parisina sobre una CALL: la opción se desactiva si el precio
# permanece por DEBAJO de la barrera H durante al menos D días CONSECUTIVOS.
def precio_parisina_DO(S0, K, r, sigma, T, H, D_dias, n_paths, seed=51,
                       paths=None):
    """Devuelve (precio, se, frac_desactivada). Reloj CONSECUTIVO bajo barrera.
    Si se pasan 'paths' (matriz S) se usan trayectorias comunes (CRN)."""
    n_steps = int(round(T * N_DIAS_ANIO))
    dt = T / n_steps
    if paths is None:
        S = simular_gbm(S0, r, sigma, T, n_steps, n_paths, seed)
    else:
        S = paths
        n_paths = S.shape[0]
    bajo = S[:, 1:] < H                       # indicador S_t < H (sin el inicio)
    # contador de días consecutivos bajo la barrera, por trayectoria
    contador = np.zeros(n_paths, dtype=int)
    desactivada = np.zeros(n_paths, dtype=bool)
    if D_dias <= 0:
        # caso límite: knock-out estándar (un solo toque/cruce desactiva)
        desactivada = bajo.any(axis=1)
    else:
        for j in range(bajo.shape[1]):
            contador = np.where(bajo[:, j], contador + 1, 0)
            desactivada |= (contador >= D_dias)
    ST = S[:, -1]
    payoff = np.where(~desactivada, np.maximum(ST - K, 0.0), 0.0)
    desc = np.exp(-r * T) * payoff
    return float(desc.mean()), float(desc.std(ddof=1) / np.sqrt(n_paths)), \
           float(desactivada.mean())

# ---- Lab 5: sensibilidad respecto del reloj D (barrera H fija) ----
H_lab5 = 90.0
Ds = [1, 5, 10, 20, 40, 60]
n_paths_par = 100_000
# trayectorias comunes para que la comparación sea limpia (mismo ruido)
n_steps_par = int(round(T * N_DIAS_ANIO))
S_par = simular_gbm(S0_op, r, sigma, T, n_steps_par, n_paths_par, seed=51)

tabla_D = []
for D in Ds:
    p, se, frac = precio_parisina_DO(S0_op, K, r, sigma, T, H_lab5, D,
                                     n_paths_par, paths=S_par)
    tabla_D.append({"D": D, "precio": p, "se": se, "frac_desact": frac})

# referencias: knock-out estándar (D->0) y vanilla (sin barrera, = MC call)
p_ko, se_ko, frac_ko = precio_parisina_DO(S0_op, K, r, sigma, T, H_lab5, 0,
                                          n_paths_par, paths=S_par)
ZT = S_par[:, -1]
p_van = float(np.exp(-r * T) * np.maximum(ZT - K, 0.0).mean())

R["lab5"] = {
    "H": H_lab5, "n_paths": n_paths_par, "n_steps": n_steps_par,
    "tabla_D": tabla_D,
    "ko_estandar": {"precio": p_ko, "frac_desact": frac_ko},
    "vanilla": p_van,
}

fig, ax = plt.subplots(figsize=(8.4, 3.9))
Dv = [d["D"] for d in tabla_D]
Pv = [d["precio"] for d in tabla_D]
SEv = [1.96 * d["se"] for d in tabla_D]
ax.errorbar(Dv, Pv, yerr=SEv, fmt="o-", color=AZUL, ecolor=NARANJA,
            capsize=3, lw=1.4, ms=5, label="parisina down-and-out")
ax.axhline(p_van, color=VERDE, ls="--", lw=1.5,
           label=f"call vanilla = {p_van:.3f}")
ax.axhline(p_ko, color=VINO, ls=":", lw=1.6,
           label=f"knock-out estándar = {p_ko:.3f}")
ax.set_title("Lab 5: precio parisino vs. reloj de permanencia $D$ ($H=90$)")
ax.set_xlabel("retardo parisino $D$ (días consecutivos)")
ax.set_ylabel("precio de la opción")
ax.legend(loc="lower right")
fig.savefig(f"{FIG}/lab5_D.pdf"); plt.close(fig)

# trayectoria ilustrativa con reloj parisino
rng = np.random.default_rng(2024)
n_st = n_steps_par
una = np.empty(n_st + 1); una[0] = S0_op
dt = T / n_st
for k in range(1, n_st + 1):
    una[k] = una[k-1] * np.exp((r - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*rng.standard_normal())
bajo = una[1:] < H_lab5
contador_t = np.zeros(n_st)
c = 0
for j in range(n_st):
    c = c + 1 if bajo[j] else 0
    contador_t[j] = c
tt = np.linspace(0, T, n_st + 1)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(8.4, 4.6), sharex=True,
                             gridspec_kw={"height_ratios": [2, 1]})
a1.plot(tt, una, color=AZUL, lw=1.2)
a1.axhline(H_lab5, color=VINO, ls="--", lw=1.3, label=f"barrera $H={H_lab5:.0f}$")
a1.fill_between(tt[1:], una[1:], H_lab5, where=bajo, color=VINO, alpha=0.15)
a1.set_ylabel("precio $S_t$"); a1.legend(loc="upper right")
a1.set_title("Reloj parisino consecutivo bajo la barrera")
a2.plot(tt[1:], contador_t, color=MORADO, lw=1.4, label="reloj consecutivo (días)")
for Dh in [10, 20, 40]:
    a2.axhline(Dh, color=GRIS, ls=":", lw=0.9)
a2.set_ylabel("reloj (días)"); a2.set_xlabel("tiempo $t$ (años)")
a2.legend(loc="upper left")
fig.savefig(f"{FIG}/lab5_reloj.pdf"); plt.close(fig)

# ===========================================================================
# PROYECTO 6: Opción parisina por Monte Carlo (sensibilidad H y D)
# ===========================================================================
Hs = [85.0, 90.0, 95.0]
Ds_p6 = [0, 5, 10, 20, 40, 80]
# malla de trayectorias comunes (CRN) para suavidad
n_paths_p6 = 80_000
S_p6 = simular_gbm(S0_op, r, sigma, T, n_steps_par, n_paths_p6, seed=606)
p_van6 = float(np.exp(-r * T) * np.maximum(S_p6[:, -1] - K, 0.0).mean())

malla = {}        # malla[H][D] = precio
for H in Hs:
    malla[H] = {}
    for D in Ds_p6:
        p, _, _ = precio_parisina_DO(S0_op, K, r, sigma, T, H, D,
                                     n_paths_p6, paths=S_p6)
        malla[H][D] = p

R["proj6"] = {
    "Hs": Hs, "Ds": Ds_p6, "n_paths": n_paths_p6,
    "vanilla": p_van6,
    "malla": {str(H): {str(D): malla[H][D] for D in Ds_p6} for H in Hs},
}

# Figura: precio vs D para varias barreras H
fig, ax = plt.subplots(figsize=(8.4, 4.0))
cmap = {85.0: VINO, 90.0: AZUL, 95.0: VERDE}
for H in Hs:
    ys = [malla[H][D] for D in Ds_p6]
    ax.plot(Ds_p6, ys, "o-", color=cmap[H], lw=1.5, ms=5, label=f"$H={H:.0f}$")
ax.axhline(p_van6, color=GRIS, ls="--", lw=1.4, label=f"vanilla = {p_van6:.3f}")
ax.set_title("Proyecto 6: precio de la parisina down-and-out vs. $D$ y $H$")
ax.set_xlabel("retardo parisino $D$ (días consecutivos)")
ax.set_ylabel("precio de la opción")
ax.legend(title="barrera", loc="lower right")
fig.savefig(f"{FIG}/proj6_curvas.pdf"); plt.close(fig)

# Heatmap fino (H x D)
Hgrid = np.array([82, 85, 88, 90, 92, 95, 98])
Dgrid = np.array([0, 2, 5, 10, 15, 20, 30, 40, 60, 80])
Mh = np.zeros((len(Hgrid), len(Dgrid)))
for i, H in enumerate(Hgrid):
    for j, D in enumerate(Dgrid):
        p, _, _ = precio_parisina_DO(S0_op, K, r, sigma, T, float(H), int(D),
                                     n_paths_p6, paths=S_p6)
        Mh[i, j] = p
fig, ax = plt.subplots(figsize=(8.4, 4.2))
im = ax.imshow(Mh, aspect="auto", origin="lower", cmap="viridis",
               extent=[Dgrid.min()-1, Dgrid.max()+1, 0, len(Hgrid)])
ax.set_yticks(np.arange(len(Hgrid)) + 0.5); ax.set_yticklabels(Hgrid)
ax.set_xlabel("retardo parisino $D$ (días)"); ax.set_ylabel("barrera $H$")
ax.set_title("Proyecto 6: superficie de precio parisino $V(H,D)$")
cb = fig.colorbar(im, ax=ax); cb.set_label("precio de la opción")
ax.grid(False)
fig.savefig(f"{FIG}/proj6_heatmap.pdf"); plt.close(fig)
R["proj6"]["heatmap_min"] = float(Mh.min())
R["proj6"]["heatmap_max"] = float(Mh.max())

# Trayectorias Monte Carlo representativas (una muestra), marcando knock-outs
sel = S_p6[:14]
desact_sel = np.zeros(14, dtype=bool)
bajo_sel = sel[:, 1:] < 90.0
cont = np.zeros(14)
for j in range(bajo_sel.shape[1]):
    cont = np.where(bajo_sel[:, j], cont + 1, 0)
    desact_sel |= (cont >= 20)
tt = np.linspace(0, T, n_steps_par + 1)
fig, ax = plt.subplots(figsize=(8.4, 4.0))
for k in range(14):
    col = VINO if desact_sel[k] else AZUL
    al = 0.9 if desact_sel[k] else 0.5
    ax.plot(tt, sel[k], color=col, lw=0.9, alpha=al)
ax.axhline(90.0, color=GRIS, ls="--", lw=1.3, label="barrera $H=90$")
ax.axhline(K, color="black", ls=":", lw=1.0, label="strike $K=100$")
ax.plot([], [], color=VINO, lw=1.2, label="desactivada (reloj $\\geq D$)")
ax.plot([], [], color=AZUL, lw=1.2, label="sobrevive")
ax.set_title("Proyecto 6: trayectorias Monte Carlo y reglas parisinas ($D=20$)")
ax.set_xlabel("tiempo $t$ (años)"); ax.set_ylabel("precio simulado $S_t$")
ax.legend(loc="upper left", ncol=2)
fig.savefig(f"{FIG}/proj6_paths.pdf"); plt.close(fig)

# ===========================================================================
# Volcado de resultados
# ===========================================================================
with open("/home/claude/proyecto/code/results.json", "w") as f:
    json.dump(R, f, indent=2, ensure_ascii=False)

print("=== RESULTADOS CLAVE ===")
print(f"Lab1  mu={mu_hat:.4f}  sigma={sigma_hat:.4f}")
print(f"Lab2  vol media w21={R['lab2']['vol_media_w21']:.4f}  max w21={R['lab2']['vol_max_w21']:.4f}")
print(f"Lab3  call MC={call_mc:.4f} (SE {call_se:.4f})  BS={call_bs:.4f}")
print(f"      put  MC={put_mc:.4f} (SE {put_se:.4f})  BS={put_bs:.4f}")
print(f"Lab4  put amer={put_am:.4f}  put eur={put_eu_bs:.4f}  prima={prima_temprano:.4f}")
print(f"Lab5  vanilla={p_van:.4f}  KO std={p_ko:.4f}")
for d in tabla_D:
    print(f"      D={d['D']:>2}  precio={d['precio']:.4f}  desact={d['frac_desact']:.3f}")
print(f"Proj6 vanilla={p_van6:.4f}  rango heatmap=[{Mh.min():.3f},{Mh.max():.3f}]")
print("OK figuras + results.json")
