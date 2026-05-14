import { useState, useEffect, useRef } from "react";
import api from "../api";

const css = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
  :root {
    --color-menta: #2DD4BF; --color-menta-oscuro: #0F9D8A;
    --color-fondo: #0F1B2D; --color-campo: #1E2D3D; --color-tarjeta: #162030;
    --color-borde: #243447; --color-texto: #E2EAF4; --color-suave: #7A95B0;
    --color-error: #F4726A; --color-exito: #4ADE80;
  }
  *, *::before, *::after { box-sizing: border-box; }
  .rm-body { margin: 0; min-height: 100vh; background-color: var(--color-fondo); font-family: 'DM Sans', sans-serif; color: var(--color-texto); display: flex; align-items: center; justify-content: center; padding: 2rem 1rem; background-image: radial-gradient(ellipse 60% 50% at 80% 10%, rgba(45,212,191,.12) 0%, transparent 70%), radial-gradient(ellipse 40% 40% at 10% 80%, rgba(45,212,191,.07) 0%, transparent 60%); }
  .rm-tarjeta { background: var(--color-tarjeta); border: 1px solid var(--color-borde); border-radius: 20px; width: 100%; max-width: 660px; padding: 2.5rem 2.5rem 2rem; box-shadow: 0 32px 80px rgba(0,0,0,.5); animation: rm-subir .5s ease both; }
  @keyframes rm-subir { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: translateY(0); } }
  .rm-marca { display: flex; align-items: center; gap: .6rem; margin-bottom: 1.75rem; }
  .rm-marca-icono { width: 38px; height: 38px; background: var(--color-menta); border-radius: 10px; display: flex; align-items: center; justify-content: center; }
  .rm-marca-icono svg { width: 22px; height: 22px; color: var(--color-fondo); }
  .rm-marca-nombre { font-family: 'DM Serif Display', serif; font-size: 1.45rem; }
  .rm-h1 { font-family: 'DM Serif Display', serif; font-size: 1.75rem; margin: 0 0 .25rem; }
  .rm-subtitulo { font-size: .88rem; color: var(--color-suave); margin: 0 0 .25rem; }
  .rm-separador { display: flex; align-items: center; gap: .75rem; margin: 1.5rem 0 1.25rem; color: var(--color-suave); font-size: .78rem; text-transform: uppercase; letter-spacing: .08em; }
  .rm-separador::before, .rm-separador::after { content: ''; flex: 1; height: 1px; background: var(--color-borde); }
  .rm-label { font-size: .82rem; font-weight: 500; color: var(--color-suave); display: block; margin-bottom: .4rem; }
  .rm-label .obligatorio { color: var(--color-menta); }
  .rm-input, .rm-select { background: var(--color-campo); border: 1.5px solid var(--color-borde); color: var(--color-texto); border-radius: 10px; padding: .65rem .9rem; font-size: .92rem; font-family: 'DM Sans', sans-serif; transition: border-color .2s, box-shadow .2s; width: 100%; }
  .rm-input:focus, .rm-select:focus { background: var(--color-campo); border-color: var(--color-menta); color: var(--color-texto); box-shadow: 0 0 0 3px rgba(45,212,191,.18); outline: none; }
  .rm-input::placeholder { color: #4A6278; }
  .rm-select option { background: var(--color-campo); }
  .rm-input.error, .rm-select.error { border-color: var(--color-error); box-shadow: none; }
  .rm-input.correcto, .rm-select.correcto { border-color: var(--color-exito); box-shadow: none; }
  .rm-error-msg { font-size: .78rem; color: var(--color-error); margin-top: .3rem; }
  .rm-caja-horarios { background: var(--color-campo); border: 1.5px solid var(--color-borde); border-radius: 10px; padding: .5rem .75rem; display: flex; flex-wrap: wrap; gap: .4rem; align-items: center; min-height: 46px; cursor: text; transition: border-color .2s, box-shadow .2s; }
  .rm-caja-horarios:focus-within { border-color: var(--color-menta); box-shadow: 0 0 0 3px rgba(45,212,191,.18); }
  .rm-caja-horarios.error { border-color: var(--color-error); }
  .rm-caja-horarios.correcto { border-color: var(--color-exito); }
  .rm-pastilla { background: rgba(45,212,191,.15); border: 1px solid rgba(45,212,191,.35); color: var(--color-menta); border-radius: 20px; padding: .2rem .65rem; font-size: .82rem; display: flex; align-items: center; gap: .35rem; }
  .rm-pastilla button { background: none; border: none; color: var(--color-menta); cursor: pointer; padding: 0; opacity: .7; font-size: .9rem; }
  .rm-pastilla button:hover { opacity: 1; }
  .rm-input-hora { border: none; background: transparent; color: var(--color-texto); font-family: 'DM Sans', sans-serif; font-size: .9rem; outline: none; width: 110px; padding: .15rem 0; }
  .rm-input-hora::-webkit-calendar-picker-indicator { filter: invert(.5); cursor: pointer; }
  .rm-texto-ayuda { font-size: .75rem; color: var(--color-suave); margin-top: .3rem; }
  .rm-grupo-dias { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: .25rem; }
  .rm-boton-dia { background: var(--color-campo); border: 1.5px solid var(--color-borde); color: var(--color-suave); border-radius: 8px; padding: .4rem .75rem; font-size: .82rem; font-family: 'DM Sans', sans-serif; cursor: pointer; transition: all .2s; user-select: none; }
  .rm-boton-dia.seleccionado { background: rgba(45,212,191,.15); border-color: var(--color-menta); color: var(--color-menta); font-weight: 600; }
  .rm-contador { font-size: .75rem; color: var(--color-suave); text-align: right; margin-top: .2rem; }
  .rm-alerta-error { background: rgba(244,114,106,.12); border: 1px solid rgba(244,114,106,.4); color: var(--color-error); border-radius: 10px; padding: .7rem 1rem; font-size: .85rem; margin-top: 1rem; }
  .rm-boton-guardar { background: var(--color-menta); color: var(--color-fondo); border: none; border-radius: 12px; padding: .75rem; font-size: .95rem; font-weight: 600; font-family: 'DM Sans', sans-serif; width: 100%; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: .5rem; transition: background .2s, box-shadow .2s, transform .1s; margin-top: 1.5rem; }
  .rm-boton-guardar:hover { background: var(--color-menta-oscuro); box-shadow: 0 8px 24px rgba(45,212,191,.3); }
  .rm-boton-guardar:active { transform: scale(.98); }
  .rm-boton-guardar:disabled { opacity: .6; cursor: not-allowed; }
  .rm-boton-guardar svg { width: 18px; height: 18px; }
  .rm-boton-limpiar { background: transparent; color: var(--color-suave); border: 1.5px solid var(--color-borde); border-radius: 12px; padding: .65rem; font-size: .88rem; font-family: 'DM Sans', sans-serif; width: 100%; cursor: pointer; transition: border-color .2s, color .2s; margin-top: .75rem; }
  .rm-boton-limpiar:hover { border-color: var(--color-suave); color: var(--color-texto); }
  .rm-notif-ctn { position: fixed; top: 1.5rem; right: 1.5rem; z-index: 9999; display: flex; flex-direction: column; gap: .5rem; }
  .rm-notif { background: var(--color-tarjeta); border: 1px solid var(--color-exito); border-radius: 12px; padding: .9rem 1.2rem; display: flex; align-items: center; gap: .75rem; box-shadow: 0 8px 32px rgba(0,0,0,.4); animation: rm-entrar .35s ease both; font-size: .88rem; }
  .rm-notif.error { border-color: var(--color-error); }
  @keyframes rm-entrar { from { opacity: 0; transform: translateX(40px); } to { opacity: 1; transform: translateX(0); } }
  .rm-row { display: flex; flex-wrap: wrap; gap: 1rem; }
  .rm-col { flex: 1; min-width: 200px; }
  .rm-col-12 { flex: 0 0 100%; }
  .rm-btn-agregar { margin-top: .4rem; background: rgba(45,212,191,.12); border: 1.5px solid rgba(45,212,191,.3); color: var(--color-menta); border-radius: 8px; padding: .35rem .9rem; font-size: .82rem; cursor: pointer; font-family: 'DM Sans', sans-serif; }
  @media (max-width: 480px) { .rm-tarjeta { padding: 1.75rem 1.25rem 1.5rem; } }
`;

const NOMBRES_DIAS = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom'];
const CLAVES_DIAS  = ['lun', 'mar', 'mie', 'jue', 'vie', 'sab', 'dom'];
const FRECUENCIAS_CON_DIAS = ['dias_alternos', 'semanal', 'personalizado'];

function convertirFechaAFormatoBackend(fechaISO) {
  if (!fechaISO) return "";
  const partes = fechaISO.split("-");
  if (partes.length !== 3) return fechaISO;
  return partes[1] + "/" + partes[2] + "/" + partes[0];
}

function extraerMensajeError(body) {
  const detalle = body?.detail ?? body;
  if (typeof detalle === 'string') return detalle;
  if (Array.isArray(detalle)) return detalle.map(i => (typeof i === 'string' ? i : i.msg || JSON.stringify(i))).join(' | ');
  if (detalle && typeof detalle === 'object') return detalle.msg || detalle.message || JSON.stringify(detalle);
  return 'No se pudo registrar el medicamento.';
}

export default function RegistroMedicamento() {
  const fechaHoy     = new Date().toISOString().split('T')[0];
  const inputHoraRef = useRef(null);

  const [pacientes,         setPacientes]         = useState([]);
  const [pacientesCargando, setPacientesCargando] = useState(true);
  const [pacientesError,    setPacientesError]    = useState('');
  const [horarios,          setHorarios]          = useState([]);
  const [horaInput,         setHoraInput]         = useState('');
  const [diasSeleccionados, setDiasSeleccionados] = useState([]);
  const [instruccionesLen,  setInstruccionesLen]  = useState(0);
  const [form, setForm] = useState({
    nombre: '', concentracion: '', forma: '', dosis: '', unidad: '',
    frecuencia: '', comida: '', fechaInicio: fechaHoy, fechaFin: '',
    paciente: '', via: '', medico: '', instrucciones: ''
  });
  const [errores,       setErrores]       = useState({});
  const [alertaGeneral, setAlertaGeneral] = useState('');
  const [notifs,        setNotifs]        = useState([]);
  const [guardando,     setGuardando]     = useState(false);

  useEffect(() => { cargarPacientes(); }, []);

  async function cargarPacientes() {
    setPacientesCargando(true);
    setPacientesError('');
    try {
      const res = await api.obtenerPacientes();
      if (!res.ok) throw new Error();
      const lista = Array.isArray(res.body) ? res.body : (res.body.pacientes || []);
      if (!lista || lista.length === 0) {
        setPacientesError('No hay pacientes registrados en el sistema.');
        setPacientes([]);
      } else {
        // Normalizar _id de MongoDB
        setPacientes(lista.map(p => ({ ...p, id: p.id || p._id })));
      }
    } catch {
      setPacientesError('No se pudieron cargar los pacientes. Verifica que el backend esté encendido.');
    } finally {
      setPacientesCargando(false);
    }
  }

  function mostrarNotif(msg, esError = false) {
    const id = Date.now();
    setNotifs(prev => [...prev, { id, msg, esError }]);
    setTimeout(() => setNotifs(prev => prev.filter(n => n.id !== id)), 3500);
  }

  function agregarHorario() {
    if (!horaInput) { inputHoraRef.current?.focus(); return; }
    if (horarios.includes(horaInput)) { mostrarNotif('Ese horario ya fue agregado.', true); setHoraInput(''); return; }
    setHorarios(prev => [...prev, horaInput]);
    setHoraInput('');
    setErrores(prev => ({ ...prev, horarios: '' }));
  }

  function quitarHorario(hora) { setHorarios(prev => prev.filter(h => h !== hora)); }
  function toggleDia(clave) { setDiasSeleccionados(prev => prev.includes(clave) ? prev.filter(d => d !== clave) : [...prev, clave]); }

  function handleChange(e) {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    if (name === 'frecuencia' && !FRECUENCIAS_CON_DIAS.includes(value)) setDiasSeleccionados([]);
  }

  function validarCampo(campo, valor) {
    if (!valor || valor === '') return 'Campo requerido.';
    if (campo === 'dosis' && parseFloat(valor) <= 0) return 'Ingresa la dosis (número mayor a 0).';
    return '';
  }

  const camposObligatorios = ['nombre','concentracion','forma','dosis','unidad','frecuencia','fechaInicio','paciente'];

  function handleBlur(e) {
    const { name, value } = e.target;
    if (camposObligatorios.includes(name)) setErrores(prev => ({ ...prev, [name]: validarCampo(name, value) }));
  }

  function limpiarFormulario() {
    setForm({ nombre:'', concentracion:'', forma:'', dosis:'', unidad:'', frecuencia:'',
              comida:'', fechaInicio: fechaHoy, fechaFin:'', paciente:'', via:'', medico:'', instrucciones:'' });
    setHorarios([]); setHoraInput(''); setDiasSeleccionados([]); setInstruccionesLen(0); setErrores({}); setAlertaGeneral('');
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setAlertaGeneral('');
    const nuevosErrores = {};
    let valido = true;
    camposObligatorios.forEach(campo => {
      const err = validarCampo(campo, form[campo]);
      if (err) { nuevosErrores[campo] = err; valido = false; }
    });
    if (horarios.length === 0) { nuevosErrores.horarios = 'Agrega al menos un horario.'; valido = false; }
    if (form.fechaFin && form.fechaFin < form.fechaInicio) { nuevosErrores.fechaFin = 'No puede ser anterior a la fecha de inicio.'; valido = false; }
    if (FRECUENCIAS_CON_DIAS.includes(form.frecuencia) && diasSeleccionados.length === 0) { nuevosErrores.dias = 'Selecciona al menos un día.'; valido = false; }
    setErrores(nuevosErrores);
    if (!valido) { mostrarNotif('Revisa los campos marcados en rojo.', true); return; }

    // ✅ Campos correctos para MongoDB / backend
    const datos = {
      nombre_medicamento: form.nombre.trim(),
      concentracion:      form.concentracion.trim(),
      forma_farmaceutica: form.forma,
      dosis_cantidad:     parseFloat(form.dosis),
      dosis_unidad:       form.unidad,
      frecuencia:         form.frecuencia,
      relacion_comida:    form.comida || "",
      horarios,                                    // array de strings "HH:MM"
      dias:               diasSeleccionados,
      fecha_inicio:       convertirFechaAFormatoBackend(form.fechaInicio),
      fecha_fin:          form.fechaFin ? convertirFechaAFormatoBackend(form.fechaFin) : null,
      paciente_id:        form.paciente,           // string ObjectId de MongoDB
      via_administracion: form.via || "",
      medico_receto:      form.medico.trim(),
      instrucciones:      form.instrucciones.trim(),
    };

    setGuardando(true);
    try {
      const res = await api.registrarMedicamento(datos);
      if (!res.ok) { setAlertaGeneral(extraerMensajeError(res.body)); mostrarNotif('Error al registrar el medicamento.', true); return; }
      const pacienteOpc = pacientes.find(p => String(p.id) === String(form.paciente));
      const nombrePaciente = pacienteOpc ? `${pacienteOpc.nombres} ${pacienteOpc.apellidos}` : 'el paciente';
      mostrarNotif(`"${datos.nombre_medicamento}" registrado para ${nombrePaciente}.`);
      limpiarFormulario();
    } catch {
      setAlertaGeneral('No se pudo conectar con el servidor.');
      mostrarNotif('No se pudo conectar con el backend.', true);
    } finally {
      setGuardando(false);
    }
  }

  const mostrarDias = FRECUENCIAS_CON_DIAS.includes(form.frecuencia);

  return (
    <div className="rm-body">
      <style>{css}</style>
      <div className="rm-notif-ctn">
        {notifs.map(n => <div key={n.id} className={`rm-notif${n.esError ? ' error' : ''}`}>{n.msg}</div>)}
      </div>
      <div className="rm-tarjeta">
        <div className="rm-marca">
          <div className="rm-marca-icono">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 8v4m0 4h.01M3 12a9 9 0 1 0 18 0A9 9 0 0 0 3 12z"/>
            </svg>
          </div>
          <span className="rm-marca-nombre">MedTrack</span>
        </div>
        <h1 className="rm-h1">Registrar Medicamento</h1>
        <p className="rm-subtitulo">Completa la información del medicamento para el paciente.</p>

        <form onSubmit={handleSubmit} noValidate>
          <div className="rm-separador">Datos del medicamento</div>
          <div className="rm-row">
            <div className="rm-col-12">
              <label className="rm-label">Nombre del medicamento <span className="obligatorio">*</span></label>
              <input className={`rm-input${errores.nombre ? ' error' : form.nombre ? ' correcto' : ''}`} name="nombre" value={form.nombre} onChange={handleChange} onBlur={handleBlur} placeholder="Ej. Losartan, Metformina" maxLength={100} />
              {errores.nombre && <div className="rm-error-msg">{errores.nombre}</div>}
            </div>
            <div className="rm-col">
              <label className="rm-label">Concentración <span className="obligatorio">*</span></label>
              <input className={`rm-input${errores.concentracion ? ' error' : form.concentracion ? ' correcto' : ''}`} name="concentracion" value={form.concentracion} onChange={handleChange} onBlur={handleBlur} placeholder="Ej. 50 mg, 500 mg/5 ml" maxLength={60} />
              {errores.concentracion && <div className="rm-error-msg">{errores.concentracion}</div>}
            </div>
            <div className="rm-col">
              <label className="rm-label">Forma farmacéutica <span className="obligatorio">*</span></label>
              <select className={`rm-select${errores.forma ? ' error' : form.forma ? ' correcto' : ''}`} name="forma" value={form.forma} onChange={handleChange} onBlur={handleBlur}>
                <option value="">Selecciona...</option>
                <option value="tableta">Tableta / Pastilla</option>
                <option value="capsula">Cápsula</option>
                <option value="jarabe">Jarabe / Solución</option>
                <option value="inyectable">Inyectable</option>
                <option value="gotas">Gotas</option>
                <option value="inhalador">Inhalador</option>
                <option value="crema">Crema / Ungüento</option>
                <option value="parche">Parche</option>
                <option value="otro">Otro</option>
              </select>
              {errores.forma && <div className="rm-error-msg">{errores.forma}</div>}
            </div>
            <div className="rm-col">
              <label className="rm-label">Dosis por toma <span className="obligatorio">*</span></label>
              <input type="number" className={`rm-input${errores.dosis ? ' error' : form.dosis ? ' correcto' : ''}`} name="dosis" value={form.dosis} onChange={handleChange} onBlur={handleBlur} placeholder="Ej. 1, 2, 0.5" min="0.1" max="999" step="0.1" />
              {errores.dosis && <div className="rm-error-msg">{errores.dosis}</div>}
            </div>
            <div className="rm-col">
              <label className="rm-label">Unidad <span className="obligatorio">*</span></label>
              <select className={`rm-select${errores.unidad ? ' error' : form.unidad ? ' correcto' : ''}`} name="unidad" value={form.unidad} onChange={handleChange} onBlur={handleBlur}>
                <option value="">Selecciona...</option>
                <option value="tabletas">Tableta(s)</option>
                <option value="capsulas">Cápsula(s)</option>
                <option value="ml">Mililitros (ml)</option>
                <option value="mg">Miligramos (mg)</option>
                <option value="gotas">Gota(s)</option>
                <option value="inhalaciones">Inhalación(es)</option>
                <option value="aplicaciones">Aplicación(es)</option>
              </select>
              {errores.unidad && <div className="rm-error-msg">{errores.unidad}</div>}
            </div>
          </div>

          <div className="rm-separador">Horario y frecuencia</div>
          <div className="rm-row">
            <div className="rm-col">
              <label className="rm-label">Frecuencia <span className="obligatorio">*</span></label>
              <select className={`rm-select${errores.frecuencia ? ' error' : form.frecuencia ? ' correcto' : ''}`} name="frecuencia" value={form.frecuencia} onChange={handleChange} onBlur={handleBlur}>
                <option value="">Selecciona...</option>
                <option value="cada_4h">Cada 4 horas</option>
                <option value="cada_6h">Cada 6 horas</option>
                <option value="cada_8h">Cada 8 horas</option>
                <option value="cada_12h">Cada 12 horas</option>
                <option value="una_vez">Una vez al día</option>
                <option value="dias_alternos">Días alternos</option>
                <option value="semanal">Semanal</option>
                <option value="personalizado">Personalizado</option>
              </select>
              {errores.frecuencia && <div className="rm-error-msg">{errores.frecuencia}</div>}
            </div>
            <div className="rm-col">
              <label className="rm-label">Relación con la comida</label>
              <select className="rm-select" name="comida" value={form.comida} onChange={handleChange}>
                <option value="">Selecciona...</option>
                <option value="antes">Antes de comer</option>
                <option value="durante">Durante la comida</option>
                <option value="despues">Después de comer</option>
                <option value="ayunas">En ayunas</option>
                <option value="no_aplica">No aplica</option>
              </select>
            </div>

            <div className="rm-col-12">
              <label className="rm-label">Horarios de toma <span className="obligatorio">*</span></label>
              <div className={`rm-caja-horarios${errores.horarios ? ' error' : horarios.length > 0 ? ' correcto' : ''}`} onClick={() => inputHoraRef.current?.focus()}>
                {horarios.map(hora => (
                  <span key={hora} className="rm-pastilla">
                    {hora}
                    <button type="button" onClick={() => quitarHorario(hora)}>×</button>
                  </span>
                ))}
                <input ref={inputHoraRef} type="time" className="rm-input-hora" value={horaInput}
                  onChange={e => setHoraInput(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); agregarHorario(); } }} />
              </div>
              {errores.horarios && <div className="rm-error-msg">{errores.horarios}</div>}
              <p className="rm-texto-ayuda">Selecciona una hora y presiona Enter o el botón +</p>
              <button type="button" className="rm-btn-agregar" onClick={agregarHorario}>+ Agregar horario</button>
            </div>

            {mostrarDias && (
              <div className="rm-col-12">
                <label className="rm-label">Días de administración</label>
                <div className="rm-grupo-dias">
                  {NOMBRES_DIAS.map((nombre, i) => (
                    <button key={CLAVES_DIAS[i]} type="button"
                      className={`rm-boton-dia${diasSeleccionados.includes(CLAVES_DIAS[i]) ? ' seleccionado' : ''}`}
                      onClick={() => toggleDia(CLAVES_DIAS[i])}>{nombre}</button>
                  ))}
                </div>
                {errores.dias && <div className="rm-error-msg">{errores.dias}</div>}
              </div>
            )}

            <div className="rm-col">
              <label className="rm-label">Fecha de inicio <span className="obligatorio">*</span></label>
              <input type="date" className={`rm-input${errores.fechaInicio ? ' error' : form.fechaInicio ? ' correcto' : ''}`} name="fechaInicio" value={form.fechaInicio} onChange={handleChange} onBlur={handleBlur} />
              {errores.fechaInicio && <div className="rm-error-msg">{errores.fechaInicio}</div>}
            </div>
            <div className="rm-col">
              <label className="rm-label">Fecha de fin del tratamiento</label>
              <input type="date" className={`rm-input${errores.fechaFin ? ' error' : ''}`} name="fechaFin" value={form.fechaFin} onChange={handleChange} />
              {errores.fechaFin && <div className="rm-error-msg">{errores.fechaFin}</div>}
            </div>
          </div>

          <div className="rm-separador">Paciente asociado</div>
          <div className="rm-row">
            <div className="rm-col-12">
              <label className="rm-label">Paciente <span className="obligatorio">*</span></label>
              <select className={`rm-select${errores.paciente ? ' error' : form.paciente ? ' correcto' : ''}`} name="paciente" value={form.paciente} onChange={handleChange} onBlur={handleBlur} disabled={pacientesCargando || !!pacientesError}>
                <option value="">{pacientesCargando ? 'Cargando pacientes...' : pacientesError ? 'Error al cargar' : 'Selecciona un paciente...'}</option>
                {pacientes.map(p => (
                  <option key={p.id} value={p.id}>{p.nombres} {p.apellidos} - {p.numero_documento}</option>
                ))}
              </select>
              {errores.paciente && <div className="rm-error-msg">{errores.paciente}</div>}
            </div>
            <div className="rm-col">
              <label className="rm-label">Vía de administración</label>
              <select className="rm-select" name="via" value={form.via} onChange={handleChange}>
                <option value="">Selecciona...</option>
                <option value="oral">Oral (por boca)</option>
                <option value="sublingual">Sublingual</option>
                <option value="topica">Tópica</option>
                <option value="nasal">Nasal</option>
                <option value="inhalada">Inhalada</option>
                <option value="inyectable_sc">Inyectable subcutánea</option>
                <option value="inyectable_im">Inyectable intramuscular</option>
                <option value="rectal">Rectal</option>
              </select>
            </div>
            <div className="rm-col">
              <label className="rm-label">Médico que lo recetó</label>
              <input className="rm-input" name="medico" value={form.medico} onChange={handleChange} placeholder="Ej. Dr. García" maxLength={80} />
            </div>
            <div className="rm-col-12">
              <label className="rm-label">Instrucciones especiales</label>
              <textarea className="rm-input" name="instrucciones" value={form.instrucciones}
                onChange={e => { handleChange(e); setInstruccionesLen(e.target.value.length); }}
                rows={3} maxLength={400} placeholder="Ej. Agitar antes de usar, refrigerar..." style={{ resize: 'vertical' }} />
              <div className="rm-contador">{instruccionesLen} / 400</div>
            </div>
          </div>

          {(alertaGeneral || pacientesError) && <div className="rm-alerta-error">{alertaGeneral || pacientesError}</div>}

          <button type="submit" className="rm-boton-guardar" disabled={guardando}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
              <polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/>
            </svg>
            {guardando ? 'Guardando...' : 'Guardar medicamento'}
          </button>
          <button type="button" className="rm-boton-limpiar" onClick={limpiarFormulario}>Limpiar formulario</button>
        </form>
      </div>
    </div>
  );
}