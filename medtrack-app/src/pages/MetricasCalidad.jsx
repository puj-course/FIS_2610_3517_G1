import { useState } from 'react';
import api from '../api';

const escenarioValido = {
  objetivo_ms: 300,
  pacientes: [
    {
      id: 'pac-1',
      paciente_id: 'pac-1',
      nombres: 'Ana',
      numero_documento: '100200300',
    },
  ],
  medicamentos: [
    {
      id: 'med-1',
      medicamento_id: 'med-1',
      nombre: 'Losartan',
      dosis: '50 mg',
      frecuencia: 'Diaria',
      paciente_id: 'pac-1',
    },
  ],
  recordatorios: [
    {
      id: 'rec-1',
      recordatorio_id: 'rec-1',
      paciente_id: 'pac-1',
      medicamento_id: 'med-1',
      hora_programada: '08:00',
      frecuencia: 'Diaria',
    },
  ],
  tomas: [
    {
      id: 'toma-1',
      toma_id: 'toma-1',
      paciente_id: 'pac-1',
      medicamento_id: 'med-1',
      recordatorio_id: 'rec-1',
      estado: 'tomada',
    },
  ],
};

const escenarioInvalido = {
  objetivo_ms: 300,
  pacientes: [
    {
      id: 'pac-1',
      paciente_id: 'pac-1',
      nombres: 'Ana',
      numero_documento: '100200300',
    },
  ],
  medicamentos: [
    {
      id: 'med-1',
      medicamento_id: 'med-1',
      nombre: 'Losartan',
      dosis: '50 mg',
      frecuencia: 'Diaria',
      paciente_id: 'pac-1',
    },
  ],
  recordatorios: [
    {
      id: 'rec-1',
      recordatorio_id: 'rec-1',
      paciente_id: 'm1',
      medicamento_id: '0',
      hora_programada: '08:00',
      frecuencia: 'Diaria',
    },
  ],
  tomas: [
    {
      id: 'toma-1',
      toma_id: 'toma-1',
      paciente_id: 'pac-2',
      medicamento_id: 'med-1',
      recordatorio_id: 'rec-1',
      estado: 'tomada',
    },
  ],
};

