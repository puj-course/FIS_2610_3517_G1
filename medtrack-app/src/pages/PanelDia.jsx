import { useState, useEffect } from "react";
import api from "../api";

const estilos = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
  :root {
    --color-menta: #2DD4BF;
    --color-fondo: #0F1B2D;
    --color-campo: #1E2D3D;
    --color-tarjeta: #162030;
    --color-borde: #243447;
    --color-texto: #E2EAF4;
    --color-texto-suave: #7A95B0;
    --color-error: #F4726A;
    --color-exito: #4ADE80;
  }
  .pd-body {
    margin: 0; min-height: 100vh; background-color: var(--color-fondo);
    font-family: 'DM Sans', sans-serif; color: var(--color-texto); padding: 2rem 1rem;
    background-image:
      radial-gradient(ellipse 60% 50% at 80% 10%, rgba(45,212,191,.12) 0%, transparent 70%),
      radial-gradient(ellipse 40% 40% at 10% 80%, rgba(45,212,191,.07) 0%, transparent 60%);
  }
  .pd-contenedor { max-width: 800px; margin: 0 auto; }
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
  .pd-med-derecha { display: flex; align-items: center; gap: .75rem; }
  .pd-med-hora {
    background: rgba(45,212,191,.12); color: var(--color-menta);
    border: 1px solid rgba(45,212,191,.3); border-radius: 20px;
    padding: .2rem .75rem; font-size: .8rem;
  }
  .pd-badge-tomado {
    background: rgba(74,222,128,.12); color: var(--color-exito);
    border: 1px solid rgba(74,222,128,.3); border-radius: 20px;
    padding: .2rem .75rem; font-size: .78rem; font-weight: 600;
  }
  .pd-badge-pendiente {
    background: rgba(251,191,36,.12); color: #FBBF24;
    border: 1px solid rgba(251,191,36,.3); border-radius: 20px;
    padding: .2rem .75rem; font-size: .78rem; font-weight: 600;
  }
  .pd-alerta-error {
    background: rgba(244,114,106,.1); border: 1px solid var(--color-error);
    color: var(--color-error); border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1.5rem;
  }
  .pd-vacio { text-align: center; color: var(--color-texto-suave); padding: 3rem; font-size: .92rem; }
`;

export default function PanelDia() {
  const [panel,    setPanel]    = useState([]);
  const [error,    setError]    = useState("");
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const cargar = async () => {
      setCargando(true);
      setError("");
      try {
        const res = await api.obtenerPanelCompleto();
        if (!res.ok) { setError("Error al cargar el panel del día."); return; }
        setPanel(res.body.panel || []);
      } catch {
        setError("No se pudo conectar con el servidor.");
      } finally {
        setCargando(false);
      }
    };
    cargar();
  }, []);

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
            <div className="pd-med-derecha">
              <span className="pd-med-hora">{med.hora}</span>
              {med.tomado
                ? <span className="pd-badge-tomado">✓ Tomado</span>
                : <span className="pd-badge-pendiente">Pendiente</span>
              }
            </div>
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
          <h1 className="pd-titulo">Panel del día</h1>
          <p className="pd-subtitulo">{fechaHoy}</p>
          {error && <div className="pd-alerta-error">{error}</div>}
          <div>{renderContenido()}</div>
        </div>
      </div>
    </>
  );
}