import { useState, useEffect, useRef } from "react";
import api from "../api";

const estilos = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
  :root {
    --color-menta: #2DD4BF; --color-fondo: #0F1B2D; --color-campo: #1E2D3D;
    --color-tarjeta: #162030; --color-borde: #243447; --color-texto: #E2EAF4;
    --color-texto-suave: #7A95B0; --color-error: #F4726A; --color-exito: #4ADE80; --color-alerta: #FBBF24;
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
  .pd-alertas-ctn { margin-bottom: 1.5rem; display: flex; flex-direction: column; gap: .6rem; }
  .pd-alerta-banner {
    border-radius: 12px; padding: .85rem 1.1rem; font-size: .88rem;
    display: flex; align-items: flex-start; gap: .75rem;
    animation: pd-slide-in .3s ease both;
  }
  @keyframes pd-slide-in { from { opacity:0; transform: translateY(-8px); } to { opacity:1; transform: translateY(0); } }
  .pd-alerta-banner.recordatorio { background: rgba(251,191,36,.1); border: 1px solid rgba(251,191,36,.4); color: var(--color-alerta); }
  .pd-alerta-banner.perdida { background: rgba(244,114,106,.1); border: 1px solid rgba(244,114,106,.4); color: var(--color-error); }
  .pd-alerta-icono { font-size: 1.1rem; flex-shrink: 0; margin-top: .05rem; }
  .pd-alerta-texto strong { display: block; font-weight: 600; margin-bottom: .1rem; }
  .pd-alerta-cerrar { margin-left: 1rem; background: none; border: none; color: inherit; cursor: pointer; font-size: .8rem; opacity: .7; }
  .pd-paciente-card {
    background: var(--color-tarjeta); border: 1px solid var(--color-borde);
    border-radius: 14px; padding: 1.25rem 1.5rem; margin-bottom: 1.25rem;
  }
  .pd-paciente-nombre { font-family: 'DM Serif Display', serif; font-size: 1.1rem; margin: 0 0 1rem; color: var(--color-menta); }
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
    border: 1px solid rgba(45,212,191,.3); border-radius: 20px; padding: .2rem .75rem; font-size: .8rem;
  }
  .pd-med-hora.pronto { background: rgba(251,191,36,.15); color: var(--color-alerta); border-color: rgba(251,191,36,.4); }
  .pd-badge-tomado { background: rgba(74,222,128,.12); color: var(--color-exito); border: 1px solid rgba(74,222,128,.3); border-radius: 20px; padding: .2rem .75rem; font-size: .78rem; font-weight: 600; }
  .pd-badge-pendiente { background: rgba(251,191,36,.12); color: #FBBF24; border: 1px solid rgba(251,191,36,.3); border-radius: 20px; padding: .2rem .75rem; font-size: .78rem; font-weight: 600; }
  .pd-badge-alerta { background: rgba(244,114,106,.12); color: var(--color-error); border: 1px solid rgba(244,114,106,.3); border-radius: 20px; padding: .2rem .75rem; font-size: .78rem; font-weight: 600; }
  .pd-alerta-error { background: rgba(244,114,106,.1); border: 1px solid var(--color-error); color: var(--color-error); border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1.5rem; }
  .pd-vacio { text-align: center; color: var(--color-texto-suave); padding: 3rem; font-size: .92rem; }
`;

function horaAMinutos(hora) {
  const [h, m] = hora.split(':').map(Number);
  return h * 60 + m;
}
function minutosAhora() {
  const n = new Date();
  return n.getHours() * 60 + n.getMinutes();
}

export default function PanelDia() {
  const [panel,    setPanel]    = useState([]);
  const [error,    setError]    = useState("");
  const [cargando, setCargando] = useState(true);
  const [alertas,  setAlertas]  = useState([]);
  const disparadas = useRef(new Set());

  useEffect(() => {
    (async () => {
      setCargando(true); setError("");
      try {
        const res = await api.obtenerPanelCompleto();
        if (!res.ok) {
          setError("Error al cargar el panel del día: " + JSON.stringify(res.body));
          return;
        }
        setPanel(res.body.panel || []);
      } catch (e) {
        setError("No se pudo conectar con el servidor.");
      } finally {
        setCargando(false);
      }
    })();
  }, []);

  useEffect(() => {
    if (!panel.length) return;
    function revisar() {
      const ahora = minutosAhora();
      const nuevas = [];
      panel.forEach(paciente => {
        (paciente.medicamentos || []).forEach(med => {
          if (med.tomado) return;
          const horaMin = horaAMinutos(med.hora);
          const diff = horaMin - ahora;
          const k15 = `rec_${paciente.nombres}_${med.medicamento}_${med.hora}`;
          const k5  = `per_${paciente.nombres}_${med.medicamento}_${med.hora}`;

          if (diff >= 13 && diff <= 16 && !disparadas.current.has(k15)) {
            disparadas.current.add(k15);
            nuevas.push({ id: k15, tipo: 'recordatorio', paciente: `${paciente.nombres} ${paciente.apellidos}`, medicamento: med.medicamento, hora: med.hora, minutos: diff });
          }

          if (diff <= -5 && !disparadas.current.has(k5)) {
            disparadas.current.add(k5);
            nuevas.push({ id: k5, tipo: 'perdida', paciente: `${paciente.nombres} ${paciente.apellidos}`, medicamento: med.medicamento, hora: med.hora });
          }
        });
      });
      if (nuevas.length) {
        setAlertas(prev => [...prev, ...nuevas]);
        nuevas.forEach(a => {
          if (a.tipo === 'recordatorio')
            setTimeout(() => setAlertas(prev => prev.filter(x => x.id !== a.id)), 15 * 60 * 1000);
        });
      }
    }
    revisar();
    const t = setInterval(revisar, 30000);
    return () => clearInterval(t);
  }, [panel]);

  const fechaHoy = new Date().toLocaleDateString("es-CO", { weekday: "long", year: "numeric", month: "long", day: "numeric" });

  function badgeEstado(med) {
    if (med.tomado) return <span className="pd-badge-tomado">✓ Tomado</span>;
    const diff = horaAMinutos(med.hora) - minutosAhora();
    if (diff < -5) return <span className="pd-badge-alerta">⚠ No tomado</span>;
    return <span className="pd-badge-pendiente">Pendiente</span>;
  }

  function claseHora(med) {
    if (med.tomado) return 'pd-med-hora';
    const diff = horaAMinutos(med.hora) - minutosAhora();
    return diff >= 0 && diff <= 15 ? 'pd-med-hora pronto' : 'pd-med-hora';
  }

  return (
    <>
      <style>{estilos}</style>
      <div className="pd-body">
        <div className="pd-contenedor">
          <h1 className="pd-titulo">Panel del día</h1>
          <p className="pd-subtitulo">{fechaHoy}</p>

          {alertas.length > 0 && (
            <div className="pd-alertas-ctn">
              {alertas.map(a => (
                <div key={a.id} className={`pd-alerta-banner ${a.tipo}`}>
                  <span className="pd-alerta-icono">{a.tipo === 'recordatorio' ? '🔔' : '⚠️'}</span>
                  <div className="pd-alerta-texto">
                    {a.tipo === 'recordatorio' ? (
                      <><strong>Recordatorio — {a.paciente}</strong>En {a.minutos} min: {a.medicamento} a las {a.hora}</>
                    ) : (
                      <><strong>Toma no registrada — {a.paciente}</strong>{a.medicamento} debía tomarse a las {a.hora} y no se ha registrado.</>
                    )}
                    <button className="pd-alerta-cerrar" onClick={() => setAlertas(prev => prev.filter(x => x.id !== a.id))}>✕ cerrar</button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {error && <div className="pd-alerta-error">{error}</div>}

          {cargando && <div className="pd-vacio">Cargando...</div>}
          {!cargando && !panel.length && <div className="pd-vacio">No hay medicamentos programados para hoy.</div>}
          {!cargando && panel.map((paciente, i) => (
            <div key={i} className="pd-paciente-card">
              <p className="pd-paciente-nombre">{paciente.nombres} {paciente.apellidos}</p>
              {paciente.medicamentos.map((med, j) => (
                <div key={j} className="pd-med-fila">
                  <div>
                    <div className="pd-med-nombre">{med.medicamento}</div>
                    <div className="pd-med-detalle">{med.dosis}</div>
                  </div>
                  <div className="pd-med-derecha">
                    <span className={claseHora(med)}>{med.hora}</span>
                    {badgeEstado(med)}
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}