const estilos = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600;700&display=swap');
  :root {
    --mc-fondo: #0F1B2D;
    --mc-panel: #162030;
    --mc-panel-2: #1E2D3D;
    --mc-borde: #243447;
    --mc-texto: #E2EAF4;
    --mc-suave: #8BA4BC;
    --mc-menta: #2DD4BF;
    --mc-verde: #4ADE80;
    --mc-amarillo: #FBBF24;
    --mc-rojo: #F4726A;
    --mc-azul: #60A5FA;
  }
  .mc-page {
    min-height: 100vh;
    background: var(--mc-fondo);
    color: var(--mc-texto);
    font-family: 'DM Sans', sans-serif;
    padding: 2rem;
  }
  .mc-wrap { max-width: 1180px; margin: 0 auto; }
  .mc-header { display: flex; justify-content: space-between; gap: 1rem; align-items: flex-end; margin-bottom: 1.5rem; }
  .mc-title { font-family: 'DM Serif Display', serif; font-size: 2rem; margin: 0; letter-spacing: 0; }
  .mc-subtitle { color: var(--mc-suave); font-size: .92rem; margin: .25rem 0 0; max-width: 780px; }
  .mc-gate {
    border: 1px solid var(--mc-borde);
    background: var(--mc-panel);
    border-radius: 8px;
    padding: .8rem 1rem;
    min-width: 230px;
  }
  .mc-gate.ok { border-color: rgba(74,222,128,.55); }
  .mc-gate.fail { border-color: rgba(244,114,106,.55); }
  .mc-gate-label { color: var(--mc-suave); font-size: .74rem; text-transform: uppercase; letter-spacing: .08em; }
  .mc-gate-value { margin-top: .2rem; font-size: 1.05rem; font-weight: 700; }
  .mc-gate.ok .mc-gate-value { color: var(--mc-verde); }
  .mc-gate.fail .mc-gate-value { color: var(--mc-rojo); }
  .mc-actions { display: flex; flex-wrap: wrap; gap: .75rem; margin: 1.25rem 0; }
  .mc-btn {
    border: 1px solid rgba(45,212,191,.35);
    background: rgba(45,212,191,.12);
    color: var(--mc-texto);
    border-radius: 8px;
    padding: .65rem .9rem;
    font: inherit;
    font-size: .88rem;
    cursor: pointer;
  }
  .mc-btn:hover { border-color: var(--mc-menta); color: var(--mc-menta); }
  .mc-btn.secondary { background: transparent; border-color: var(--mc-borde); color: var(--mc-suave); }
  .mc-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; margin-bottom: 1.25rem; }
  .mc-card {
    background: var(--mc-panel);
    border: 1px solid var(--mc-borde);
    border-radius: 8px;
    padding: 1.15rem;
    min-height: 270px;
    display: flex;
    flex-direction: column;
    gap: .8rem;
  }
  .mc-card-head { display: flex; justify-content: space-between; gap: .8rem; align-items: flex-start; }
  .mc-card-title { margin: 0; font-size: .96rem; font-weight: 700; line-height: 1.25; }
  .mc-level {
    border-radius: 999px;
    border: 1px solid var(--mc-borde);
    padding: .18rem .55rem;
    font-size: .76rem;
    flex-shrink: 0;
  }
  .mc-level.bueno { color: var(--mc-verde); border-color: rgba(74,222,128,.45); background: rgba(74,222,128,.1); }
  .mc-level.aceptable { color: var(--mc-amarillo); border-color: rgba(251,191,36,.45); background: rgba(251,191,36,.1); }
  .mc-level.deficiente { color: var(--mc-rojo); border-color: rgba(244,114,106,.45); background: rgba(244,114,106,.1); }
  .mc-percent { font-size: 2.5rem; font-weight: 700; line-height: 1; color: var(--mc-menta); }
  .mc-meta { color: var(--mc-suave); font-size: .85rem; line-height: 1.45; margin: 0; }
  .mc-detail { display: grid; gap: .45rem; margin-top: auto; }
  .mc-detail-row { display: flex; justify-content: space-between; gap: .75rem; color: var(--mc-suave); font-size: .82rem; border-top: 1px solid rgba(36,52,71,.75); padding-top: .45rem; }
  .mc-detail-row strong { color: var(--mc-texto); font-weight: 600; }
  .mc-lab {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 360px;
    gap: 1rem;
    align-items: start;
  }
  .mc-panel {
    background: var(--mc-panel);
    border: 1px solid var(--mc-borde);
    border-radius: 8px;
    padding: 1rem;
  }
  .mc-panel-title { margin: 0 0 .75rem; font-size: 1rem; }
  .mc-textarea {
    width: 100%;
    min-height: 420px;
    resize: vertical;
    border: 1px solid var(--mc-borde);
    border-radius: 8px;
    background: #0B1422;
    color: var(--mc-texto);
    padding: .9rem;
    font-family: Consolas, 'Courier New', monospace;
    font-size: .82rem;
    line-height: 1.45;
    box-sizing: border-box;
  }
  .mc-error {
    border: 1px solid rgba(244,114,106,.55);
    background: rgba(244,114,106,.1);
    color: var(--mc-rojo);
    border-radius: 8px;
    padding: .8rem 1rem;
    margin-bottom: 1rem;
  }
  .mc-rules { display: grid; gap: .65rem; }
  .mc-rule {
    border: 1px solid rgba(244,114,106,.35);
    border-radius: 8px;
    background: rgba(244,114,106,.08);
    padding: .75rem;
  }
  .mc-rule-name { margin: 0 0 .25rem; font-size: .86rem; color: var(--mc-rojo); font-weight: 700; }
  .mc-rule-info { margin: 0; color: var(--mc-suave); font-size: .8rem; line-height: 1.4; overflow-wrap: anywhere; }
  .mc-empty { color: var(--mc-suave); font-size: .9rem; margin: 0; }
  @media (max-width: 1020px) {
    .mc-header { align-items: stretch; flex-direction: column; }
    .mc-grid { grid-template-columns: 1fr; }
    .mc-lab { grid-template-columns: 1fr; }
  }
  @media (max-width: 640px) {
    .mc-page { padding: 1rem; }
    .mc-title { font-size: 1.6rem; }
    .mc-percent { font-size: 2.15rem; }
    .mc-actions { flex-direction: column; }
    .mc-btn { width: 100%; }
  }
