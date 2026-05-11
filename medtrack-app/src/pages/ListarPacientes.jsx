import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
  .lp-root {
    margin: 0; min-height: 100vh; background-color: #0F1B2D;
    font-family: 'DM Sans', sans-serif; color: #E2EAF4; padding: 2rem 1rem;
    background-image:
      radial-gradient(ellipse 60% 50% at 80% 10%, rgba(45,212,191,.12) 0%, transparent 70%),
      radial-gradient(ellipse 40% 40% at 10% 80%, rgba(45,212,191,.07) 0%, transparent 60%);
  }
  .lp-encabezado {
    max-width: 1200px; margin: 0 auto 2rem;
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;
  }
  .lp-marca { display: flex; align-items: center; gap: .6rem; }
  .lp-marca-icono { width: 36px; height: 36px; background: #2DD4BF; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
  .lp-marca-icono svg { width: 20px; height: 20px; color: #0F1B2D; }
  .lp-marca-nombre { font-family: 'DM Serif Display', serif; font-size: 1.4rem; color: #E2EAF4; }
  .lp-boton-nuevo {
    background: #2DD4BF; color: #0F1B2D; border: none; border-radius: 12px;
    padding: .6rem 1.4rem; font-size: .9rem; font-weight: 600; font-family: 'DM Sans', sans-serif;
    cursor: pointer; transition: background .2s, box-shadow .2s;
    text-decoration: none; display: inline-flex; align-items: center; gap: .4rem;
  }
  .lp-boton-nuevo:hover { background: #0F9D8A; box-shadow: 0 8px 24px rgba(45,212,191,.3); color: #0F1B2D; }
  .lp-tarjeta {
    background: #162030; border: 1px solid #243447; border-radius: 20px;
    max-width: 1200px; margin: 0 auto; padding: 2rem;
    box-shadow: 0 32px 80px rgba(0,0,0,.5); animation: lp-aparecer .5s ease both;
  }
  @keyframes lp-aparecer { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
  .lp-titulo { font-family: 'DM Serif Display', serif; font-size: 1.5rem; margin-bottom: 1.5rem; }
  .lp-buscador {
    background: #1E2D3D; border: 1.5px solid #243447; color: #E2EAF4; border-radius: 10px;
    padding: .6rem .9rem; font-size: .9rem; font-family: 'DM Sans', sans-serif;
    width: 100%; max-width: 320px; margin-bottom: 1.5rem; transition: border-color .2s; outline: none;
  }
  .lp-buscador:focus { border-color: #2DD4BF; box-shadow: 0 0 0 3px rgba(45,212,191,.18); }
  .lp-buscador::placeholder { color: #4A6278; }
  .lp-alerta-error {
    background: rgba(244,114,106,.1); border: 1px solid #F4726A; color: #F4726A;
    border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1.5rem;
  }
  .lp-table-wrap { overflow-x: auto; }
  .lp-table { width: 100%; border-collapse: collapse; color: #E2EAF4; }
  .lp-table thead th {
    background: #1E2D3D; color: #2DD4BF; border-bottom: 1px solid #243447;
    font-size: .78rem; text-transform: uppercase; letter-spacing: .05em;
    font-weight: 500; padding: .85rem 1rem; white-space: nowrap; text-align: left;
  }
  .lp-table tbody tr { border-bottom: 1px solid #243447; transition: background .15s; cursor: pointer; }
  .lp-table tbody tr:hover { background: rgba(45,212,191,.10); }
  .lp-table tbody td { padding: .8rem 1rem; font-size: .88rem; vertical-align: middle; }
  .lp-vacio { text-align: center; color: #7A95B0; padding: 3rem !important; }
  .lp-badge-ver {
    background: transparent; border: 1px solid #2DD4BF; color: #2DD4BF;
    border-radius: 8px; padding: .25rem .65rem; font-size: .78rem; font-weight: 600;
    white-space: nowrap; transition: background .15s, color .15s; display: inline-block;
  }
  tr:hover .lp-badge-ver { background: #2DD4BF; color: #0F1B2D; }
  .lp-badge-alerta {
    display: inline-flex; align-items: center; gap: .35rem; border-radius: 999px;
    padding: .28rem .65rem; font-size: .76rem; font-weight: 700; white-space: nowrap; border: 1px solid transparent;
  }
  .lp-alerta-atrasada { background: rgba(250,204,21,.12); border-color: rgba(250,204,21,.45); color: #FACC15; }
  .lp-alerta-omitida  { background: rgba(248,113,113,.12); border-color: rgba(248,113,113,.45); color: #F87171; }
  .lp-alerta-mixta    { background: rgba(251,146,60,.12);  border-color: rgba(251,146,60,.45);  color: #FB923C; }
  .lp-sin-alerta { color: #7A95B0; font-size: .8rem; }
  .lp-spinner {
    display: inline-block; width: 18px; height: 18px;
    border: 2px solid #243447; border-top-color: #2DD4BF;
    border-radius: 50%; animation: lp-girar .7s linear infinite; vertical-align: middle; margin-right: .5rem;
  }
  @keyframes lp-girar { to { transform: rotate(360deg); } }
  @media (max-width: 768px) { .lp-tarjeta { padding: 1.25rem; } }
`;

function CeldaAlerta({ paciente }) {
  const alerta = paciente.alerta || {
    tiene_alerta: Boolean(paciente.tiene_tomas_atrasadas || paciente.tiene_tomas_omitidas),
    tipo: paciente.alerta_tomas || 'sin_alerta',
    atrasadas: paciente.total_tomas_atrasadas || 0,
    omitidas: paciente.total_tomas_omitidas || 0,
  };
  if (!alerta.tiene_alerta || alerta.tipo === 'sin_alerta')
    return <td><span className="lp-sin-alerta">Sin alerta</span></td>;
  if (alerta.tipo === 'mixta')
    return <td><span className="lp-badge-alerta lp-alerta-mixta">⚠️ {alerta.atrasadas} atrasada(s) / {alerta.omitidas} omitida(s)</span></td>;
  if (alerta.tipo === 'omitida')
    return <td><span className="lp-badge-alerta lp-alerta-omitida">🚨 {alerta.omitidas} omitida(s)</span></td>;
  if (alerta.tipo === 'atrasada')
    return <td><span className="lp-badge-alerta lp-alerta-atrasada">⏰ {alerta.atrasadas} atrasada(s)</span></td>;
  return <td><span className="lp-sin-alerta">Sin alerta</span></td>;
}

function FilaPaciente({ paciente, onClickFila }) {
  const v = (val) => (val !== null && val !== undefined && val !== '' ? String(val) : '—');
  // MongoDB: el id puede venir como _id (string ObjectId)
  const id = paciente.id || paciente._id;
  return (
    <tr onClick={() => onClickFila(id)} title={`Ver resumen de ${paciente.nombres || ''} ${paciente.apellidos || ''}`}>
      <td>{paciente.nombres  || ''}</td>
      <td>{paciente.apellidos || ''}</td>
      <td>{v(paciente.fecha_nacimiento)}</td>
      <td>{v(paciente.genero)}</td>
      <td>{v(paciente.tipo_documento)}</td>
      <td>{v(paciente.numero_documento)}</td>
      <td>{v(paciente.telefono_contacto)}</td>
      <td>{v(paciente.eps_aseguradora)}</td>
      <td>{v(paciente.diagnostico_principal)}</td>
      <td>{v(paciente.alergias_conocidas)}</td>
      <td>{v(paciente.observaciones_adicionales)}</td>
      <CeldaAlerta paciente={paciente} />
      <td><span className="lp-badge-ver">Ver resumen</span></td>
    </tr>
  );
}

export default function ListarPacientes() {
  const navigate = useNavigate();
  const [pacientes, setPacientes] = useState([]);
  const [busqueda,  setBusqueda]  = useState('');
  const [error,     setError]     = useState('');
  const [cargando,  setCargando]  = useState(true);

  useEffect(() => {
    async function cargar() {
      try {
        const resultado = await api.obtenerPacientes();
        if (!resultado.ok) { setError('Error al cargar los pacientes.'); return; }
        // MongoDB puede devolver { pacientes: [...] } o array directo
        const lista = resultado.body?.pacientes ?? resultado.body ?? [];
        const arr = Array.isArray(lista) ? lista : [];
        // Normalizar _id → id
        setPacientes(arr.map(p => ({ ...p, id: p.id || p._id })));
      } catch {
        setError('No se pudo conectar con el servidor.');
      } finally {
        setCargando(false);
      }
    }
    cargar();
  }, []);

  const filtrados = pacientes.filter((p) => {
    const t = busqueda.trim().toLowerCase();
    if (!t) return true;
    return (
      (p.nombres          || '').toLowerCase().includes(t) ||
      (p.apellidos        || '').toLowerCase().includes(t) ||
      (p.numero_documento || '').toLowerCase().includes(t)
    );
  });

  function irAResumen(id) {
    if (!id) return;
    navigate(`/resumen-paciente?id=${id}`);
  }

  return (
    <>
      <style>{CSS}</style>
      <div className="lp-root">
        <div className="lp-encabezado">
          <div className="lp-marca">
            <div className="lp-marca-icono">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
            </div>
            <span className="lp-marca-nombre">MedTrack</span>
          </div>
          <button className="lp-boton-nuevo" onClick={() => navigate('/registrar-paciente')}>
            + Nuevo paciente
          </button>
        </div>

        <div className="lp-tarjeta">
          <h2 className="lp-titulo">Lista de Pacientes</h2>
          <input
            type="text" className="lp-buscador"
            placeholder="Buscar por nombre, documento…"
            value={busqueda} onChange={(e) => setBusqueda(e.target.value)}
          />
          {error && <div className="lp-alerta-error">{error}</div>}
          <div className="lp-table-wrap">
            <table className="lp-table">
              <thead>
                <tr>
                  <th>Nombres</th><th>Apellidos</th><th>Fecha nac.</th><th>Género</th>
                  <th>Tipo doc.</th><th>N.º documento</th><th>Teléfono</th><th>EPS</th>
                  <th>Diagnóstico</th><th>Alergias</th><th>Observaciones</th><th>Alertas</th><th>Acción</th>
                </tr>
              </thead>
              <tbody>
                {cargando && (
                  <tr><td className="lp-vacio" colSpan={13}><span className="lp-spinner" />Cargando pacientes…</td></tr>
                )}
                {!cargando && filtrados.length === 0 && (
                  <tr><td className="lp-vacio" colSpan={13}>
                    {pacientes.length === 0 ? 'No hay pacientes registrados aún.' : 'No hay pacientes que coincidan con la búsqueda.'}
                  </td></tr>
                )}
                {!cargando && filtrados.map((p) => (
                  <FilaPaciente key={p.id || p._id} paciente={p} onClickFila={irAResumen} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}