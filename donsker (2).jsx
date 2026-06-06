import { useState, useEffect, useRef, useCallback } from "react";

const W = 900;
const H = 420;
const PAD = { top: 40, right: 30, bottom: 50, left: 60 };
const INNER_W = W - PAD.left - PAD.right;
const INNER_H = H - PAD.top - PAD.bottom;

function generateDonsker(n) {
  const steps = Array.from({ length: n }, () => (Math.random() < 0.5 ? -1 : 1));
  const S = new Float32Array(n);
  S[0] = steps[0];
  for (let i = 1; i < n; i++) S[i] = S[i - 1] + steps[i];
  const sqrtN = Math.sqrt(n);
  return S.map((s) => s / sqrtN);
}

function toPath(W_arr, progress, yMin, yMax) {
  const count = Math.floor(W_arr.length * progress);
  if (count < 2) return "";
  const scaleX = (i) => PAD.left + (i / (W_arr.length - 1)) * INNER_W;
  const scaleY = (v) => PAD.top + ((yMax - v) / (yMax - yMin)) * INNER_H;
  let d = `M ${scaleX(0)} ${scaleY(W_arr[0])}`;
  for (let i = 1; i < count; i++) {
    d += ` L ${scaleX(i)} ${scaleY(W_arr[i])}`;
  }
  return d;
}

function YAxis({ yMin, yMax, ticks = 6 }) {
  const vals = Array.from({ length: ticks }, (_, i) => yMin + (i / (ticks - 1)) * (yMax - yMin));
  return (
    <>
      {vals.map((v) => {
        const y = PAD.top + ((yMax - v) / (yMax - yMin)) * INNER_H;
        return (
          <g key={v}>
            <line x1={PAD.left - 5} y1={y} x2={PAD.left + INNER_W} y2={y} stroke="#1e3a2f" strokeWidth={0.5} />
            <text x={PAD.left - 10} y={y + 4} textAnchor="end" fill="#4a9970" fontSize={11} fontFamily="'Courier New', monospace">
              {v.toFixed(2)}
            </text>
          </g>
        );
      })}
    </>
  );
}

function XAxis() {
  const ticks = [0, 0.25, 0.5, 0.75, 1];
  return (
    <>
      {ticks.map((v) => {
        const x = PAD.left + v * INNER_W;
        return (
          <g key={v}>
            <line x1={x} y1={PAD.top} x2={x} y2={PAD.top + INNER_H + 5} stroke="#1e3a2f" strokeWidth={0.5} />
            <text x={x} y={PAD.top + INNER_H + 18} textAnchor="middle" fill="#4a9970" fontSize={11} fontFamily="'Courier New', monospace">
              {v.toFixed(2)}
            </text>
          </g>
        );
      })}
    </>
  );
}