`;

function formatearJson(valor) {
  return JSON.stringify(valor, null, 2);
}

function claseNivel(nivel) {
  return String(nivel || '').toLowerCase();
}

function porcentaje(valor) {
  if (typeof valor !== 'number') return '0.0%';
  return `${valor.toFixed(1)}%`;
}

function MetricCard({ titulo, metrica, detalleExtra, afectada }) {
  const nivel = metrica?.nivel || 'Sin datos';

  return (
    <article className="mc-card">
      <div className="mc-card-head">
        <h2 className="mc-card-title">{titulo}</h2>
        <span className={`mc-level ${claseNivel(nivel)}`}>{nivel}</span>
      </div>
      <div className="mc-percent">{porcentaje(metrica?.porcentaje)}</div>
      <p className="mc-meta">{metrica?.que_mide || 'Pendiente de evaluar.'}</p>
      <p className="mc-meta">{metrica?.que_hace_que_cambie || 'Ejecuta una evaluacion para ver el resultado.'}</p>
      <div className="mc-detail">
        {detalleExtra}
        <div className="mc-detail-row">
          <span>Quality gate</span>
          <strong>{afectada ? 'Lo bloquea' : 'No lo bloquea'}</strong>
        </div>
      </div>
    </article>
  );
}

export default function MetricasCalidad() {
  const [reporte, setReporte] = useState(null);
  const [jsonEscenario, setJsonEscenario] = useState(formatearJson(escenarioValido));
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);

  const metricas = reporte?.resumen_metricas || {};
  const afectadas = reporte?.notificacion?.metricas_afectadas || [];
  const reglasFallidas = metricas.cumplimiento_reglas_negocio?.reglas_fallidas || [];

  async function aplicarRespuesta(peticion) {
    setCargando(true);
    setError('');
    try {
      const respuesta = await peticion();
      if (!respuesta.ok) {
        setError(`No se pudo evaluar: ${JSON.stringify(respuesta.body)}`);
        return;
      }
      setReporte(respuesta.body);
    } catch (e) {
      setError('No se pudo conectar con el backend.');
    } finally {
      setCargando(false);
    }
  }

  function cargarEscenario(valor) {
    setJsonEscenario(formatearJson(valor));
    setError('');
  }

  function evaluarActuales() {
    aplicarRespuesta(() => api.obtenerMetricasCalidad());
  }

  function evaluarJson() {
    let payload;
    try {
      payload = JSON.parse(jsonEscenario);
    } catch (e) {
      setError('El JSON no es valido.');
      return;
    }
    aplicarRespuesta(() => api.evaluarMetricasCalidad(payload));
  }

  return (
    <>
      <style>{estilos}</style>
      <div className="mc-page">
        <div className="mc-wrap">
          <header className="mc-header">
            <div>
              <h1 className="mc-title">Metricas de calidad</h1>
              <p className="mc-subtitle">
                Evaluacion integrada de completitud, coherencia de negocio y rendimiento del backend real de MedTrack.
              </p>
            </div>
            <div className={`mc-gate ${reporte ? (reporte.quality_gate_aprobado ? 'ok' : 'fail') : ''}`}>
              <div className="mc-gate-label">Quality gate</div>
              <div className="mc-gate-value">
                {reporte ? reporte.estado_general : 'Sin evaluar'}
              </div>
            </div>
          </header>

          <div className="mc-actions">
            <button className="mc-btn" type="button" onClick={evaluarActuales} disabled={cargando}>
              Evaluar datos actuales del sistema
            </button>
            <button className="mc-btn secondary" type="button" onClick={() => cargarEscenario(escenarioValido)}>
              Cargar escenario valido
            </button>
            <button className="mc-btn secondary" type="button" onClick={() => cargarEscenario(escenarioInvalido)}>
              Cargar escenario con dato incorrecto
            </button>
            <button className="mc-btn" type="button" onClick={evaluarJson} disabled={cargando}>
              Evaluar JSON
            </button>
          </div>

          {error && <div className="mc-error">{error}</div>}

          <section className="mc-grid">
            <MetricCard
              titulo="Completitud de datos"
              metrica={metricas.completitud_datos}
              afectada={afectadas.includes('completitud_datos')}
              detalleExtra={(
                <>
                  <div className="mc-detail-row">
                    <span>Campos completos</span>
                    <strong>{metricas.completitud_datos?.campos_completos ?? 0}</strong>
                  </div>
                  <div className="mc-detail-row">
                    <span>Campos totales</span>
                    <strong>{metricas.completitud_datos?.campos_totales ?? 0}</strong>
                  </div>
                </>
              )}
            />
            <MetricCard
              titulo="Cumplimiento de reglas de negocio"
              metrica={metricas.cumplimiento_reglas_negocio}
              afectada={afectadas.includes('cumplimiento_reglas_negocio')}
              detalleExtra={(
                <>
                  <div className="mc-detail-row">
                    <span>Reglas cumplidas</span>
                    <strong>{metricas.cumplimiento_reglas_negocio?.reglas_cumplidas ?? 0}</strong>
                  </div>
                  <div className="mc-detail-row">
                    <span>Reglas totales</span>
                    <strong>{metricas.cumplimiento_reglas_negocio?.reglas_totales ?? 0}</strong>
                  </div>
                </>
              )}
            />
            <MetricCard
              titulo="Rendimiento / latencia"
              metrica={metricas.rendimiento_latencia}
              afectada={afectadas.includes('rendimiento_latencia')}
              detalleExtra={(
                <>
                  <div className="mc-detail-row">
                    <span>Latencia real</span>
                    <strong>{metricas.rendimiento_latencia?.latencia_ms ?? 0} ms</strong>
                  </div>
                  <div className="mc-detail-row">
                    <span>Objetivo</span>
                    <strong>{metricas.rendimiento_latencia?.objetivo_ms ?? 300} ms</strong>
                  </div>
                </>
              )}
            />
          </section>

          <section className="mc-lab">
            <div className="mc-panel">
              <h2 className="mc-panel-title">Probar escenarios editables</h2>
              <textarea
                className="mc-textarea"
                value={jsonEscenario}
                onChange={(evento) => setJsonEscenario(evento.target.value)}
                spellCheck="false"
              />
            </div>
            <aside className="mc-panel">
              <h2 className="mc-panel-title">Reglas fallidas</h2>
              <div className="mc-rules">
                {reglasFallidas.length === 0 && (
                  <p className="mc-empty">
                    No hay reglas fallidas en la ultima evaluacion.
                  </p>
                )}
                {reglasFallidas.map((regla, index) => (
                  <div className="mc-rule" key={`${regla.referencia}-${regla.regla}-${index}`}>
                    <p className="mc-rule-name">{regla.regla}</p>
                    <p className="mc-rule-info">Entidad: {regla.entidad} | Referencia: {regla.referencia}</p>
                    <p className="mc-rule-info">Esperado: {regla.esperado}</p>
                    <p className="mc-rule-info">Obtenido: {regla.obtenido}</p>
                  </div>
                ))}
              </div>
            </aside>
          </section>
        </div>
      </div>
    </>
  );
}
