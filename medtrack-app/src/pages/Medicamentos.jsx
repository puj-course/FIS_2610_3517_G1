import { useState, useEffect } from "react";
import api from "../api";

const estilos = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
  :root {
    --color-menta: #2DD4BF; --color-menta-oscuro: #0F9D8A;
    --color-fondo: #0F1B2D; --color-campo: #1E2D3D; --color-tarjeta: #162030;
    --color-borde: #243447; --color-texto: #E2EAF4; --color-texto-suave: #7A95B0;
    --color-error: #F4726A; --color-exito: #4ADE80;
  }
  .med-body { margin: 0; min-height: 100vh; background-color: var(--color-fondo); font-family: 'DM Sans', sans-serif; color: var(--color-texto); padding: 2rem 1rem; background-image: radial-gradient(ellipse 60% 50% at 80% 10%, rgba(45,212,191,.13) 0%, transparent 70%), radial-gradient(ellipse 40% 40% at 10% 80%, rgba(45,212,191,.07) 0%, transparent 60%); }
  .med-contenedor { max-width: 800px; margin: 0 auto; }
  @keyframes med-aparecer { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: translateY(0); } }
  .med-marca { display: flex; align-items: center; gap: .6rem; margin-bottom: 2rem; }
  .med-marca-icono { width: 38px; height: 38px; background: var(--color-menta); border-radius: 10px; display: flex; align-items: center; justify-content: center; }
  .med-marca-nombre { font-family: 'DM Serif Display', serif; font-size: 1.45rem; color: var(--color-texto); }
  .med-titulo    { font-family: 'DM Serif Display', serif; font-size: 1.75rem; margin: 0 0 .25rem; }
  .med-subtitulo { font-size: .88rem; color: var(--color-texto-suave); margin: 0 0 1.75rem; }
  .med-vista { animation: med-aparecer .35s ease both; }
  .med-paciente-card { background: var(--color-tarjeta); border: 1px solid var(--color-borde); border-radius: 14px; padding: 1.1rem 1.4rem; margin-bottom: .85rem; display: flex; align-items: center; gap: 1rem; cursor: pointer; transition: border-color .2s, box-shadow .2s; }
  .med-paciente-card:hover { border-color: rgba(45,212,191,.5); box-shadow: 0 4px 20px rgba(45,212,191,.08); }
  .med-paciente-avatar { width: 44px; height: 44px; background: rgba(45,212,191,.12); border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-family: 'DM Serif Display', serif; font-size: 1.1rem; color: var(--color-menta); }
  .med-paciente-info { flex: 1; min-width: 0; }
  .med-paciente-nombre { font-weight: 600; font-size: .97rem; margin: 0 0 .2rem; }
  .med-paciente-datos  { font-size: .8rem; color: var(--color-texto-suave); margin: 0; }
  .med-paciente-flecha { color: var(--color-texto-suave); flex-shrink: 0; }
  .med-boton-volver { background: none; border: 1.5px solid var(--color-borde); color: var(--color-texto-suave); border-radius: 10px; padding: .5rem 1rem; font-size: .85rem; font-family: 'DM Sans', sans-serif; cursor: pointer; display: inline-flex; align-items: center; gap: .4rem; transition: border-color .2s, color .2s; margin-bottom: 1.5rem; }
  .med-boton-volver:hover { border-color: var(--color-menta); color: var(--color-menta); }
  .med-paciente-header { background: var(--color-tarjeta); border: 1px solid var(--color-borde); border-radius: 14px; padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 1rem; }
  .med-card { background: var(--color-tarjeta); border: 1px solid var(--color-borde); border-radius: 14px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; animation: med-aparecer .3s ease both; transition: border-color .2s; }
  .med-card:hover { border-color: rgba(45,212,191,.3); }
  .med-header { display: flex; align-items: center; gap: .75rem; margin-bottom: .85rem; }
  .med-icono { width: 38px; height: 38px; background: rgba(45,212,191,.12); border-radius: 9px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
  .med-nombre { font-family: 'DM Serif Display', serif; font-size: 1.1rem; margin: 0; color: var(--color-texto); }
  .med-tags { display: flex; flex-wrap: wrap; gap: .4rem; margin-bottom: .75rem; }
  .med-tag { background: var(--color-campo); border: 1px solid var(--color-borde); border-radius: 6px; padding: .22rem .65rem; font-size: .78rem; color: var(--color-texto-suave); display: inline-flex; align-items: center; gap: .3rem; }
  .med-observaciones { font-size: .82rem; color: var(--color-texto-suave); border-top: 1px solid var(--color-borde); padding-top: .75rem; }
  .med-observaciones strong { color: var(--color-texto); }
  .med-contador { font-size: .82rem; color: var(--color-texto-suave); margin-bottom: 1rem; }
  .med-contador span { color: var(--color-menta); font-weight: 600; }
  .med-estado { text-align: center; padding: 3rem 1rem; color: var(--color-texto-suave); font-size: .92rem; }
  .med-alerta-error { background: rgba(244,114,106,.12); border: 1px solid rgba(244,114,106,.4); color: var(--color-error); border-radius: 10px; padding: .7rem 1rem; font-size: .85rem; margin-bottom: 1rem; }
`;

const IconMedtrack = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
       strokeLinecap="round" strokeLinejoin="round" style={{ width: 22, height: 22, color: "var(--color-fondo)" }}>
    <path d="M12 8v4m0 4h.01M3 12a9 9 0 1 0 18 0A9 9 0 0 0 3 12z" />
  </svg>
);
const IconChevronRight = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
       strokeLinecap="round" strokeLinejoin="round" style={{ width: 18, height: 18 }}>
    <polyline points="9 18 15 12 9 6" />
  </svg>
);
const IconChevronLeft = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
       strokeLinecap="round" strokeLinejoin="round" style={{ width: 16, height: 16 }}>
    <polyline points="15 18 9 12 15 6" />
  </svg>
);
const IconPill = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
       strokeLinecap="round" strokeLinejoin="round" style={{ width: 18, height: 18, color: "var(--color-menta)" }}>
    <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
  </svg>
);

export default function Medicamentos() {
  const [vista,          setVista]         = useState("pacientes");
  const [pacientes,      setPacientes]     = useState([]);
  const [pacienteActual, setPacienteActual] = useState(null);
  const [medicamentos,   setMedicamentos]  = useState([]);
  const [cargandoPac,    setCargandoPac]   = useState(true);
  const [cargandoMed,    setCargandoMed]   = useState(false);
  const [errorPac,       setErrorPac]      = useState("");
  const [errorMed,       setErrorMed]      = useState("");

  useEffect(() => {
    const cargarPacientes = async () => {
      setCargandoPac(true);
      setErrorPac("");
      try {
        // ✅ Usa api en vez de fetch directo
        const res = await api.obtenerPacientes();
        if (!res.ok) throw new Error();
        const lista = Array.isArray(res.body) ? res.body : (res.body.pacientes || []);
        // Normalizar _id de MongoDB
        setPacientes(lista.map(p => ({ ...p, id: p.id || p._id })));
      } catch {
        setErrorPac("No se pudo conectar al servidor. ¿Está corriendo el backend?");
      } finally {
        setCargandoPac(false);
      }
    };
    cargarPacientes();
  }, []);

  const verMedicamentos = async (paciente) => {
    setPacienteActual(paciente);
    setVista("medicamentos");
    setErrorMed("");
    setCargandoMed(true);
    setMedicamentos([]);
    try {
      const id = paciente.id || paciente._id;
      // ✅ Usa api en vez de fetch directo
      const res = await api.obtenerMedicamentos(id);
      if (!res.ok) {
        if (res.status === 404) { setErrorMed("No se encontró el paciente en la base de datos."); return; }
        throw new Error();
      }
      const lista = Array.isArray(res.body) ? res.body : (res.body.medicamentos || []);
      setMedicamentos(lista.map(m => ({ ...m, id: m.id || m._id })));
    } catch {
      setErrorMed("No se pudo conectar al servidor.");
    } finally {
      setCargandoMed(false);
    }
  };

  const volverAPacientes = () => { setVista("pacientes"); setPacienteActual(null); };

  const renderPacientes = () => (
    <div className="med-vista">
      <h1 className="med-titulo">Pacientes</h1>
      <p className="med-subtitulo">Selecciona un paciente para ver sus medicamentos.</p>
      {errorPac && <div className="med-alerta-error">{errorPac}</div>}
      {cargandoPac && <div className="med-estado">Cargando pacientes...</div>}
      {!cargandoPac && !errorPac && pacientes.length === 0 && <div className="med-estado">No hay pacientes registrados aún.</div>}
      {pacientes.map((p) => (
        <div key={p.id} className="med-paciente-card" onClick={() => verMedicamentos(p)}>
          <div className="med-paciente-avatar">{(p.nombres || '?').charAt(0).toUpperCase()}</div>
          <div className="med-paciente-info">
            <p className="med-paciente-nombre">{p.nombres} {p.apellidos}</p>
            <p className="med-paciente-datos">{p.diagnostico_principal || "Sin diagnóstico registrado"}</p>
          </div>
          <div className="med-paciente-flecha"><IconChevronRight /></div>
        </div>
      ))}
    </div>
  );

  const renderMedicamentos = () => (
    <div className="med-vista">
      <button className="med-boton-volver" onClick={volverAPacientes}><IconChevronLeft /> Volver a pacientes</button>
      {errorMed && <div className="med-alerta-error">{errorMed}</div>}
      {pacienteActual && (
        <div className="med-paciente-header">
          <div className="med-paciente-avatar" style={{ width: 52, height: 52, fontSize: "1.3rem" }}>
            {(pacienteActual.nombres || '?').charAt(0).toUpperCase()}
          </div>
          <div className="med-paciente-info">
            <p className="med-paciente-nombre" style={{ fontSize: "1.05rem" }}>{pacienteActual.nombres} {pacienteActual.apellidos}</p>
            <p className="med-paciente-datos">{pacienteActual.diagnostico_principal || "Sin diagnóstico registrado"}</p>
          </div>
        </div>
      )}
      {cargandoMed && <div className="med-estado">Cargando medicamentos...</div>}
      {!cargandoMed && !errorMed && medicamentos.length === 0 && <div className="med-estado">Este paciente no tiene medicamentos registrados aún.</div>}
      {!cargandoMed && medicamentos.length > 0 && (
        <>
          <div className="med-contador">Se encontraron <span>{medicamentos.length}</span> medicamento(s) registrado(s).</div>
          {medicamentos.map((med, i) => (
            <div key={med.id || i} className="med-card">
              <div className="med-header">
                <div className="med-icono"><IconPill /></div>
                {/* MongoDB puede tener nombre_medicamento o nombre */}
                <h3 className="med-nombre">{med.nombre_medicamento || med.nombre}</h3>
              </div>
              <div className="med-tags">
                <span className="med-tag">Dosis: {med.dosis_cantidad} {med.dosis_unidad || med.dosis}</span>
                <span className="med-tag">Frecuencia: {med.frecuencia}</span>
                <span className="med-tag">Horario: {Array.isArray(med.horarios) ? med.horarios.join(', ') : (med.horario || '—')}</span>
                <span className="med-tag">Inicio: {med.fecha_inicio}</span>
              </div>
              {med.instrucciones && (
                <div className="med-observaciones"><strong>Instrucciones:</strong> {med.instrucciones}</div>
              )}
            </div>
          ))}
        </>
      )}
    </div>
  );

  return (
    <>
      <style>{estilos}</style>
      <div className="med-body">
        <div className="med-contenedor">
          <div className="med-marca">
            <div className="med-marca-icono"><IconMedtrack /></div>
            <span className="med-marca-nombre">MedTrack</span>
          </div>
          {vista === "pacientes" ? renderPacientes() : renderMedicamentos()}
        </div>
      </div>
    </>
  );
}