import { useState, useEffect, useCallback } from "react";
import api from "../api";  

const estilos = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
  :root {
    --color-menta: #2DD4BF;
    --color-menta-oscuro: #0F9D8A;
    --color-fondo: #0F1B2D;
    --color-campo: #1E2D3D;
    --color-tarjeta: #162030;
    --color-borde: #243447;
    --color-texto: #E2EAF4;
    --color-texto-suave: #7A95B0;
    --color-error: #F4726A;
    --color-exito: #4ADE80;
  }
  .lr-body {
    margin: 0;
    min-height: 100vh;
    background-color: var(--color-fondo);
    font-family: 'DM Sans', sans-serif;
    color: var(--color-texto);
    padding: 2rem 1rem;
    background-image:
      radial-gradient(ellipse 60% 50% at 80% 10%, rgba(45,212,191,.12) 0%, transparent 70%),
      radial-gradient(ellipse 40% 40% at 10% 80%, rgba(45,212,191,.07) 0%, transparent 60%);
  }
  .lr-encabezado {
    max-width: 1100px; margin: 0 auto 2rem;
    display: flex; align-items: center; justify-content: space-between;
  }
  .lr-marca { display: flex; align-items: center; gap: .6rem; }
  .lr-marca-icono {
    width: 36px; height: 36px;
    background: var(--color-menta); border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
  }
  .lr-marca-nombre { font-family: 'DM Serif Display', serif; font-size: 1.4rem; color: var(--color-texto); }
  .lr-boton-nuevo {
    background: var(--color-menta); color: var(--color-fondo);
    border: none; border-radius: 12px;
    padding: .6rem 1.4rem; font-size: .9rem; font-weight: 600;
    font-family: 'DM Sans', sans-serif; cursor: pointer;
    transition: background .2s, box-shadow .2s;
    display: inline-flex; align-items: center; gap: .4rem;
    text-decoration: none;
  }
  .lr-boton-nuevo:hover { background: var(--color-menta-oscuro); box-shadow: 0 8px 24px rgba(45,212,191,.3); color: var(--color-fondo); }
  .lr-tarjeta {
    background: var(--color-tarjeta); border: 1px solid var(--color-borde);
    border-radius: 20px; max-width: 1100px; margin: 0 auto;
    padding: 2rem; box-shadow: 0 32px 80px rgba(0,0,0,.5);
    animation: lr-aparecer .5s ease both;
  }
  @keyframes lr-aparecer {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .lr-titulo { font-family: 'DM Serif Display', serif; font-size: 1.5rem; margin-bottom: 1.5rem; }
  .lr-table { color: var(--color-texto); border-collapse: collapse; width: 100%; }
  .lr-table thead th {
    background: var(--color-campo); color: var(--color-menta);
    border-bottom: 1px solid var(--color-borde);
    font-size: .82rem; text-transform: uppercase;
    letter-spacing: .05em; font-weight: 500; padding: .85rem 1rem; text-align: left;
  }
  .lr-table tbody tr { border-bottom: 1px solid var(--color-borde); transition: background .15s; }
  .lr-table tbody tr:hover { background: rgba(45,212,191,.05); }
  .lr-table tbody td { padding: .85rem 1rem; font-size: .9rem; vertical-align: middle; }
  .lr-vacio { text-align: center; color: var(--color-texto-suave); padding: 3rem !important; }
  .lr-alerta-error {
    background: rgba(244,114,106,.1); border: 1px solid var(--color-error);
    color: var(--color-error); border-radius: 12px;
    padding: 1rem 1.25rem; margin-bottom: 1.5rem;
  }
  .lr-badge-tomada {
    background: rgba(74,222,128,.15); color: var(--color-exito);
    border: 1px solid var(--color-exito); border-radius: 20px;
    padding: .2rem .7rem; font-size: .78rem; font-weight: 500;
  }
  .lr-badge-pendiente {
    background: rgba(244,114,106,.12); color: #fca5a5;
    border: 1px solid #fca5a5; border-radius: 20px;
    padding: .2rem .7rem; font-size: .78rem; font-weight: 500;
  }
  .lr-boton-tomada {
    background: var(--color-menta); color: var(--color-fondo);
    border: none; border-radius: 10px;
    padding: .45rem .9rem; font-size: .82rem; font-weight: 600;
    cursor: pointer; transition: background .2s, box-shadow .2s;
  }
  .lr-boton-tomada:hover { background: var(--color-menta-oscuro); box-shadow: 0 8px 20px rgba(45,212,191,.25); }
  .lr-alertas-flotantes {
    position: fixed; top: 1rem; right: 1rem;
    z-index: 9999; max-width: 350px;
  }
  .lr-alerta-retraso {
    background: rgba(244,114,106,.15);
    border: 1px solid #F4726A;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: .75rem;
    color: #F4726A;
    font-family: 'DM Sans', sans-serif;
    font-size: .88rem;
    box-shadow: 0 8px 24px rgba(0,0,0,.3);
    animation: lr-entrar .35s ease both;
  }
  @keyframes lr-entrar {
    from { opacity: 0; transform: translateX(40px); }
    to   { opacity: 1; transform: translateX(0); }
  }
  .lr-boton-retraso {
    margin-top: .5rem;
    background: #F4726A; color: white;
    border: none; border-radius: 8px;
    padding: .3rem .8rem; cursor: pointer; font-size: .82rem;
  }
  .table-responsive { overflow-x: auto; }
`;

const IconMedtrack = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
       strokeLinecap="round" strokeLinejoin="round"
       style={{ width: 20, height: 20, color: "var(--color-fondo)" }}>
    <path d="M12 8v4m0 4h.01M3 12a9 9 0 1 0 18 0A9 9 0 0 0 3 12z" />
  </svg>
);

const fechaHoraActual = () => {
  const a = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${a.getFullYear()}-${p(a.getMonth()+1)}-${p(a.getDate())} ${p(a.getHours())}:${p(a.getMinutes())}:${p(a.getSeconds())}`;
};

