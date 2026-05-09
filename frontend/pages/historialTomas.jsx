// src/pages/HistorialTomas.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

// NOTA: el HTML original hacía fetch() directo. Aquí usamos api.obtenerHistorial()
// que ya existe en tu api.js, centralizando la llamada al backend como corresponde
// al patrón Fachada que tiene el proyecto.

const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

  .ht-root {
    margin: 0;
    min-height: 100vh;
    background: #0F1B2D;
    font-family: 'DM Sans', sans-serif;
    color: #E2EAF4;
    padding: 2rem 1rem;
    background-image:
      radial-gradient(ellipse 60% 50% at 80% 10%, rgba(45,212,191,.12) 0%, transparent 70%),
      radial-gradient(ellipse 40% 40% at 10% 80%, rgba(45,212,191,.07) 0%, transparent 60%);
  }
  .ht-encabezado {
    max-width: 1000px; margin: 0 auto 2rem;
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 1rem;
  }
  .ht-marca { display: flex; align-items: center; gap: .6rem; }
  .ht-marca-icono {
    width: 36px; height: 36px; background: #2DD4BF;
    border-radius: 10px; display: flex; align-items: center; justify-content: center;
  }
  .ht-marca-icono svg { width: 20px; height: 20px; color: #0F1B2D; }
  .ht-marca-nombre { font-family: 'DM Serif Display', serif; font-size: 1.35rem; }

  .ht-btn-volver {
    background: transparent; color: #7A95B0;
    border: 1.5px solid #243447; border-radius: 10px;
    padding: .5rem 1.1rem; font-size: .85rem; font-family: 'DM Sans', sans-serif;
    cursor: pointer; transition: all .2s; text-decoration: none;
    display: inline-flex; align-items: center; gap: .4rem;
  }
  .ht-btn-volver:hover { border-color: #2DD4BF; color: #2DD4BF; }

  .ht-tarjeta {
    background: #162030; border: 1px solid #243447;
    border-radius: 20px; max-width: 1000px; margin: 0 auto;
    padding: 2rem; box-shadow: 0 32px 80px rgba(0,0,0,.5);
    animation: ht-subir .45s ease both;
  }
  @keyframes ht-subir {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .ht-titulo { font-family: 'DM Serif Display', serif; font-size: 1.5rem; margin-bottom: 1.5rem; }

  /* Filtro de búsqueda */
  .ht-filtro { display: flex; align-items: center; gap: .75rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
  .ht-input {
    background: #1E2D3D; border: 1.5px solid #243447;
    color: #E2EAF4; border-radius: 10px;
    padding: .55rem .9rem; font-size: .88rem;
    font-family: 'DM Sans', sans-serif;
    transition: border-color .2s; width: 180px; outline: none;
  }
  .ht-input:focus { border-color: #2DD4BF; }
  .ht-input::placeholder { color: #4A6278; }
  .ht-input::-webkit-inner-spin-button,
  .ht-input::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }

  .ht-btn-consultar {
    background: #2DD4BF; color: #0F1B2D;
    border: none; border-radius: 10px;
    padding: .55rem 1.2rem; font-size: .88rem; font-weight: 600;
    font-family: 'DM Sans', sans-serif; cursor: pointer; transition: background .2s;
  }
  .ht-btn-consultar:hover { background: #0F9D8A; }
  .ht-btn-consultar:disabled { opacity: .6; cursor: not-allowed; }

  .ht-alerta-error {
    background: rgba(244,114,106,.1); border: 1px solid #F4726A;
    color: #F4726A; border-radius: 12px;
    padding: .85rem 1rem; margin-bottom: 1.25rem; font-size: .88rem;
  }

  /* Tabla */
  .ht-tabla-wrap { overflow-x: auto; }
  .ht-tabla { width: 100%; border-collapse: collapse; }
  .ht-tabla thead th {
    background: #1E2D3D; color: #2DD4BF;
    border-bottom: 1px solid #243447;
    font-size: .76rem; text-transform: uppercase; letter-spacing: .06em;
    font-weight: 500; padding: .8rem 1rem; text-align: left; white-space: nowrap;
  }
  .ht-tabla tbody tr { border-bottom: 1px solid #243447; transition: background .15s; }
  .ht-tabla tbody tr:last-child { border-bottom: none; }
  .ht-tabla tbody tr:hover { background: rgba(45,212,191,.04); }
  .ht-tabla tbody td { padding: .85rem 1rem; font-size: .88rem; vertical-align: middle; }
  .ht-vacio { text-align: center; color: #7A95B0; padding: 2.5rem !important; }

  /* Badges de estado */
  .ht-badge {
    display: inline-flex; align-items: center;
    border-radius: 20px; padding: .22rem .65rem;
    font-size: .75rem; font-weight: 600;
  }
  .ht-tomado   { background: rgba(74,222,128,.12);  color: #4ADE80; border: 1px solid rgba(74,222,128,.3); }
  .ht-pendiente{ background: rgba(251,191,36,.12);  color: #FBBF24; border: 1px solid rgba(251,191,36,.3); }
  .ht-atrasado { background: rgba(244,114,106,.12); color: #F4726A; border: 1px solid rgba(244,114,106,.3); }

  /* Spinner */
  .ht-spinner {
    display: inline-block; width: 15px; height: 15px;
    border: 2px solid #243447; border-top-color: #2DD4BF;
    border-radius: 50%; animation: ht-spin .7s linear infinite;
    vertical-align: middle; margin-right: .35rem;
  }
  @keyframes ht-spin { to { transform: rotate(360deg); } }

  @media (max-width: 600px) { .ht-tarjeta { padding: 1.25rem; } }
`;

// ── Badge según estado ──────────────────────────────────────────────────────
function BadgeEstado({ estado }) {
  // El HTML original usaba clases CSS ('pendiente', 'tomado', 'atrasado')
  // Aquí las mapeamos a clases con prefijo para no colisionar
  const mapa = {
    tomado:   'ht-badge ht-tomado',
    a_tiempo: 'ht-badge ht-tomado',
    atrasado: 'ht-badge ht-atrasado',
    tarde:    'ht-badge ht-atrasado',
    omitida:  'ht-badge ht-atrasado',
    pendiente:'ht-badge ht-pendiente',
  };
  const cls  = mapa[estado] || 'ht-badge ht-pendiente';
  const texto = estado === 'a_tiempo' ? 'tomado' : (estado || 'pendiente');
  return <span className={cls}>{texto}</span>;
}

export default function HistorialTomas() {
  const navigate = useNavigate();

  const [pacienteId, setPacienteId] = useState('');
  const [historial, setHistorial]   = useState(null);  // null = no consultado aún
  const [error, setError]           = useState('');
  const [cargando, setCargando]     = useState(false);

  // Equivale a la función cargarHistorial() del HTML original
  // Cambio principal: usa api.obtenerHistorial() en vez de fetch() directo
  async function cargarHistorial() {
    if (!pacienteId.trim()) {
      setError('Debes ingresar un ID de paciente.');
      return;
    }
    setError('');
    setCargando(true);
    setHistorial(null);
    try {
      const res = await api.obtenerHistorial(pacienteId);
      if (!res.ok) {
        setError('Error al consultar el historial.');
        return;
      }
      // El backend devuelve { historial: [...] }
      const lista = res.body?.historial ?? [];
      setHistorial(lista);
    } catch {
      setError('Error al consultar el historial.');
    } finally {
      setCargando(false);
    }
  }

  // Permite consultar presionando Enter en el input
  function handleKeyDown(e) {
    if (e.key === 'Enter') cargarHistorial();
  }

  return (
    <>
      <style>{CSS}</style>

      <div className="ht-root">

        {/* Encabezado con marca y botón volver */}
        <div className="ht-encabezado">
          <div className="ht-marca">
            <div className="ht-marca-icono">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 8v4m0 4h.01M3 12a9 9 0 1 0 18 0A9 9 0 0 0 3 12z"/>
              </svg>
            </div>
            <span className="ht-marca-nombre">MedTrack</span>
          </div>
          <button className="ht-btn-volver" onClick={() => navigate('/dashboard')}>
            ← Volver al dashboard
          </button>
        </div>

        <div className="ht-tarjeta">
          <h2 className="ht-titulo">Historial de tomas de los últimos 7 días</h2>

          {/* Filtro — antes era un <input> + <button onclick> en el HTML */}
          <div className="ht-filtro">
            <input
              className="ht-input"
              type="number"
              placeholder="ID del paciente"
              value={pacienteId}
              onChange={(e) => setPacienteId(e.target.value)}
              onKeyDown={handleKeyDown}
              min={1}
            />
            <button
              className="ht-btn-consultar"
              onClick={cargarHistorial}
              disabled={cargando}
            >
              {cargando ? 'Consultando…' : 'Consultar historial'}
            </button>
          </div>

          {/* Error */}
          {error && <div className="ht-alerta-error">{error}</div>}

          {/* Tabla */}
          <div className="ht-tabla-wrap">
            <table className="ht-tabla">
              <thead>
                <tr>
                  <th>Medicamento</th>
                  <th>Fecha</th>
                  <th>Hora programada</th>
                  <th>Hora tomada</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {/* Estado: esperando consulta */}
                {historial === null && !cargando && (
                  <tr><td className="ht-vacio" colSpan={5}>Ingresa un ID de paciente para consultar.</td></tr>
                )}

                {/* Estado: cargando */}
                {cargando && (
                  <tr>
                    <td className="ht-vacio" colSpan={5}>
                      <span className="ht-spinner" />
                      Consultando historial…
                    </td>
                  </tr>
                )}

                {/* Estado: sin resultados */}
                {historial !== null && !cargando && historial.length === 0 && (
                  <tr>
                    <td className="ht-vacio" colSpan={5}>
                      No hay historial para este paciente en los últimos 7 días.
                    </td>
                  </tr>
                )}

                {/* Filas — .map() reemplaza el forEach + innerHTML del HTML original */}
                {historial !== null && !cargando && historial.map((t, i) => (
                  <tr key={i}>
                    {/* El backend puede devolver 't.medicamento' o 't.medicamento_nombre' */}
                    <td style={{ fontWeight: 500 }}>{t.medicamento || t.medicamento_nombre || '—'}</td>
                    <td>{t.fecha || t.fecha_programada || '—'}</td>
                    <td>{t.hora_programada || '—'}</td>
                    <td>{t.hora_tomado || t.fecha_hora_toma?.slice(11, 16) || '—'}</td>
                    <td><BadgeEstado estado={t.estado} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

        </div>
      </div>
    </>
  );
}