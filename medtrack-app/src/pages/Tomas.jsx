import { useState, useEffect } from "react";
import api from "../api";

const css = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
  :root {
    --menta: #2DD4BF;
    --menta-oscuro: #0F9D8A;
    --fondo: #0F1B2D;
    --campo: #1E2D3D;
    --tarjeta: #162030;
    --borde: #243447;
    --texto: #E2EAF4;
    --suave: #7A95B0;
    --error: #F4726A;
    --exito: #4ADE80;
    --alerta: #FBBF24;
  }
  *, *::before, *::after { box-sizing: border-box; }
  .tm-body {
    margin: 0; min-height: 100vh; background: var(--fondo);
    font-family: 'DM Sans', sans-serif; color: var(--texto); padding: 2rem 1rem;
    background-image:
      radial-gradient(ellipse 60% 50% at 80% 10%, rgba(45,212,191,.12) 0%, transparent 70%),
      radial-gradient(ellipse 40% 40% at 10% 80%, rgba(45,212,191,.07) 0%, transparent 60%);
  }
  .tm-encabezado {
    max-width: 1000px; margin: 0 auto 2rem;
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 1rem;
  }
  .tm-marca { display: flex; align-items: center; gap: .6rem; }
  .tm-marca-icono {
    width: 36px; height: 36px; background: var(--menta);
    border-radius: 10px; display: flex; align-items: center; justify-content: center;
  }
  .tm-marca-icono svg { width: 20px; height: 20px; color: var(--fondo); }
  .tm-marca-nombre { font-family: 'DM Serif Display', serif; font-size: 1.35rem; }
  .tm-btn-volver {
    background: transparent; color: var(--suave);
    border: 1.5px solid var(--borde); border-radius: 10px; padding: .5rem 1.1rem;
    font-size: .85rem; font-family: 'DM Sans', sans-serif; cursor: pointer;
    transition: all .2s; text-decoration: none; display: inline-flex; align-items: center; gap: .4rem;
  }
  .tm-btn-volver:hover { border-color: var(--menta); color: var(--menta); }
  .tm-tarjeta {
    background: var(--tarjeta); border: 1px solid var(--borde); border-radius: 20px;
    max-width: 1000px; margin: 0 auto; padding: 2rem;
    box-shadow: 0 32px 80px rgba(0,0,0,.5); animation: tm-subir .45s ease both;
  }
  @keyframes tm-subir {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .tm-titulo { font-family: 'DM Serif Display', serif; font-size: 1.5rem; margin-bottom: .3rem; }
  .tm-fecha-hoy { font-size: .88rem; color: var(--suave); margin-bottom: 1.5rem; }
  .tm-filtro-fila { display: flex; align-items: center; gap: .75rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
  .tm-select {
    background: var(--campo); border: 1.5px solid var(--borde); color: var(--texto);
    border-radius: 10px; padding: .55rem .9rem; font-size: .88rem;
    font-family: 'DM Sans', sans-serif; transition: border-color .2s; min-width: 260px;
  }
  .tm-select:focus { outline: none; border-color: var(--menta); }
  .tm-select option { background: var(--campo); }
  .tm-btn-consultar {
    background: var(--menta); color: var(--fondo); border: none; border-radius: 10px;
    padding: .55rem 1.2rem; font-size: .88rem; font-weight: 600;
    font-family: 'DM Sans', sans-serif; cursor: pointer; transition: background .2s;
  }
  .tm-btn-consultar:hover { background: var(--menta-oscuro); }
  .tm-tabla-wrap { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; }
  thead th {
    background: var(--campo); color: var(--menta); border-bottom: 1px solid var(--borde);
    font-size: .76rem; text-transform: uppercase; letter-spacing: .06em;
    font-weight: 500; padding: .8rem 1rem; text-align: left; white-space: nowrap;
  }
  tbody tr { border-bottom: 1px solid var(--borde); transition: background .15s; }
  tbody tr:last-child { border-bottom: none; }
  tbody tr:hover { background: rgba(45,212,191,.04); }
  tbody td { padding: .8rem 1rem; font-size: .87rem; vertical-align: middle; }
  .tm-vacio { text-align: center; color: var(--suave); padding: 2.5rem !important; }
  .tm-badge {
    display: inline-flex; align-items: center; border-radius: 20px;
    padding: .2rem .65rem; font-size: .75rem; font-weight: 500;
  }
  .tm-badge-verde { background: rgba(74,222,128,.12); color: var(--exito); border: 1px solid rgba(74,222,128,.3); }
  .tm-badge-amarillo { background: rgba(251,191,36,.12); color: var(--alerta); border: 1px solid rgba(251,191,36,.3); }
  .tm-btn-tomar {
    background: var(--menta); color: var(--fondo); border: none; border-radius: 8px;
    padding: .32rem .8rem; font-size: .8rem; font-weight: 600;
    font-family: 'DM Sans', sans-serif; cursor: pointer; transition: background .2s;
  }
  .tm-btn-tomar:hover { background: var(--menta-oscuro); }
  .tm-btn-tomar:disabled { background: var(--campo); color: var(--suave); cursor: not-allowed; }
  .tm-alerta-error {
    background: rgba(244,114,106,.1); border: 1px solid var(--error); color: var(--error);
    border-radius: 12px; padding: .85rem 1rem; margin-bottom: 1.25rem; font-size: .88rem;
  }
  .tm-spinner {
    display: inline-block; width: 15px; height: 15px;
    border: 2px solid var(--borde); border-top-color: var(--menta);
    border-radius: 50%; animation: tm-spin .7s linear infinite; vertical-align: middle; margin-right: .35rem;
  }
  @keyframes tm-spin { to { transform: rotate(360deg); } }
  .tm-notif-ctn { position: fixed; top: 1.25rem; right: 1.25rem; z-index: 9999; }
  .tm-notif {
    background: var(--tarjeta); border: 1px solid var(--exito); border-radius: 12px;
    padding: .85rem 1.1rem; font-size: .85rem; margin-bottom: .5rem; min-width: 240px;
    animation: tm-deslizar .3s ease both;
  }
  .tm-notif.err { border-color: var(--error); }
  @keyframes tm-deslizar {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
  }
`;

const pad = n => String(n).padStart(2, '0');

export default function Tomas() {
  const [pacientes, setPacientes] = useState([]);
  const [pacienteId, setPacienteId] = useState('');
  const [recordatorios, setRecordatorios] = useState(null); // null = sin consultar
  const [cargandoPanel, setCargandoPanel] = useState(false);
  const [errorPanel, setErrorPanel] = useState('');
  const [tomasLocales, setTomasLocales] = useState({}); // recordatorio_id -> true
  const [tomasGuardando, setTomasGuardando] = useState({});
  const [notifs, setNotifs] = useState([]);

  const fechaHoy = new Date().toLocaleDateString('es-CO', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
    return () => document.head.removeChild(style);
  }, []);

  useEffect(() => {
    cargarPacientes();
  }, []);

  async function cargarPacientes() {
    try {
      const res = await api.obtenerPacientes();
      if (!res.ok) throw new Error();
      const lista = Array.isArray(res.body) ? res.body : (res.body.pacientes || []);
      setPacientes(lista);
    } catch {
      setPacientes([]);
    }
  }

  function mostrarNotif(msg, esError = false) {
    const id = Date.now();
    setNotifs(prev => [...prev, { id, msg, esError }]);
    setTimeout(() => setNotifs(prev => prev.filter(n => n.id !== id)), 3500);
  }

  async function cargarPanelPaciente() {
  setErrorPanel('');
  if (!pacienteId) { setErrorPanel('Selecciona un paciente primero.'); return; }
  setCargandoPanel(true);
  setRecordatorios(null);
  setTomasLocales({});
  try {
    const res = await api.obtenerMedicamentos(pacienteId);
    if (!res.ok) throw new Error('Error al cargar medicamentos.');
    
    const meds = Array.isArray(res.body) ? res.body : [];
    const hoy = new Date().toISOString().split('T')[0];
    
    // Expandir cada medicamento en sus horarios
    const items = [];
    for (const m of meds) {
      const horarios = m.horario ? m.horario.split(',').map(h => h.trim()).filter(Boolean) : [];
      for (const hora of horarios) {
        items.push({
          recordatorio_id: `${m.id}_${hora}`,
          paciente_id: pacienteId,
          medicamento_id: m.id,
          medicamento_nombre: m.nombre,
          dosis: m.dosis,
          hora_recordatorio: hora,
          fecha_inicio: m.fecha_inicio,
          tomado: false,
          observaciones: '',
        });
      }
    }
    setRecordatorios(items);
  } catch (e) {
    setErrorPanel(e.message || 'Error de conexión.');
    setRecordatorios([]);
  } finally {
    setCargandoPanel(false);
  }
}

  async function marcarTomada(r) {
    setTomasGuardando(prev => ({ ...prev, [r.recordatorio_id]: true }));
    const ahora = new Date();
    const fechaHoraToma = `${ahora.getFullYear()}-${pad(ahora.getMonth()+1)}-${pad(ahora.getDate())} ${pad(ahora.getHours())}:${pad(ahora.getMinutes())}:${pad(ahora.getSeconds())}`;
    const datos = {
      paciente_id: r.paciente_id,
      medicamento_id: r.medicamento_id,
      recordatorio_id: r.recordatorio_id.includes('_') ? null : r.recordatorio_id,
      fecha_programada: new Date().toISOString().split('T')[0] + ' ' + r.hora_recordatorio + ':00',
      fecha_hora_toma: fechaHoraToma,
      estado: 'tomada',
      observaciones: 'Marcada'
    };
    try {
      const res = await api.registrarToma(datos);
      if (!res.ok) {
        mostrarNotif(res.body?.detail || 'Error al registrar la toma.', true);
        return;
      }
      mostrarNotif('Toma registrada correctamente ✓');
      setTomasLocales(prev => ({ ...prev, [r.recordatorio_id]: true }));
    } catch {
      mostrarNotif('Error de conexión con el servidor.', true);
    } finally {
      setTomasGuardando(prev => ({ ...prev, [r.recordatorio_id]: false }));
    }
  }

  const renderTabla = () => {
    if (cargandoPanel) {
      return <tr><td className="tm-vacio" colSpan={6}><span className="tm-spinner" /> Cargando…</td></tr>;
    }
    if (recordatorios === null) {
      return <tr><td className="tm-vacio" colSpan={6}>Selecciona un paciente para ver sus tomas del día.</td></tr>;
    }
    if (recordatorios.length === 0) {
      return <tr><td className="tm-vacio" colSpan={6}>No hay medicamentos programados para hoy.</td></tr>;
    }
    return recordatorios.map(r => {
      const tomada = r.tomada || tomasLocales[r.recordatorio_id];
      const guardando = tomasGuardando[r.recordatorio_id];
      return (
        <tr key={r.recordatorio_id}>
          <td style={{ fontWeight: 500 }}>{r.medicamento_nombre || '—'}</td>
          <td>{r.dosis || '—'}</td>
          <td>{r.hora_recordatorio || '—'}</td>
          <td>
            {tomada
              ? <span className="tm-badge tm-badge-verde">Tomada ✓</span>
              : <span className="tm-badge tm-badge-amarillo">Pendiente</span>}
          </td>
          <td>{r.observaciones || <span style={{ color: 'var(--suave)' }}>—</span>}</td>
          <td>
            {tomada ? '—' : (
              <button
                className="tm-btn-tomar"
                disabled={guardando}
                onClick={() => marcarTomada(r)}
              >
                {guardando ? 'Guardando…' : 'Marcar tomada'}
              </button>
            )}
          </td>
        </tr>
      );
    });
  };

  return (
    <div className="tm-body">
      <style>{css}</style>

      <div className="tm-notif-ctn">
        {notifs.map(n => (
          <div key={n.id} className={`tm-notif${n.esError ? ' err' : ''}`}>{n.msg}</div>
        ))}
      </div>

      <div className="tm-encabezado">
        <div className="tm-marca">
          <div className="tm-marca-icono">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 8v4m0 4h.01M3 12a9 9 0 1 0 18 0A9 9 0 0 0 3 12z"/>
            </svg>
          </div>
          <span className="tm-marca-nombre">MedTrack</span>
        </div>
        <a href="dashboard.html" className="tm-btn-volver">← Volver al dashboard</a>
      </div>

      <div className="tm-tarjeta">
        <h2 className="tm-titulo">Marcar tomas</h2>
        <p className="tm-fecha-hoy">{fechaHoy}</p>

        <div className="tm-filtro-fila">
          <select
            className="tm-select"
            value={pacienteId}
            onChange={e => setPacienteId(e.target.value)}
          >
            <option value="">{pacientes.length === 0 ? 'Cargando pacientes…' : 'Selecciona un paciente…'}</option>
            {pacientes.map(p => (
              <option key={p.id} value={p.id}>{p.nombres} {p.apellidos}</option>
            ))}
          </select>
          <button className="tm-btn-consultar" onClick={cargarPanelPaciente}>Ver tomas</button>
        </div>

        {errorPanel && <div className="tm-alerta-error">{errorPanel}</div>}

        <div className="tm-tabla-wrap">
          <table>
            <thead>
              <tr>
                <th>Medicamento</th>
                <th>Dosis</th>
                <th>Hora programada</th>
                <th>Estado</th>
                <th>Observaciones</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              {renderTabla()}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}