export default function ListaRecordatorios({ pacienteId, onNuevoRecordatorio }) {
  const [recordatorios, setRecordatorios] = useState([]);
  const [error,         setError]         = useState("");
  const [cargando,      setCargando]      = useState(true);
  const [retrasados,    setRetrasados]    = useState([]);

  const cargarPanelDia = useCallback(async () => {
    setError("");
    setCargando(true);
    if (!pacienteId) {
      setError("Falta el paciente. Selecciona uno desde la lista de pacientes.");
      setCargando(false);
      return;
    }
    try {
      const res = await api.obtenerPanelDiaPaciente(pacienteId);
      if (!res.ok) { setError("Error al cargar el panel del día."); return; }
      setRecordatorios(res.body.recordatorios || []);
    } catch {
      setError("No se pudo conectar con el servidor.");
    } finally {
      setCargando(false);
    }
  }, [pacienteId]);

  const verificarRetrasados = useCallback(async () => {
    if (!pacienteId) return;
    try {
      const res = await api.obtenerRecordatoriosRetrasados(pacienteId);
      if (res.ok && res.body.retrasados?.length) setRetrasados(res.body.retrasados);
    } catch { /* silencioso */ }
  }, [pacienteId]);

  useEffect(() => {
    cargarPanelDia();
    verificarRetrasados();
  }, [cargarPanelDia, verificarRetrasados]);

  const marcarComoTomada = async (pId, medId, recId, fechaProgramada) => {
    setError("");
    const datos = {
      paciente_id:     pId,      
      medicamento_id:  medId,    
      recordatorio_id: recId,    
      fecha_programada: fechaProgramada,
      fecha_hora_toma: fechaHoraActual(),
      estado: "tomada",
      observaciones: "Marcada desde el panel del día",
    };
    try {
      const res = await api.registrarToma(datos);
      const data = res.body;
      if (!res.ok) { setError(data.detail || "No se pudo registrar la toma."); return; }
      await cargarPanelDia();
    } catch {
      setError("No se pudo conectar con el servidor.");
    }
  };

  const marcarRetrasadoTomado = async (recId) => {
    try {
      const res = await api.marcarRecordatorioTomado(recId);
      if (res.ok) setRetrasados((prev) => prev.filter((r) => r.id !== recId));
    } catch { /* silencioso */ }
  };

  const renderFilas = () => {
    if (cargando) return (
      <tr><td className="lr-vacio" colSpan={7}>Cargando...</td></tr>
    );
    if (!recordatorios.length) return (
      <tr><td className="lr-vacio" colSpan={7}>No hay recordatorios para mostrar hoy.</td></tr>
    );
    return recordatorios.map((r, i) => (
      <tr key={r.recordatorio_id || i}>
        <td>{r.medicamento_nombre}</td>
        <td>{r.dosis || "—"}</td>
        <td>{r.hora_recordatorio}</td>
        <td>{r.fecha_programada}</td>
        <td>
          {r.tomada
            ? <span className="lr-badge-tomada">Tomada</span>
            : <span className="lr-badge-pendiente">Pendiente</span>}
        </td>
        <td>{r.observaciones || "—"}</td>
        <td>
          {r.tomada ? "—" : (
            <button
              className="lr-boton-tomada"
              onClick={() => marcarComoTomada(r.paciente_id, r.medicamento_id, r.recordatorio_id, r.fecha_programada)}
            >
              Marcar como tomada
            </button>
          )}
        </td>
      </tr>
    ));
  };

  return (
    <>
      <style>{estilos}</style>
      <div className="lr-alertas-flotantes">
        {retrasados.map((r) => (
          <div key={r.id} className="lr-alerta-retraso">
            <strong>⚠️ Medicamento no tomado</strong><br />
            <span style={{ color: "#E2EAF4" }}>{r.paciente}</span> debía tomar{" "}
            <strong>{r.medicamento_nombre}</strong> a las {r.hora_recordatorio}.
            <br />
            <button className="lr-boton-retraso" onClick={() => marcarRetrasadoTomado(r.id)}>
              Marcar como tomado
            </button>
          </div>
        ))}
      </div>
      <div className="lr-body">
        <div className="lr-encabezado">
          <div className="lr-marca">
            <div className="lr-marca-icono"><IconMedtrack /></div>
            <span className="lr-marca-nombre">MedTrack</span>
          </div>
          <button className="lr-boton-nuevo" onClick={onNuevoRecordatorio}>
            + Nuevo recordatorio
          </button>
        </div>
        <div className="lr-tarjeta">
          <h2 className="lr-titulo">Panel del día</h2>
          {error && <div className="lr-alerta-error">{error}</div>}
          <div className="table-responsive">
            <table className="lr-table">
              <thead>
                <tr>
                  <th>Medicamento</th><th>Dosis</th><th>Hora</th>
                  <th>Fecha programada</th><th>Estado</th>
                  <th>Observaciones</th><th>Acción</th>
                </tr>
              </thead>
              <tbody>{renderFilas()}</tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}
