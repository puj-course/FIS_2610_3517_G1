import { useState, useEffect, useCallback } from "react";
import api from "../api";  

const estilos = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
  :root {
    --color-menta: #2DD4BF; --color-menta-oscuro: #0F9D8A;
    --color-fondo: #0F1B2D; --color-campo: #1E2D3D; --color-tarjeta: #162030;
    --color-borde: #243447; --color-texto: #E2EAF4; --color-texto-suave: #7A95B0;
    --color-error: #F4726A; --color-exito: #4ADE80; --color-alerta: #FBBF24;
  }
  .lt-body {
    margin: 0; min-height: 100vh;
    background-color: var(--color-fondo);
    font-family: 'DM Sans', sans-serif; color: var(--color-texto);
    padding: 2rem 1rem;
    background-image:
      radial-gradient(ellipse 60% 50% at 80% 10%, rgba(45,212,191,.12) 0%, transparent 70%),
      radial-gradient(ellipse 40% 40% at 10% 80%, rgba(45,212,191,.07) 0%, transparent 60%);
  }
  .lt-encabezado { max-width: 1100px; margin: 0 auto 2rem; display: flex; align-items: center; justify-content: space-between; }
  .lt-marca { display: flex; align-items: center; gap: .6rem; }
  .lt-marca-icono { width: 36px; height: 36px; background: var(--color-menta); border-radius: 10px; display: flex; align-items: center; justify-content: center; }
  .lt-marca-nombre { font-family: 'DM Serif Display', serif; font-size: 1.4rem; color: var(--color-texto); }
  .lt-tarjeta { background: var(--color-tarjeta); border: 1px solid var(--color-borde); border-radius: 20px; max-width: 1100px; margin: 0 auto; padding: 2rem; box-shadow: 0 32px 80px rgba(0,0,0,.5); animation: lt-aparecer .5s ease both; }
  @keyframes lt-aparecer { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
  .lt-titulo { font-family: 'DM Serif Display', serif; font-size: 1.5rem; margin-bottom: .5rem; }
  .lt-subtitulo { color: var(--color-texto-suave); font-size: .9rem; margin-bottom: 1.5rem; }
  .lt-table { color: var(--color-texto); border-collapse: collapse; width: 100%; }
  .lt-table thead th { background: var(--color-campo); color: var(--color-menta); border-bottom: 1px solid var(--color-borde); font-size: .82rem; text-transform: uppercase; letter-spacing: .05em; font-weight: 500; padding: .85rem 1rem; text-align: left; }
  .lt-table tbody tr { border-bottom: 1px solid var(--color-borde); transition: background .15s; }
  .lt-table tbody tr:hover { background: rgba(45,212,191,.05); }
  .lt-table tbody td { padding: .85rem 1rem; font-size: .9rem; vertical-align: middle; }
  .lt-vacio { text-align: center; color: var(--color-texto-suave); padding: 3rem !important; }
  .lt-alerta-error { background: rgba(244,114,106,.1); border: 1px solid var(--color-error); color: var(--color-error); border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1.5rem; }
  .lt-badge-pendiente { background: rgba(251,191,36,.15); color: var(--color-alerta); border: 1px solid var(--color-alerta); border-radius: 20px; padding: .2rem .7rem; font-size: .78rem; font-weight: 500; }
  .lt-badge-tomado { background: rgba(74,222,128,.15); color: var(--color-exito); border: 1px solid var(--color-exito); border-radius: 20px; padding: .2rem .7rem; font-size: .78rem; font-weight: 500; }
  .lt-badge-atrasado { background: rgba(244,114,106,.15); color: var(--color-error); border: 1px solid var(--color-error); border-radius: 20px; padding: .2rem .7rem; font-size: .78rem; font-weight: 500; }
  .lt-boton-tomar { background: var(--color-menta); color: var(--color-fondo); border: none; border-radius: 8px; padding: .3rem .8rem; font-size: .82rem; font-weight: 600; font-family: 'DM Sans', sans-serif; cursor: pointer; transition: background .2s; }
  .lt-boton-tomar:hover { background: var(--color-menta-oscuro); }
  .lt-boton-tomar:disabled { background: var(--color-campo); color: var(--color-texto-suave); cursor: not-allowed; }
  .lt-notificaciones { position: fixed; top: 1.5rem; right: 1.5rem; z-index: 9999; }
  .lt-notif { background: var(--color-tarjeta); border: 1px solid var(--color-exito); border-radius: 12px; padding: .9rem 1.2rem; display: flex; align-items: center; gap: .75rem; box-shadow: 0 8px 32px rgba(0,0,0,.4); animation: lt-deslizar .35s ease both; font-size: .88rem; margin-bottom: .5rem; color: var(--color-texto); }
  .lt-notif.error { border-color: var(--color-error); }
  @keyframes lt-deslizar { from { opacity: 0; transform: translateX(40px); } to { opacity: 1; transform: translateX(0); } }
  .table-responsive { overflow-x: auto; }
`;

const IconMedtrack = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
       strokeLinecap="round" strokeLinejoin="round"
       style={{ width: 20, height: 20, color: "var(--color-fondo)" }}>
    <path d="M12 8v4m0 4h.01M3 12a9 9 0 1 0 18 0A9 9 0 0 0 3 12z" />
  </svg>
);

const BadgeEstado = ({ estado }) => {
  if (estado === "tomado" || estado === "a_tiempo") return <span className="lt-badge-tomado">Tomado</span>;
  if (estado === "atrasado" || estado === "tarde")   return <span className="lt-badge-atrasado">Atrasado</span>;
  return <span className="lt-badge-pendiente">Pendiente</span>;
};

export default function ListaTomas({ pacienteId, nombrePaciente = "Paciente" }) {
  const hoy = new Date().toISOString().split("T")[0];
  const [tomas,          setTomas]          = useState([]);
  const [error,          setError]          = useState("");
  const [cargando,       setCargando]       = useState(true);
  const [notificaciones, setNotificaciones] = useState([]);

  const mostrarNotificacion = (mensaje, tipo = "exito") => {
    const id = Date.now();
    setNotificaciones((prev) => [...prev, { id, mensaje, tipo }]);
    setTimeout(() => setNotificaciones((prev) => prev.filter((n) => n.id !== id)), 3500);
  };

  const cargarTomas = useCallback(async () => {
    setError(""); setCargando(true);
    if (!pacienteId) { setError("No se recibió un paciente seleccionado."); setCargando(false); return; }
    try {
      // ✅ usa api.obtenerTomas — sin fetch directo
      const res = await api.obtenerTomas(pacienteId, hoy);
      if (!res.ok) { setError("Error al cargar las tomas."); return; }
      setTomas(res.body.tomas || res.body || []);
    } catch {
      setError("No se pudo conectar con el servidor.");
    } finally {
      setCargando(false);
    }
  }, [pacienteId, hoy]);

  useEffect(() => { cargarTomas(); }, [cargarTomas]);

  const marcarComoTomado = async (medicamentoId, horaProgramada) => {
    const ahora = new Date();
    const horaActual = ahora.toTimeString().slice(0, 5);
    const datos = {
      medicamento_id: medicamentoId,  // ✅ string ObjectId, no parseInt
      paciente_id:    pacienteId,     // ✅ string ObjectId
      fecha:          hoy,
      hora_programada: horaProgramada,
      hora_tomada:    horaActual,
      estado:         "tomado",
      observaciones:  "Toma registrada desde la interfaz",
    };
    try {
      // ✅ usa api.registrarToma
      const res = await api.registrarToma(datos);
      if (res.ok) {
        mostrarNotificacion("Toma marcada como tomada correctamente.");
        cargarTomas();
      } else {
        mostrarNotificacion("Error al registrar la toma.", "error");
      }
    } catch {
      mostrarNotificacion("Error de conexión con el servidor.", "error");
    }
  };

  const fechaFormateada = new Date().toLocaleDateString("es-CO", {
    weekday: "long", year: "numeric", month: "long", day: "numeric",
  });

  const renderFilas = () => {
    if (cargando) return <tr><td className="lt-vacio" colSpan={6}>Cargando...</td></tr>;
    if (!tomas.length) return <tr><td className="lt-vacio" colSpan={6}>No hay tomas registradas para hoy.</td></tr>;
    return tomas.map((t, i) => {
      const esTomado = t.estado === "tomado" || t.estado === "a_tiempo";
      return (
        <tr key={t.id || i}>
          <td>{t.medicamento_nombre || t.medicamento_id}</td>
          <td>{t.hora_programada || "—"}</td>
          <td>{t.hora_tomada || "—"}</td>
          <td><BadgeEstado estado={t.estado} /></td>
          <td>{t.observaciones || "—"}</td>
          <td>
            <button
              className="lt-boton-tomar"
              disabled={esTomado}
              onClick={() => marcarComoTomado(t.medicamento_id, t.hora_programada || hoy)}
            >
              {esTomado ? "Tomado ✓" : "Marcar tomado"}
            </button>
          </td>
        </tr>
      );
    });
  };

  return (
    <>
      <style>{estilos}</style>
      <div className="lt-notificaciones">
        {notificaciones.map((n) => (
          <div key={n.id} className={`lt-notif${n.tipo === "error" ? " error" : ""}`}>
            <span>{n.tipo === "exito" ? "✓" : "⚠"}</span>
            <span>{n.mensaje}</span>
          </div>
        ))}
      </div>
      <div className="lt-body">
        <div className="lt-encabezado">
          <div className="lt-marca">
            <div className="lt-marca-icono"><IconMedtrack /></div>
            <span className="lt-marca-nombre">MedTrack</span>
          </div>
        </div>
        <div className="lt-tarjeta">
          <h2 className="lt-titulo">Tomas del día</h2>
          <p className="lt-subtitulo">Paciente: {nombrePaciente} — {fechaFormateada}</p>
          {error && <div className="lt-alerta-error">{error}</div>}
          <div className="table-responsive">
            <table className="lt-table">
              <thead>
                <tr>
                  <th>Medicamento</th><th>Hora programada</th><th>Hora tomada</th>
                  <th>Estado</th><th>Observaciones</th><th>Acción</th>
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
