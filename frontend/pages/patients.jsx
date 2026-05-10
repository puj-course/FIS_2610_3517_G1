import { useState, useEffect } from "react";
import api from "../api";

const estilos = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
  :root {
    --color-menta: #2DD4BF;
    --color-fondo: #0F1B2D;
    --color-tarjeta: #162030;
    --color-borde: #243447;
    --color-texto: #E2EAF4;
    --color-texto-suave: #7A95B0;
    --color-error: #F4726A;
    --color-campo: #1E2D3D;
  }
  .dp-body {
    background-color: var(--color-fondo);
    font-family: 'DM Sans', sans-serif;
    color: var(--color-texto);
    padding: 2rem; min-height: 100vh;
  }
  .dp-tarjeta {
    background: var(--color-tarjeta); border: 1px solid var(--color-borde);
    border-radius: 20px; padding: 2rem;
    max-width: 800px; margin: 0 auto;
  }
  .dp-btn-volver {
    background: var(--color-menta); color: var(--color-fondo);
    border: none; border-radius: 10px;
    padding: .5rem 1rem; cursor: pointer;
    font-family: 'DM Sans', sans-serif; font-size: .9rem; font-weight: 600;
    margin-bottom: 1rem; display: inline-block;
    transition: background .2s;
  }
  .dp-btn-volver:hover { background: #0F9D8A; }
  .dp-titulo { font-family: 'DM Serif Display', serif; font-size: 1.75rem; margin: 0 0 1rem; }
  .dp-hr { border: none; border-top: 1px solid var(--color-borde); margin: 1.25rem 0; }
  .dp-row { display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1rem; }
  .dp-col { flex: 1; min-width: 240px; }
  .dp-col p { font-size: .92rem; margin: 0 0 .75rem; line-height: 1.6; }
  .dp-col p strong { color: var(--color-texto); }
  .dp-subtitulo { font-family: 'DM Serif Display', serif; font-size: 1.3rem; margin: 1rem 0; }
  .dp-med-card {
    background: rgba(45,212,191,.08); border: 1px solid var(--color-borde);
    border-radius: 12px; padding: 1rem; margin-bottom: 1rem;
  }
  .dp-med-nombre { font-family: 'DM Serif Display', serif; font-size: 1.1rem; margin: 0 0 .75rem; }
  .dp-med-card p { font-size: .88rem; margin: 0 0 .4rem; color: var(--color-texto-suave); }
  .dp-med-card p strong { color: var(--color-texto); }
  .dp-acciones { margin-top: 1.5rem; display: flex; gap: .75rem; flex-wrap: wrap; }
  .dp-btn-agregar {
    background: var(--color-menta); color: var(--color-fondo);
    border: none; border-radius: 10px;
    padding: .55rem 1.1rem; cursor: pointer;
    font-family: 'DM Sans', sans-serif; font-size: .9rem; font-weight: 600;
    transition: background .2s;
  }
  .dp-btn-agregar:hover { background: #0F9D8A; }
  .dp-btn-secundario {
    background: none; color: var(--color-texto-suave);
    border: 1.5px solid var(--color-borde); border-radius: 10px;
    padding: .55rem 1.1rem; cursor: pointer;
    font-family: 'DM Sans', sans-serif; font-size: .9rem;
    transition: border-color .2s, color .2s;
  }
  .dp-btn-secundario:hover { border-color: var(--color-menta); color: var(--color-menta); }
  .dp-alerta {
    background: rgba(244,114,106,.12); border: 1px solid rgba(244,114,106,.4);
    color: var(--color-error); border-radius: 10px;
    padding: .7rem 1rem; font-size: .85rem; margin-bottom: 1rem;
  }
  .dp-muted { color: var(--color-texto-suave); font-size: .88rem; }
  .dp-cargando { text-align: center; padding: 2rem; color: var(--color-texto-suave); }
`;

// ── Componente principal ────────────────────────────────────────────────────
export default function DetallePaciente({ pacienteId, onVolver, onAgregarMedicamento }) {
  /*
    Props:
    - pacienteId (número/string): ID del paciente a mostrar.
      En el HTML original venía de ?id= en la URL.
    - onVolver: función que navega de vuelta al dashboard.
    - onAgregarMedicamento: función que navega a la pantalla de agregar medicamento.
      Recibe el pacienteId para que el destino lo use.
  */

  const [paciente,     setPaciente]     = useState(null);
  const [medicamentos, setMedicamentos] = useState([]);
  const [error,        setError]        = useState("");
  const [cargando,     setCargando]     = useState(true);

  useEffect(() => {
    if (!pacienteId) {
      setError("No se especificó un paciente válido.");
      setCargando(false);
      return;
    }

    const cargar = async () => {
      setCargando(true);
      setError("");
      try {
        // 1. Obtener lista de pacientes y filtrar por ID
        const resPac = await fetch("http://localhost:8000/pacientes");
        if (!resPac.ok) throw new Error("Error al cargar pacientes");
        const pacientes = await resPac.json();
        const encontrado = pacientes.find((p) => String(p.id) === String(pacienteId));

        if (!encontrado) {
          setError(`No se encontró el paciente con ID ${pacienteId}.`);
          return;
        }
        setPaciente(encontrado);

        // 2. Obtener medicamentos del paciente
        const resMed = await fetch(`http://localhost:8000/medicamentos/paciente/${pacienteId}`);
        const meds = resMed.ok ? await resMed.json() : [];
        setMedicamentos(meds);
      } catch {
        setError("Error de conexión con el servidor.");
      } finally {
        setCargando(false);
      }
    };

    cargar();
  }, [pacienteId]);

  if (cargando) {
    return (
      <>
        <style>{estilos}</style>
        <div className="dp-body">
          <div className="dp-tarjeta">
            <div className="dp-cargando">Cargando información del paciente...</div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <style>{estilos}</style>
      <div className="dp-body">
        <div className="dp-tarjeta">
          <button className="dp-btn-volver" onClick={onVolver}>← Volver al Dashboard</button>

          {error && <div className="dp-alerta">{error}</div>}

          {paciente && (
            <>
              <h2 className="dp-titulo">{paciente.nombres} {paciente.apellidos}</h2>
              <hr className="dp-hr" />

              <div className="dp-row">
                <div className="dp-col">
                  <p><strong>📄 Documento:</strong> {paciente.tipo_documento} {paciente.numero_documento}</p>
                  <p><strong>🎂 Fecha nacimiento:</strong> {paciente.fecha_nacimiento}</p>
                  <p><strong>⚥ Género:</strong> {paciente.genero}</p>
                  <p><strong>📞 Teléfono:</strong> {paciente.telefono_contacto || "—"}</p>
                </div>
                <div className="dp-col">
                  <p><strong>🏥 EPS:</strong> {paciente.eps_aseguradora || "—"}</p>
                  <p><strong>🩺 Diagnóstico:</strong> {paciente.diagnostico_principal || "—"}</p>
                  <p><strong>⚠️ Alergias:</strong> {paciente.alergias_conocidas || "—"}</p>
                </div>
              </div>

              <hr className="dp-hr" />
              <h3 className="dp-subtitulo">💊 Medicamentos</h3>

              {medicamentos.length === 0 ? (
                <p className="dp-muted">No hay medicamentos registrados para este paciente.</p>
              ) : (
                medicamentos.map((m, i) => (
                  <div key={i} className="dp-med-card">
                    <h4 className="dp-med-nombre">{m.nombre}</h4>
                    <p><strong>Dosis:</strong> {m.dosis}</p>
                    <p><strong>Frecuencia:</strong> {m.frecuencia}</p>
                    <p><strong>Horario:</strong> {m.horario}</p>
                    <p><strong>Fecha inicio:</strong> {m.fecha_inicio}</p>
                    {m.observaciones && <p><strong>Observaciones:</strong> {m.observaciones}</p>}
                  </div>
                ))
              )}

              <div className="dp-acciones">
                <button
                  className="dp-btn-agregar"
                  onClick={() => onAgregarMedicamento?.(pacienteId)}
                >
                  + Agregar Medicamento
                </button>
                <button className="dp-btn-secundario" onClick={onVolver}>
                  Volver
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}