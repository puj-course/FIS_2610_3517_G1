import { useState, useEffect } from "react";
import api from "../api";  

const hoy = new Date().toISOString().split("T")[0];

const estilos = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
  :root {
    --menta: #2DD4BF; --menta-oscuro: #0F9D8A;
    --fondo: #0F1B2D; --campo: #1E2D3D; --tarjeta: #162030;
    --borde: #243447; --texto: #E2EAF4; --suave: #7A95B0;
    --error: #F4726A; --exito: #4ADE80;
  }
  *, *::before, *::after { box-sizing: border-box; }
  .rec-body { margin: 0; min-height: 100vh; background: var(--fondo); font-family: 'DM Sans', sans-serif; color: var(--texto); display: flex; align-items: center; justify-content: center; padding: 2rem 1rem; background-image: radial-gradient(ellipse 60% 50% at 80% 10%, rgba(45,212,191,.12) 0%, transparent 70%), radial-gradient(ellipse 40% 40% at 10% 80%, rgba(45,212,191,.07) 0%, transparent 60%); }
  .rec-tarjeta { background: var(--tarjeta); border: 1px solid var(--borde); border-radius: 20px; width: 100%; max-width: 560px; padding: 2.5rem; box-shadow: 0 32px 80px rgba(0,0,0,.5); animation: rec-subir .45s ease both; }
  @keyframes rec-subir { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: translateY(0); } }
  .rec-marca { display: flex; align-items: center; gap: .6rem; margin-bottom: 1.75rem; }
  .rec-marca-icono { width: 36px; height: 36px; background: var(--menta); border-radius: 10px; display: flex; align-items: center; justify-content: center; }
  .rec-marca-nombre { font-family: 'DM Serif Display', serif; font-size: 1.35rem; }
  .rec-titulo { font-family: 'DM Serif Display', serif; font-size: 1.65rem; margin: 0 0 .25rem; }
  .rec-subtitulo { font-size: .88rem; color: var(--suave); margin: 0 0 1.75rem; }
  .rec-campo-grupo { margin-bottom: 1.1rem; }
  .rec-label { display: block; font-size: .82rem; font-weight: 500; color: var(--suave); margin-bottom: .4rem; }
  .rec-label .req { color: var(--menta); }
  .rec-select, .rec-input, .rec-textarea { width: 100%; background: var(--campo); border: 1.5px solid var(--borde); color: var(--texto); border-radius: 10px; padding: .65rem .9rem; font-size: .92rem; font-family: 'DM Sans', sans-serif; transition: border-color .2s, box-shadow .2s; }
  .rec-select:focus, .rec-input:focus, .rec-textarea:focus { outline: none; border-color: var(--menta); box-shadow: 0 0 0 3px rgba(45,212,191,.18); }
  .rec-select option { background: var(--campo); }
  .rec-input::placeholder, .rec-textarea::placeholder { color: #4A6278; }
  .rec-invalido { border-color: var(--error) !important; }
  .rec-valido   { border-color: var(--exito) !important; }
  .rec-msg-error { font-size: .78rem; color: var(--error); margin-top: .3rem; }
  .rec-alerta { background: rgba(244,114,106,.1); border: 1px solid var(--error); color: var(--error); border-radius: 10px; padding: .75rem 1rem; font-size: .85rem; margin-bottom: 1rem; }
  .rec-info-med { background: rgba(45,212,191,.08); border: 1px solid rgba(45,212,191,.2); border-radius: 10px; padding: .75rem 1rem; font-size: .84rem; color: var(--menta); margin-bottom: 1rem; }
  .rec-btn-guardar { width: 100%; background: var(--menta); color: var(--fondo); border: none; border-radius: 12px; padding: .75rem; font-size: .95rem; font-weight: 600; font-family: 'DM Sans', sans-serif; cursor: pointer; margin-top: 1.5rem; transition: background .2s, box-shadow .2s; }
  .rec-btn-guardar:hover { background: var(--menta-oscuro); box-shadow: 0 8px 24px rgba(45,212,191,.3); }
  .rec-btn-guardar:disabled { opacity: .6; cursor: not-allowed; }
  .rec-btn-volver { width: 100%; background: transparent; color: var(--suave); border: 1.5px solid var(--borde); border-radius: 12px; padding: .65rem; font-size: .88rem; font-family: 'DM Sans', sans-serif; cursor: pointer; margin-top: .75rem; transition: border-color .2s, color .2s; }
  .rec-btn-volver:hover { border-color: var(--suave); color: var(--texto); }
  .rec-notif-ctn { position: fixed; top: 1.25rem; right: 1.25rem; z-index: 9999; }
  .rec-notif { background: var(--tarjeta); border: 1px solid var(--exito); border-radius: 12px; padding: .85rem 1.1rem; font-size: .86rem; margin-bottom: .5rem; min-width: 250px; color: var(--texto); animation: rec-deslizar .3s ease both; }
  .rec-notif.err { border-color: var(--error); }
  @keyframes rec-deslizar { from { opacity: 0; transform: translateX(30px); } to { opacity: 1; transform: translateX(0); } }
`;

const claseInput = (tocado, invalido) => {
  if (!tocado) return "";
  return invalido ? "rec-invalido" : "rec-valido";
};

export default function Recordatorios({ onVolver, onGuardadoExitoso }) {
  const [pacientes,       setPacientes]       = useState([]);
  const [medicamentos,    setMedicamentos]    = useState([]);
  const [medSeleccionado, setMedSeleccionado] = useState(null);
  const [notifs,          setNotifs]          = useState([]);
  const [cargandoMeds,    setCargandoMeds]    = useState(false);
  const [guardando,       setGuardando]       = useState(false);
  const [alertaError,     setAlertaError]     = useState("");

  const [form, setForm] = useState({
    pacienteId: "", medicamentoId: "", horaRecordatorio: "",
    fechaInicio: hoy, activo: "1", observaciones: "",
  });
  const [tocados, setTocados] = useState({});
  const [errores, setErrores] = useState({});

  // ✅ usa api.obtenerPacientes
  useEffect(() => {
    api.obtenerPacientes()
      .then(res => {
        if (!res.ok) throw new Error();
        const lista = Array.isArray(res.body) ? res.body : (res.body.pacientes || []);
        setPacientes(lista);
      })
      .catch(() => setAlertaError("No se pudo conectar con el servidor para cargar los pacientes."));
  }, []);

  const handlePacienteChange = async (e) => {
    const id = e.target.value;
    setForm(f => ({ ...f, pacienteId: id, medicamentoId: "" }));
    setMedicamentos([]); setMedSeleccionado(null);
    if (!id) return;
    setCargandoMeds(true);
    try {
      // ✅ usa api.obtenerMedicamentos — ID es string ObjectId
      const res = await api.obtenerMedicamentos(id);
      const meds = res.ok ? (Array.isArray(res.body) ? res.body : (res.body.medicamentos || [])) : [];
      setMedicamentos(meds);
    } catch {
      setMedicamentos([]);
    } finally {
      setCargandoMeds(false);
    }
  };

  const handleMedChange = (e) => {
    const id = e.target.value;
    setForm(f => ({ ...f, medicamentoId: id }));
    // ✅ comparar como string (ObjectId de MongoDB)
    const med = medicamentos.find(m => String(m.id) === id);
    setMedSeleccionado(med || null);
    if (med?.horario) {
      const primera = med.horario.split(",")[0].trim();
      if (primera) setForm(f => ({ ...f, horaRecordatorio: primera }));
    }
  };

  const validar = (campos = form) => {
    const e = {};
    if (!campos.pacienteId)       e.pacienteId = true;
    if (!campos.medicamentoId)    e.medicamentoId = true;
    if (!campos.horaRecordatorio) e.horaRecordatorio = true;
    if (!campos.fechaInicio)      e.fechaInicio = true;
    return e;
  };

  const notif = (msg, err) => {
    const id = Date.now();
    setNotifs(p => [...p, { id, msg, err }]);
    setTimeout(() => setNotifs(p => p.filter(n => n.id !== id)), 3500);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setAlertaError("");
    const allTocados = { pacienteId: true, medicamentoId: true, horaRecordatorio: true, fechaInicio: true };
    setTocados(allTocados);
    const e2 = validar();
    setErrores(e2);
    if (Object.keys(e2).length) return;

    setGuardando(true);
    const partes = form.fechaInicio.split("-");
    const fechaBackend = partes[1] + "/" + partes[2] + "/" + partes[0];
    const datos = {
      medicamento_id:    form.medicamentoId,  // ✅ string ObjectId, sin parseInt
      hora_recordatorio: form.horaRecordatorio,
      fecha_inicio:      fechaBackend,
      activo:            parseInt(form.activo),  // activo sí es int (0/1)
      observaciones:     form.observaciones.trim(),
    };
    try {
      // ✅ usa api.crearRecordatorio
      const res = await api.crearRecordatorio(datos);
      if (!res.ok) { setAlertaError(res.body.detail || "Error al crear el recordatorio."); return; }
      notif("Recordatorio creado correctamente ✓");
      setTimeout(() => onGuardadoExitoso?.(), 1500);
    } catch {
      setAlertaError("Error de conexión con el servidor.");
    } finally {
      setGuardando(false);
    }
  };

  const touch = (field) => setTocados(t => ({ ...t, [field]: true }));

  return (
    <>
      <style>{estilos}</style>
      <div className="rec-notif-ctn">
        {notifs.map(n => (
          <div key={n.id} className={`rec-notif${n.err ? " err" : ""}`}>{n.msg}</div>
        ))}
      </div>
      <div className="rec-body">
        <div className="rec-tarjeta">
          <div className="rec-marca">
            <div className="rec-marca-icono">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ width: 20, height: 20, color: "var(--fondo)" }}>
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>
              </svg>
            </div>
            <span className="rec-marca-nombre">MedTrack</span>
          </div>
          <h1 className="rec-titulo">Registrar Recordatorio</h1>
          <p className="rec-subtitulo">Selecciona el paciente y su medicamento para programar el recordatorio.</p>
          {alertaError && <div className="rec-alerta">{alertaError}</div>}

          <form onSubmit={handleSubmit} noValidate>
            <div className="rec-campo-grupo">
              <label className="rec-label">Paciente <span className="req">*</span></label>
              <select className={`rec-select ${claseInput(tocados.pacienteId, errores.pacienteId)}`}
                value={form.pacienteId} onChange={handlePacienteChange} onBlur={() => touch("pacienteId")}>
                <option value="">Selecciona un paciente…</option>
                {pacientes.map(p => (
                  <option key={p.id} value={p.id}>{p.nombres} {p.apellidos} — {p.tipo_documento} {p.numero_documento}</option>
                ))}
              </select>
              {tocados.pacienteId && errores.pacienteId && <div className="rec-msg-error">Selecciona un paciente.</div>}
            </div>

            <div className="rec-campo-grupo">
              <label className="rec-label">Medicamento <span className="req">*</span></label>
              <select className={`rec-select ${claseInput(tocados.medicamentoId, errores.medicamentoId)}`}
                value={form.medicamentoId} onChange={handleMedChange} onBlur={() => touch("medicamentoId")}
                disabled={!form.pacienteId || cargandoMeds}>
                <option value="">{cargandoMeds ? "Cargando medicamentos…" : !form.pacienteId ? "Primero selecciona un paciente" : "Selecciona un medicamento…"}</option>
                {medicamentos.map(m => (
                  <option key={m.id} value={m.id}>{m.nombre_medicamento || m.nombre} — {m.dosis_cantidad} {m.dosis_unidad || m.dosis} ({m.frecuencia})</option>
                ))}
              </select>
              {tocados.medicamentoId && errores.medicamentoId && <div className="rec-msg-error">Selecciona un medicamento.</div>}
            </div>

            {medSeleccionado && (
              <div className="rec-info-med">
                💊 <strong>{medSeleccionado.nombre_medicamento || medSeleccionado.nombre}</strong> &nbsp;|&nbsp;
                Dosis: {medSeleccionado.dosis_cantidad} {medSeleccionado.dosis_unidad || medSeleccionado.dosis} &nbsp;|&nbsp;
                Frecuencia: {medSeleccionado.frecuencia}
                {medSeleccionado.horario && ` | Horario: ${medSeleccionado.horario}`}
              </div>
            )}

            <div className="rec-campo-grupo">
              <label className="rec-label">Hora del recordatorio <span className="req">*</span></label>
              <input type="time" className={`rec-input ${claseInput(tocados.horaRecordatorio, errores.horaRecordatorio)}`}
                value={form.horaRecordatorio}
                onChange={e => setForm(f => ({ ...f, horaRecordatorio: e.target.value }))}
                onBlur={() => touch("horaRecordatorio")} />
              {tocados.horaRecordatorio && errores.horaRecordatorio && <div className="rec-msg-error">Selecciona una hora.</div>}
            </div>

            <div className="rec-campo-grupo">
              <label className="rec-label">Fecha de inicio <span className="req">*</span></label>
              <input type="date" className={`rec-input ${claseInput(tocados.fechaInicio, errores.fechaInicio)}`}
                value={form.fechaInicio} min={hoy}
                onChange={e => setForm(f => ({ ...f, fechaInicio: e.target.value }))}
                onBlur={() => touch("fechaInicio")} />
              {tocados.fechaInicio && errores.fechaInicio && <div className="rec-msg-error">Selecciona una fecha válida.</div>}
            </div>

            <div className="rec-campo-grupo">
              <label className="rec-label">Estado</label>
              <select className="rec-select" value={form.activo} onChange={e => setForm(f => ({ ...f, activo: e.target.value }))}>
                <option value="1">Activo</option>
                <option value="0">Inactivo</option>
              </select>
            </div>

            <div className="rec-campo-grupo">
              <label className="rec-label">Observaciones</label>
              <textarea className="rec-textarea" rows={2} maxLength={300} placeholder="Notas adicionales…"
                value={form.observaciones}
                onChange={e => setForm(f => ({ ...f, observaciones: e.target.value }))} />
            </div>

            <button type="submit" className="rec-btn-guardar" disabled={guardando}>
              {guardando ? "Guardando…" : "Guardar recordatorio"}
            </button>
            <button type="button" className="rec-btn-volver" onClick={onVolver}>← Volver</button>
          </form>
        </div>
      </div>
    </>
  );
}
