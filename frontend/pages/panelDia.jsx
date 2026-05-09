import { useState, useEffect } from "react";

// ── Estilos ─────────────────────────────────────────────────────────────────
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
  }
  .pd-body {
    margin: 0; min-height: 100vh;
    background-color: var(--color-fondo);
    font-family: 'DM Sans', sans-serif; color: var(--color-texto);
    padding: 2rem 1rem;
    background-image:
      radial-gradient(ellipse 60% 50% at 80% 10%, rgba(45,212,191,.12) 0%, transparent 70%),
      radial-gradient(ellipse 40% 40% at 10% 80%, rgba(45,212,191,.07) 0%, transparent 60%);
  }
  .pd-contenedor { max-width: 800px; margin: 0 auto; }
  .pd-marca { display: flex; align-items: center; gap: .6rem; margin-bottom: 2rem; }
  .pd-marca-icono {
    width: 38px; height: 38px;
    background: var(--color-menta); border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
  }
  .pd-marca-nombre { font-family: 'DM Serif Display', serif; font-size: 1.45rem; color: var(--color-texto); }
  .pd-titulo { font-family: 'DM Serif Display', serif; font-size: 1.75rem; margin: 0 0 .25rem; }
  .pd-subtitulo { font-size: .88rem; color: var(--color-texto-suave); margin: 0 0 2rem; }
  .pd-paciente-card {
    background: var(--color-tarjeta); border: 1px solid var(--color-borde);
    border-radius: 14px; padding: 1.25rem 1.5rem; margin-bottom: 1.25rem;
  }
  .pd-paciente-nombre {
    font-family: 'DM Serif Display', serif; font-size: 1.1rem;
    margin: 0 0 1rem; color: var(--color-menta);
  }
  .pd-med-fila {
    display: flex; justify-content: space-between; align-items: center;
    padding: .6rem 0; border-bottom: 1px solid var(--color-borde); font-size: .9rem;
  }
  .pd-med-fila:last-child { border-bottom: none; }
  .pd-med-nombre { font-weight: 500; }
  .pd-med-detalle { color: var(--color-texto-suave); font-size: .82rem; }
  .pd-med-hora {
    background: rgba(45,212,191,.12); color: var(--color-menta);
    border: 1px solid rgba(45,212,191,.3); border-radius: 20px;
    padding: .2rem .75rem; font-size: .8rem;
  }
  .pd-alerta-error {
    background: rgba(244,114,106,.1); border: 1px solid var(--color-error);
    color: var(--color-error); border-radius: 12px;
    padding: 1rem 1.25rem; margin-bottom: 1.5rem;
  }
  .pd-vacio { text-align: center; color: var(--color-texto-suave); padding: 3rem; font-size: .92rem; }
`;

const IconMedtrack = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
       strokeLinecap="round" strokeLinejoin="round"
       style={{ width: 22, height: 22, color: "var(--color-fondo)" }}>
    <path d="M12 8v4m0 4h.01M3 12a9 9 0 1 0 18 0A9 9 0 0 0 3 12z" />
  </svg>
);

// ── Componente principal ────────────────────────────────────────────────────
export default function PanelDia() {
  /*
    Este componente no requiere props adicionales: obtiene los datos del
    panel del día directamente desde el backend al montarse.
    El endpoint /panel-dia devuelve todos los pacientes con sus medicamentos
    del día, por lo que no necesita un paciente_id específico.
  */
  const [panel,    setPanel]    = useState([]);
  const [error,    setError]    = useState("");
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const cargar = async () => {
      setCargando(true);
      setError("");
      try {
        // Equivalente al api.obtenerPanelDia() del HTML original
        const res = await fetch("http://localhost:8000/panel-dia");
        const datos = await res.json();
        if (!res.ok) { setError("Error al cargar el panel del día."); return; }
        setPanel(datos.panel || []);
      } catch {
        setError("No se pudo conectar con el servidor.");
      } finally {
        setCargando(false);
      }
    };
    cargar();
  }, []);

  // Fecha de hoy formateada
  const fechaHoy = new Date().toLocaleDateString("es-CO", {
    weekday: "long", year: "numeric", month: "long", day: "numeric",
  });

  const renderContenido = () => {
    if (cargando) return <div className="pd-vacio">Cargando...</div>;
    if (!panel.length) return <div className="pd-vacio">No hay medicamentos programados para hoy.</div>;
    return panel.map((paciente, i) => (
      <div key={i} className="pd-paciente-card">
        <p className="pd-paciente-nombre">{paciente.nombres} {paciente.apellidos}</p>
        {paciente.medicamentos.map((med, j) => (
          <div key={j} className="pd-med-fila">
            <div>
              <div className="pd-med-nombre">{med.medicamento}</div>
              <div className="pd-med-detalle">{med.dosis}</div>
            </div>
            <span className="pd-med-hora">{med.hora}</span>
          </div>
        ))}
      </div>
    ));
  };

  return (
    <>
      <style>{estilos}</style>
      <div className="pd-body">
        <div className="pd-contenedor">
          <div className="pd-marca">
            <div className="pd-marca-icono"><IconMedtrack /></div>
            <span className="pd-marca-nombre">MedTrack</span>
          </div>
          <h1 className="pd-titulo">Panel del día</h1>
          <p className="pd-subtitulo">{fechaHoy}</p>
          {error && <div className="pd-alerta-error">{error}</div>}
          <div>{renderContenido()}</div>
        </div>
      </div>
    </>
  );
}