export default function DonskerViz() {
  const [n, setN] = useState(500);
  const [W_arr, setW_arr] = useState(() => generateDonsker(500));
  const [progress, setProgress] = useState(0);
  const [running, setRunning] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [trails, setTrails] = useState([]);
  const rafRef = useRef(null);
  const startTimeRef = useRef(null);
  const pausedProgressRef = useRef(0);

  const yArr = W_arr;
  const yMin = Math.min(...yArr) - 0.3;
  const yMax = Math.max(...yArr) + 0.3;

  const animate = useCallback((ts) => {
    if (!startTimeRef.current) startTimeRef.current = ts - pausedProgressRef.current * (2000 / speed);
    const elapsed = ts - startTimeRef.current;
    const dur = 2000 / speed;
    const p = Math.min(elapsed / dur, 1);
    setProgress(p);
    if (p < 1) {
      rafRef.current = requestAnimationFrame(animate);
    } else {
      setRunning(false);
      pausedProgressRef.current = 1;
    }
  }, [speed]);

  const start = () => {
    if (progress === 1) {
      pausedProgressRef.current = 0;
      startTimeRef.current = null;
      setProgress(0);
    }
    setRunning(true);
  };

  const pause = () => {
    setRunning(false);
    pausedProgressRef.current = progress;
    cancelAnimationFrame(rafRef.current);
  };

  const reset = () => {
    setRunning(false);
    cancelAnimationFrame(rafRef.current);
    pausedProgressRef.current = 0;
    startTimeRef.current = null;
    setProgress(0);
  };

  const regenerate = () => {
    const newW = generateDonsker(n);
    if (progress === 1) {
      setTrails((t) => [...t.slice(-4), { data: W_arr, yMin, yMax }]);
    }
    reset();
    setW_arr(newW);
  };

  useEffect(() => {
    if (running) {
      startTimeRef.current = null;
      rafRef.current = requestAnimationFrame(animate);
    } else {
      cancelAnimationFrame(rafRef.current);
    }
    return () => cancelAnimationFrame(rafRef.current);
  }, [running, animate]);

  useEffect(() => {
    reset();
    setW_arr(generateDonsker(n));
    setTrails([]);
  }, [n]);

  const pathD = toPath(W_arr, progress, yMin, yMax);
  const endIdx = Math.floor(W_arr.length * progress) - 1;
  const endX = endIdx >= 0 ? PAD.left + (endIdx / (W_arr.length - 1)) * INNER_W : null;
  const endY = endIdx >= 0 ? PAD.top + ((yMax - W_arr[endIdx]) / (yMax - yMin)) * INNER_H : null;
  const currentVal = endIdx >= 0 ? W_arr[endIdx].toFixed(4) : "—";

  return (
    <div style={{
      minHeight: "100vh",
      background: "#020c07",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      fontFamily: "'Courier New', monospace",
      padding: "32px 16px",
      color: "#e0ffe0",
    }}>
      {/* Header */}
      <div style={{ marginBottom: 24, textAlign: "center" }}>
        <div style={{ fontSize: 11, letterSpacing: "0.25em", color: "#4a9970", marginBottom: 6, textTransform: "uppercase" }}>
          Convergencia estocástica
        </div>
        <h1 style={{
          fontSize: "clamp(22px, 4vw, 38px)",
          fontWeight: 400,
          letterSpacing: "0.05em",
          color: "#c8ffe0",
          margin: 0,
          fontFamily: "'Georgia', serif",
        }}>
          Teorema de Donsker
        </h1>
        <div style={{ fontSize: 12, color: "#3a7055", marginTop: 8 }}>
          W<sub>n</sub>(t) = S<sub>⌊nt⌋</sub> / √n → B(t) &nbsp;&nbsp; n → ∞
        </div>
      </div>

      {/* SVG Chart */}
      <div style={{
        background: "#050f08",
        border: "1px solid #0e2a1a",
        borderRadius: 4,
        position: "relative",
        width: "100%",
        maxWidth: W,
        boxShadow: "0 0 60px #00ff6611",
      }}>
        {/* Live stats */}
        <div style={{
          position: "absolute", top: 10, right: 14,
          display: "flex", gap: 18, fontSize: 10, letterSpacing: "0.1em", color: "#2a6045",
        }}>
          <span>n = {n}</span>
          <span style={{ color: progress > 0 ? "#5adf90" : "#2a6045" }}>W_n = {currentVal}</span>
          <span>{(progress * 100).toFixed(0)}%</span>
        </div>

        <svg width="100%" viewBox={`0 0 ${W} ${H}`} style={{ display: "block" }}>
          <defs>
            <linearGradient id="lineGrad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#00cc55" />
              <stop offset="100%" stopColor="#00ffaa" />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="2.5" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Axes */}
          <line x1={PAD.left} y1={PAD.top} x2={PAD.left} y2={PAD.top + INNER_H} stroke="#1e3a2f" strokeWidth={1} />
          <line x1={PAD.left} y1={PAD.top + INNER_H} x2={PAD.left + INNER_W} y2={PAD.top + INNER_H} stroke="#1e3a2f" strokeWidth={1} />

          <YAxis yMin={yMin} yMax={yMax} />
          <XAxis />

          {/* Zero line */}
          {yMin < 0 && yMax > 0 && (
            <line
              x1={PAD.left} y1={PAD.top + (yMax / (yMax - yMin)) * INNER_H}
              x2={PAD.left + INNER_W} y2={PAD.top + (yMax / (yMax - yMin)) * INNER_H}
              stroke="#1a4030" strokeWidth={1} strokeDasharray="4 4"
            />
          )}

          {/* Trail paths */}
          {trails.map((tr, i) => {
            const alpha = 0.08 + i * 0.05;
            const d2 = toPath(tr.data, 1, tr.yMin, tr.yMax);
            return <path key={i} d={d2} fill="none" stroke={`rgba(0,200,80,${alpha})`} strokeWidth={1} />;
          })}

          {/* Main path */}
          {pathD && (
            <>
              <path d={pathD} fill="none" stroke="url(#lineGrad)" strokeWidth={2} filter="url(#glow)" strokeLinecap="round" strokeLinejoin="round" />
              {/* Cursor dot */}
              {endX !== null && (
                <circle cx={endX} cy={endY} r={4} fill="#00ffaa" filter="url(#glow)" />
              )}
            </>
          )}

          {/* Axis labels */}
          <text x={PAD.left + INNER_W / 2} y={H - 4} textAnchor="middle" fill="#2a6045" fontSize={11} fontFamily="'Courier New', monospace">
            t ∈ [0, 1]
          </text>
          <text x={14} y={PAD.top + INNER_H / 2} textAnchor="middle" fill="#2a6045" fontSize={11} fontFamily="'Courier New', monospace"
            transform={`rotate(-90, 14, ${PAD.top + INNER_H / 2})`}>
            W_n(t)
          </text>
        </svg>
      </div>

      {/* Controls */}
      <div style={{
        marginTop: 20,
        display: "flex",
        flexWrap: "wrap",
        gap: 12,
        alignItems: "center",
        justifyContent: "center",
      }}>
        {/* Play/Pause/Reset */}
        {[
          { label: running ? "⏸ Pausar" : "▶ Animar", action: running ? pause : start },
          { label: "↺ Reset", action: reset },
          { label: "⟳ Nueva muestra", action: regenerate },
        ].map(({ label, action }) => (
          <button key={label} onClick={action} style={{
            background: "transparent",
            border: "1px solid #1e5035",
            color: "#5adf90",
            padding: "8px 18px",
            fontFamily: "'Courier New', monospace",
            fontSize: 12,
            letterSpacing: "0.05em",
            cursor: "pointer",
            borderRadius: 2,
            transition: "all 0.15s",
          }}
            onMouseEnter={e => { e.target.style.background = "#0a2018"; e.target.style.borderColor = "#3aaf65"; }}
            onMouseLeave={e => { e.target.style.background = "transparent"; e.target.style.borderColor = "#1e5035"; }}
          >
            {label}
          </button>
        ))}

        {/* n selector */}
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 11, color: "#2a6045" }}>n =</span>
          {[100, 500, 1000, 5000].map((v) => (
            <button key={v} onClick={() => setN(v)} style={{
              background: n === v ? "#0a2518" : "transparent",
              border: `1px solid ${n === v ? "#3aaf65" : "#1e5035"}`,
              color: n === v ? "#00ffaa" : "#3a7055",
              padding: "6px 12px",
              fontFamily: "'Courier New', monospace",
              fontSize: 11,
              cursor: "pointer",
              borderRadius: 2,
            }}>
              {v}
            </button>
          ))}
        </div>

        {/* Speed */}
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 11, color: "#2a6045" }}>vel</span>
          {[0.5, 1, 2, 4].map((v) => (
            <button key={v} onClick={() => setSpeed(v)} style={{
              background: speed === v ? "#0a2518" : "transparent",
              border: `1px solid ${speed === v ? "#3aaf65" : "#1e5035"}`,
              color: speed === v ? "#00ffaa" : "#3a7055",
              padding: "6px 10px",
              fontFamily: "'Courier New', monospace",
              fontSize: 11,
              cursor: "pointer",
              borderRadius: 2,
            }}>
              {v}×
            </button>
          ))}
        </div>
      </div>

      {/* Footer note */}
      <div style={{ marginTop: 24, fontSize: 10, color: "#1a4030", letterSpacing: "0.12em", textAlign: "center", maxWidth: 600 }}>
        Caminata aleatoria S_k = ξ₁ + … + ξₖ con ξᵢ ∈ {"{-1, +1}"} escalada por 1/√n converge en distribución al movimiento browniano estándar (Donsker, 1951)
      </div>
    </div>
  );
}
