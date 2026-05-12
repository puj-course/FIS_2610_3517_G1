import { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import api from "../api";

const css = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
  :root {
    --color-menta: #2DD4BF; --color-menta-oscuro: #0F9D8A;
    --color-fondo: #0F1B2D; --color-campo: #1E2D3D; --color-tarjeta: #162030;
    --color-borde: #243447; --color-texto: #E2EAF4; --color-texto-suave: #7A95B0;
    --color-error: #F4726A; --color-exito: #4ADE80; --color-advertencia: #FBBF24;
  }
  *, *::before, *::after { box-sizing: border-box; }
  .rp-body {
    margin: 0; min-height: 100vh; background-color: var(--color-fondo);
    font-family: 'DM Sans', sans-serif; color: var(--color-texto); padding: 2rem 1rem;
    background-image:
      radial-gradient(ellipse 60% 50% at 80% 10%, rgba(45,212,191,.12) 0%, transparent 70%),
      radial-gradient(ellipse 40% 40% at 10% 80%, rgba(45,212,191,.07) 0%, transparent 60%);
  }
  .rp-encabezado {
    max-width: 1100px; margin: 0 auto 2rem;
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;
  }
  .rp-marca { display: flex; align-items: center; gap: .6rem; }
  .rp-marca-icono { width: 36px; height: 36px; background: var(--color-menta); border-radius: 10px; display: flex; align-items: center; justify-content: center; }
  .rp-marca-icono svg { width: 20px; height: 20px; color: var(--color-fondo); }
  .rp-marca-nombre { font-family: 'DM Serif Display', serif; font-size: 1.4rem; }
  .rp-boton-volver {
    background: transparent; border: 1.5px solid var(--color-borde); color: var(--color-texto-suave);
    border-radius: 10px; padding: .5rem 1.2rem; font-size: .88rem; font-family: 'DM Sans', sans-serif;
    cursor: pointer; display: inline-flex; align-items: center; gap: .4rem; transition: border-color .2s, color .2s;
  }
  .rp-boton-volver:hover { border-color: var(--color-menta); color: var(--color-menta); }
  .rp-tarjeta {
    background: var(--color-tarjeta); border: 1px solid var(--color-borde); border-radius: 20px;
    max-width: 1100px; margin: 0 auto 1.5rem; padding: 2rem;
    box-shadow: 0 32px 80px rgba(0,0,0,.5); animation: rp-aparecer .45s ease both;
  }
  @keyframes rp-aparecer { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: translateY(0); } }
  .rp-perfil-header { display: flex; align-items: center; gap: 1.2rem; flex-wrap: wrap; }
  .rp-avatar {
    width: 64px; height: 64px; background: rgba(45,212,191,.15); border: 2px solid var(--color-menta);
    border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  }
  .rp-avatar svg { width: 30px; height: 30px; color: var(--color-menta); }
  .rp-perfil-nombre { font-family: 'DM Serif Display', serif; font-size: 1.6rem; margin: 0; line-height: 1.2; }
  .rp-perfil-meta { color: var(--color-texto-suave); font-size: .85rem; margin-top: .25rem; }
  .rp-grid-datos { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; margin-top: 1.5rem; }
  .rp-dato-item label { display: block; font-size: .72rem; text-transform: uppercase; letter-spacing: .05em; color: var(--color-texto-suave); margin-bottom: .2rem; }
  .rp-dato-item span { font-size: .9rem; font-weight: 500; }
  .rp-titulo-seccion { font-family: 'DM Serif Display', serif; font-size: 1.15rem; margin-bottom: 1.25rem; }
  .rp-grid-metricas { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; }
  .rp-metrica { background: var(--color-campo); border: 1px solid var(--color-borde); border-radius: 14px; padding: 1.2rem 1rem; text-align: center; }
  .rp-metrica-valor { font-family: 'DM Serif Display', serif; font-size: 2rem; line-height: 1; margin-bottom: .3rem; }
  .rp-metrica-valor.verde { color: var(--color-exito); }
  .rp-metrica-valor.menta { color: var(--color-menta); }
  .rp-metrica-valor.amarillo { color: var(--color-advertencia); }
  .rp-metrica-valor.rojo { color: var(--color-error); }
  .rp-metrica-etiqueta { font-size: .78rem; color: var(--color-texto-suave); text-transform: uppercase; letter-spacing: .05em; }
  .rp-barra-contenedor { margin-top: 1.2rem; }
  .rp-barra-label { display: flex; justify-content: space-between; font-size: .82rem; color: var(--color-texto-suave); margin-bottom: .4rem; }
  .rp-barra-progreso { height: 8px; background: var(--color-campo); border-radius: 99px; overflow: hidden; }
  .rp-barra-relleno { height: 100%; border-radius: 99px; background: var(--color-menta); transition: width .6s ease; }
  .rp-lista-alertas { list-style: none; padding: 0; margin: 0; }
  .rp-alerta-item { display: flex; align-items: flex-start; gap: .75rem; padding: .9rem 1rem; border-radius: 12px; border: 1px solid var(--color-borde); margin-bottom: .6rem; background: var(--color-campo); }
  .rp-alerta-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; margin-top: .35rem; }
  .rp-alerta-dot.alta { background: var(--color-error); }
  .rp-alerta-dot.media { background: var(--color-advertencia); }
  .rp-alerta-dot.baja { background: var(--color-menta); }
  .rp-alerta-mensaje { font-size: .88rem; line-height: 1.4; }
  .rp-alerta-fecha { font-size: .75rem; color: var(--color-texto-suave); margin-top: .15rem; }
  .rp-sin-alertas { text-align: center; color: var(--color-texto-suave); padding: 1.5rem; font-size: .88rem; }
  .rp-alerta-error {
    background: rgba(244,114,106,.1); border: 1px solid var(--color-error); color: var(--color-error);
    border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1.5rem; max-width: 1100px; margin-left: auto; margin-right: auto;
  }
  .rp-spinner {
    display: inline-block; width: 18px; height: 18px;
    border: 2px solid var(--color-borde); border-top-color: var(--color-menta);
    border-radius: 50%; animation: rp-girar .7s linear infinite; vertical-align: middle; margin-right: .5rem;
  }
  @keyframes rp-girar { to { transform: rotate(360deg); } }
  .rp-cargando { text-align: center; padding: 3rem; color: var(--color-texto-suave); }
  @media (max-width: 600px) { .rp-tarjeta { padding: 1.25rem; } .rp-grid-metricas { grid-template-columns: 1fr 1fr; } }
`;

function formatearPorcentaje(valor) {
  if (Number.isInteger(valor)) return valor.toString();
  return valor.toFixed(1);
}

export default function ResumenPaciente() {
  // ✅ CORREGIDO: usar useSearchParams en vez de window.location.search
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  // MongoDB: el id es un string ObjectId
  const pacienteId = searchParams.get('id');

  const [estado,     setEstado]     = useState('cargando');
  const [errorMsg,   setErrorMsg]   = useState('');
  const [paciente,   setPaciente]   = useState(null);
  const [resumen,    setResumen]    = useState(null);
  const [pct,        setPct]        = useState(0);
  const [pctVisible, setPctVisible] = useState(0);

  useEffect(() => {
    if (!pacienteId) {
      setErrorMsg('No se especificó un paciente. Por favor, selecciona uno desde la lista.');
      setEstado('error');
      return;
    }
    cargar();
  }, [pacienteId]);

  useEffect(() => {
    if (pct > 0) setTimeout(() => setPctVisible(pct), 50);
  }, [pct]);

  async function cargar() {
    try {
      const [resPaciente, resResumen] = await Promise.all([
        api.obtenerPaciente(pacienteId),
        api.obtenerResumen(pacienteId),
      ]);
      if (!resPaciente.ok) {
        setErrorMsg(resPaciente.status === 404
          ? 'El paciente seleccionado no existe o fue eliminado.'
          : 'No se pudo cargar la información del paciente.');
        setEstado('error');
        return;
      }
      if (!resResumen.ok) {
        setErrorMsg('Se cargó el paciente pero no se pudo obtener su resumen.');
        setEstado('error');
        return;
      }
      // Normalizar _id de MongoDB
      const p = resPaciente.body;
      if (p._id && !p.id) p.id = p._id;
      setPaciente(p);
      setResumen(resResumen.body);
      const pctBase = resResumen.body.porcentaje_cumplimiento ?? 0;
      setPct(Math.max(0, Math.min(100, Number(pctBase) || 0)));
      setEstado('listo');
    } catch (error) {
      console.error(error);
      setErrorMsg('No se pudo conectar con el servidor.');
      setEstado('error');
    }
  }

  const renderPerfil = () => {
    if (!paciente) return null;
    const nombreCompleto = ((paciente.nombres || '') + ' ' + (paciente.apellidos || '')).trim() || 'Paciente sin nombre';
    const meta = [paciente.tipo_documento, paciente.numero_documento, paciente.diagnostico_principal].filter(Boolean).join(' · ') || 'Sin información adicional';
    const campos = [
      { label: 'Fecha de nacimiento', valor: paciente.fecha_nacimiento },
      { label: 'Género',              valor: paciente.genero },
      { label: 'Teléfono',            valor: paciente.telefono_contacto },
      { label: 'EPS / Aseguradora',   valor: paciente.eps_aseguradora },
      { label: 'Alergias conocidas',  valor: paciente.alergias_conocidas },
      { label: 'Observaciones',       valor: paciente.observaciones_adicionales },
    ].filter(c => c.valor);

    return (
      <div className="rp-tarjeta">
        <div className="rp-perfil-header">
          <div className="rp-avatar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </div>
          <div>
            <h1 className="rp-perfil-nombre">{nombreCompleto}</h1>
            <p className="rp-perfil-meta">{meta}</p>
          </div>
        </div>
        <div className="rp-grid-datos">
          {campos.map(c => (
            <div key={c.label} className="rp-dato-item">
              <label>{c.label}</label>
              <span>{c.valor}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderResumen = () => {
    if (!resumen) return null;
    const medicamentosActivos = resumen.total_medicamentos_activos ?? 0;
    const tomasRealizadas     = resumen.tomas_realizadas ?? resumen.tomas_registradas_hoy ?? 0;
    const tomasPendientes     = resumen.tomas_atrasadas ?? ((resumen.tomas_pendientes ?? 0) + (resumen.tomas_omitidas ?? 0));
    const pctTexto  = formatearPorcentaje(pct) + '%';
    const colorPct  = pct >= 80 ? 'verde' : pct >= 50 ? 'amarillo' : 'rojo';
    const alertas   = resumen.alertas_activas || [];

    return (
      <>
        <div className="rp-tarjeta">
          <h2 className="rp-titulo-seccion">Resumen del tratamiento</h2>
          <div className="rp-grid-metricas">
            <div className="rp-metrica">
              <div className="rp-metrica-valor menta">{medicamentosActivos}</div>
              <div className="rp-metrica-etiqueta">Medicamentos activos</div>
            </div>
            <div className="rp-metrica">
              <div className="rp-metrica-valor verde">{tomasRealizadas}</div>
              <div className="rp-metrica-etiqueta">Tomas realizadas</div>
            </div>
            <div className="rp-metrica">
              <div className="rp-metrica-valor amarillo">{tomasPendientes}</div>
              <div className="rp-metrica-etiqueta">Pendientes u omitidas</div>
            </div>
            <div className="rp-metrica">
              <div className={`rp-metrica-valor ${colorPct}`}>{pctTexto}</div>
              <div className="rp-metrica-etiqueta">Cumplimiento</div>
            </div>
          </div>
          <div className="rp-barra-contenedor">
            <div className="rp-barra-label"><span>Cumplimiento del tratamiento</span><span>{pctTexto}</span></div>
            <div className="rp-barra-progreso">
              <div className="rp-barra-relleno" style={{ width: `${pctVisible}%` }} />
            </div>
          </div>
        </div>
        <div className="rp-tarjeta">
          <h2 className="rp-titulo-seccion">Alertas activas</h2>
          <ul className="rp-lista-alertas">
            {alertas.length === 0 ? (
              <li className="rp-sin-alertas">✓ Sin alertas activas</li>
            ) : alertas.map((alerta, i) => {
              const severidad = (alerta.severidad || 'baja').toLowerCase();
              return (
                <li key={i} className="rp-alerta-item">
                  <span className={`rp-alerta-dot ${severidad}`} />
                  <div>
                    <div className="rp-alerta-mensaje">{alerta.mensaje || 'Alerta sin descripción'}</div>
                    {alerta.fecha_creacion && <div className="rp-alerta-fecha">{alerta.fecha_creacion}</div>}
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      </>
    );
  };

  return (
    <div className="rp-body">
      <style>{css}</style>
      <div className="rp-encabezado">
        <div className="rp-marca">
          <div className="rp-marca-icono">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <span className="rp-marca-nombre">MedTrack</span>
        </div>
        {}
        <button className="rp-boton-volver" onClick={() => navigate('/pacientes')}>
          ← Volver a pacientes
        </button>
      </div>

      {estado === 'error'    && <div className="rp-alerta-error">{errorMsg}</div>}
      {estado === 'cargando' && (
        <div className="rp-tarjeta">
          <div className="rp-cargando"><span className="rp-spinner" />Cargando información del paciente…</div>
        </div>
      )}
      {estado === 'listo' && <>{renderPerfil()}{renderResumen()}</>}
    </div>
  );
}