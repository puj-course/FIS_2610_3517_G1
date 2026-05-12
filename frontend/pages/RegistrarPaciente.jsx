// src/pages/RegistrarPaciente.jsx
import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

  .rp-root {
    margin: 0;
    min-height: 100vh;
    background-color: #0F1B2D;
    font-family: 'DM Sans', sans-serif;
    color: #E2EAF4;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
    background-image:
      radial-gradient(ellipse 60% 50% at 80% 10%, rgba(45,212,191,.12) 0%, transparent 70%),
      radial-gradient(ellipse 40% 40% at 10% 80%, rgba(45,212,191,.07) 0%, transparent 60%);
  }
  .rp-tarjeta {
    background: #162030;
    border: 1px solid #243447;
    border-radius: 20px;
    width: 100%;
    max-width: 640px;
    padding: 2.5rem 2.5rem 2rem;
    box-shadow: 0 32px 80px rgba(0,0,0,.5);
    animation: rp-aparecer .5s ease both;
  }
  @keyframes rp-aparecer {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .rp-marca { display: flex; align-items: center; gap: .6rem; margin-bottom: 1.5rem; }
  .rp-marca-icono {
    width: 36px; height: 36px;
    background: #2DD4BF;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
  }
  .rp-marca-icono svg { width: 20px; height: 20px; color: #0F1B2D; }
  .rp-marca-nombre { font-family: 'DM Serif Display', serif; font-size: 1.4rem; }
  .rp-titulo { font-family: 'DM Serif Display', serif; font-size: 1.75rem; margin: 0 0 .3rem; }
  .rp-subtitulo { font-size: .9rem; color: #7A95B0; margin: 0 0 2rem; }

  .rp-separador {
    display: flex; align-items: center; gap: .75rem;
    margin: 1.5rem 0 1.25rem;
    color: #7A95B0; font-size: .78rem;
    text-transform: uppercase; letter-spacing: .08em;
  }
  .rp-separador::before, .rp-separador::after {
    content: ''; flex: 1; height: 1px; background: #243447;
  }

  .rp-row { display: flex; flex-wrap: wrap; gap: .75rem; }
  .rp-col-6 { flex: 1 1 calc(50% - .375rem); min-width: 200px; }
  .rp-col-12 { flex: 1 1 100%; }

  .rp-label {
    font-size: .82rem; font-weight: 500;
    color: #7A95B0; display: block; margin-bottom: .4rem;
  }
  .rp-req { color: #2DD4BF; margin-left: 2px; }

  .rp-input, .rp-select, .rp-textarea {
    width: 100%;
    background: #1E2D3D;
    border: 1.5px solid #243447;
    color: #E2EAF4;
    border-radius: 10px;
    padding: .65rem .9rem;
    font-size: .92rem;
    font-family: 'DM Sans', sans-serif;
    transition: border-color .2s, box-shadow .2s;
    box-sizing: border-box;
  }
  .rp-input:focus, .rp-select:focus, .rp-textarea:focus {
    outline: none;
    border-color: #2DD4BF;
    box-shadow: 0 0 0 3px rgba(45,212,191,.18);
  }
  .rp-input::placeholder, .rp-textarea::placeholder { color: #4A6278; }
  .rp-select option { background: #1E2D3D; }

  .rp-invalido { border-color: #F4726A !important; box-shadow: none !important; }
  .rp-valido   { border-color: #4ADE80 !important; box-shadow: none !important; }

  .rp-error-msg {
    font-size: .78rem; color: #F4726A; margin-top: .3rem;
  }
  .rp-contador {
    font-size: .75rem; color: #7A95B0; text-align: right; margin-top: .2rem;
  }

  .rp-boton-guardar {
    background: #2DD4BF; color: #0F1B2D;
    border: none; border-radius: 12px;
    padding: .75rem 2rem; font-size: .95rem; font-weight: 600;
    font-family: 'DM Sans', sans-serif;
    width: 100%; cursor: pointer;
    display: flex; align-items: center; justify-content: center; gap: .5rem;
    transition: background .2s, transform .1s, box-shadow .2s;
    margin-top: 1.5rem;
  }
  .rp-boton-guardar:hover { background: #0F9D8A; box-shadow: 0 8px 24px rgba(45,212,191,.3); }
  .rp-boton-guardar:active { transform: scale(.98); }
  .rp-boton-guardar:disabled { opacity: .6; cursor: not-allowed; }
  .rp-boton-guardar svg { width: 18px; height: 18px; }

  .rp-boton-limpiar {
    background: transparent; color: #7A95B0;
    border: 1.5px solid #243447; border-radius: 12px;
    padding: .65rem 1.5rem; font-size: .88rem;
    font-family: 'DM Sans', sans-serif;
    width: 100%; cursor: pointer;
    transition: border-color .2s, color .2s; margin-top: .75rem;
  }
  .rp-boton-limpiar:hover { border-color: #7A95B0; color: #E2EAF4; }

  .rp-link-volver {
    display: block; text-align: center; margin-top: .75rem;
    color: #7A95B0; font-size: .88rem;
    text-decoration: underline; cursor: pointer;
    background: none; border: none; font-family: 'DM Sans', sans-serif;
    width: 100%;
  }

  /* Notificaciones flotantes */
  .rp-notif-ctn {
    position: fixed; top: 1.5rem; right: 1.5rem; z-index: 9999;
    display: flex; flex-direction: column; gap: .5rem;
  }
  .rp-notif {
    background: #162030; border: 1px solid #4ADE80;
    border-radius: 12px; padding: .9rem 1.2rem;
    display: flex; align-items: center; gap: .75rem;
    box-shadow: 0 8px 32px rgba(0,0,0,.4);
    animation: rp-deslizar .35s ease both; font-size: .88rem;
    min-width: 260px;
  }
  .rp-notif.error { border-color: #F4726A; }
  @keyframes rp-deslizar {
    from { opacity: 0; transform: translateX(40px); }
    to   { opacity: 1; transform: translateX(0); }
  }

  @media (max-width: 480px) {
    .rp-tarjeta { padding: 1.75rem 1.25rem 1.5rem; }
    .rp-col-6 { flex: 1 1 100%; }
  }
`;

// ── Valores iniciales del formulario ────────────────────────────────────────
const FORM_INICIAL = {
  nombres: '',
  apellidos: '',
  fecha_nacimiento: '',
  genero: '',
  tipo_documento: '',
  numero_documento: '',
  telefono_contacto: '',
  eps_aseguradora: '',
  diagnostico_principal: '',
  alergias: '',
  observaciones: '',
};

// ── Hook para las notificaciones flotantes ──────────────────────────────────
// Reemplaza la función mostrarNotificacion() del HTML original
function useNotificaciones() {
  const [notifs, setNotifs] = useState([]);

  function mostrar(mensaje, tipo = 'exito') {
    const id = Date.now();
    setNotifs((prev) => [...prev, { id, mensaje, tipo }]);
    setTimeout(() => {
      setNotifs((prev) => prev.filter((n) => n.id !== id));
    }, 3500);
  }

  return { notifs, mostrar };
}

// ── Lógica de validación (equivale a validarCampo() del HTML) ───────────────
function validarCampoLogica(nombre, valor, form) {
  const obligatorios = ['nombres', 'apellidos', 'fecha_nacimiento', 'genero', 'tipo_documento', 'numero_documento'];

  if (obligatorios.includes(nombre) && !valor.trim()) {
    return 'Este campo es obligatorio.';
  }
  if (nombre === 'fecha_nacimiento' && valor) {
    const fecha = new Date(valor);
    if (isNaN(fecha) || fecha > new Date()) return 'La fecha no puede ser futura.';
    const edad = (new Date() - fecha) / (1000 * 60 * 60 * 24 * 365.25);
    if (edad > 130) return 'Ingresa una fecha de nacimiento válida.';
  }
  if (nombre === 'telefono_contacto' && valor.trim()) {
    if (!/^[0-9+\-\s()]{7,15}$/.test(valor.trim())) return 'Teléfono inválido (mínimo 7 dígitos).';
  }
  if (nombre === 'numero_documento' && valor.trim()) {
    if (!/^[A-Za-z0-9\-]+$/.test(valor.trim())) return 'Solo letras, números y guiones.';
  }
  return ''; // sin error
}

export default function RegistrarPaciente() {
  const navigate = useNavigate();
  const { notifs, mostrar } = useNotificaciones();

  const [form, setForm]         = useState(FORM_INICIAL);
  const [errores, setErrores]   = useState({});   // { campo: 'mensaje de error' }
  const [tocados, setTocados]   = useState({});   // { campo: true } — si el usuario ya lo tocó
  const [cargando, setCargando] = useState(false);

  const fechaHoy = new Date().toISOString().split('T')[0];

  // Maneja cualquier cambio en inputs/selects/textareas
  // Reemplaza los addEventListener('input') e 'blur' del HTML
  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));

    // Si el campo ya fue tocado (blur), revalidamos en tiempo real
    if (tocados[name]) {
      const msg = validarCampoLogica(name, value, form);
      setErrores((prev) => ({ ...prev, [name]: msg }));
    }
  }

  function handleBlur(e) {
    const { name, value } = e.target;
    setTocados((prev) => ({ ...prev, [name]: true }));
    const msg = validarCampoLogica(name, value, form);
    setErrores((prev) => ({ ...prev, [name]: msg }));
  }

  // Devuelve la clase CSS del campo según su estado de validación
  function claseInput(nombre) {
    if (!tocados[nombre]) return 'rp-input';
    return errores[nombre] ? 'rp-input rp-invalido' : 'rp-input rp-valido';
  }
  function claseSelect(nombre) {
    if (!tocados[nombre]) return 'rp-select';
    return errores[nombre] ? 'rp-select rp-invalido' : 'rp-select rp-valido';
  }

  // Valida todos los campos antes de enviar — equivale al forEach del submit
  function validarTodo() {
    const camposAValidar = Object.keys(FORM_INICIAL);
    const nuevosErrores = {};
    const nuevosTocados = {};
    let valido = true;

    camposAValidar.forEach((nombre) => {
      nuevosTocados[nombre] = true;
      const msg = validarCampoLogica(nombre, form[nombre], form);
      nuevosErrores[nombre] = msg;
      if (msg) valido = false;
    });

    setTocados(nuevosTocados);
    setErrores(nuevosErrores);
    return valido;
  }

  async function handleSubmit(e) {
    e.preventDefault();

    if (!validarTodo()) {
      mostrar('Revisa los campos marcados en rojo.', 'error');
      return;
    }

    setCargando(true);
    try {
      // Convertimos fecha de yyyy-mm-dd a mm/dd/yyyy (formato que espera el backend)
      const datos = { ...form };
      if (datos.fecha_nacimiento) {
        const [y, m, d] = datos.fecha_nacimiento.split('-');
        datos.fecha_nacimiento = `${m}/${d}/${y}`;
      }
      // El campo en el backend se llama 'alergias_conocidas', ajustamos el nombre
      datos.alergias_conocidas = datos.alergias;
      delete datos.alergias;

      const resultado = await api.registrarPaciente(datos);

      if (!resultado.ok) {
        const detalle = resultado.body?.detail;
        const msg = Array.isArray(detalle) ? detalle.join(' | ') : (detalle || 'Error al guardar.');
        mostrar(msg, 'error');
      } else {
        mostrar(`Paciente "${form.nombres} ${form.apellidos}" registrado correctamente.`);
        setForm(FORM_INICIAL);
        setErrores({});
        setTocados({});
      }
    } catch {
      mostrar('Error de conexión con el servidor.', 'error');
    } finally {
      setCargando(false);
    }
  }

  function limpiarFormulario() {
    setForm(FORM_INICIAL);
    setErrores({});
    setTocados({});
  }

  return (
    <>
      <style>{CSS}</style>

      {/* Notificaciones flotantes */}
      <div className="rp-notif-ctn">
        {notifs.map((n) => (
          <div key={n.id} className={`rp-notif${n.tipo === 'error' ? ' error' : ''}`}>
            <span>{n.tipo === 'exito' ? '✓' : '⚠'}</span>
            <span>{n.mensaje}</span>
          </div>
        ))}
      </div>

      <div className="rp-root">
        <div className="rp-tarjeta">

          {/* Logo */}
          <div className="rp-marca">
            <div className="rp-marca-icono">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 8v4m0 4h.01M3 12a9 9 0 1 0 18 0A9 9 0 0 0 3 12z"/>
              </svg>
            </div>
            <span className="rp-marca-nombre">MedTrack</span>
          </div>

          <h1 className="rp-titulo">Registro de Paciente</h1>
          <p className="rp-subtitulo">Completa la información para comenzar el seguimiento del tratamiento.</p>

          <form onSubmit={handleSubmit} noValidate>

            {/* ── Datos personales ── */}
            <div className="rp-separador">Datos personales</div>
            <div className="rp-row">

              <div className="rp-col-6">
                <label className="rp-label">Nombres <span className="rp-req">*</span></label>
                <input
                  className={claseInput('nombres')}
                  name="nombres" type="text"
                  placeholder="Ej. María Elena"
                  maxLength={60} autoComplete="off"
                  value={form.nombres}
                  onChange={handleChange} onBlur={handleBlur}
                />
                {tocados.nombres && errores.nombres && (
                  <div className="rp-error-msg">{errores.nombres}</div>
                )}
              </div>

              <div className="rp-col-6">
                <label className="rp-label">Apellidos <span className="rp-req">*</span></label>
                <input
                  className={claseInput('apellidos')}
                  name="apellidos" type="text"
                  placeholder="Ej. Gómez Torres"
                  maxLength={60} autoComplete="off"
                  value={form.apellidos}
                  onChange={handleChange} onBlur={handleBlur}
                />
                {tocados.apellidos && errores.apellidos && (
                  <div className="rp-error-msg">{errores.apellidos}</div>
                )}
              </div>

              <div className="rp-col-6">
                <label className="rp-label">Fecha de nacimiento <span className="rp-req">*</span></label>
                <input
                  className={claseInput('fecha_nacimiento')}
                  name="fecha_nacimiento" type="date"
                  max={fechaHoy}
                  value={form.fecha_nacimiento}
                  onChange={handleChange} onBlur={handleBlur}
                />
                {tocados.fecha_nacimiento && errores.fecha_nacimiento && (
                  <div className="rp-error-msg">{errores.fecha_nacimiento}</div>
                )}
              </div>

              <div className="rp-col-6">
                <label className="rp-label">Género <span className="rp-req">*</span></label>
                <select
                  className={claseSelect('genero')}
                  name="genero"
                  value={form.genero}
                  onChange={handleChange} onBlur={handleBlur}
                >
                  <option value="">Selecciona…</option>
                  <option value="Femenino">Femenino</option>
                  <option value="Masculino">Masculino</option>
                  <option value="Otro">Otro</option>
                  <option value="no_especifica">Prefiero no decirlo</option>
                </select>
                {tocados.genero && errores.genero && (
                  <div className="rp-error-msg">{errores.genero}</div>
                )}
              </div>

              <div className="rp-col-6">
                <label className="rp-label">Tipo de documento <span className="rp-req">*</span></label>
                <select
                  className={claseSelect('tipo_documento')}
                  name="tipo_documento"
                  value={form.tipo_documento}
                  onChange={handleChange} onBlur={handleBlur}
                >
                  <option value="">Selecciona…</option>
                  <option value="CC">Cédula de ciudadanía</option>
                  <option value="TI">Tarjeta de identidad</option>
                  <option value="pasaporte">Pasaporte</option>
                  <option value="ce">Cédula de extranjería</option>
                  <option value="rc">Registro civil</option>
                </select>
                {tocados.tipo_documento && errores.tipo_documento && (
                  <div className="rp-error-msg">{errores.tipo_documento}</div>
                )}
              </div>

              <div className="rp-col-6">
                <label className="rp-label">Número de documento <span className="rp-req">*</span></label>
                <input
                  className={claseInput('numero_documento')}
                  name="numero_documento" type="text"
                  placeholder="Ej. 1020304050"
                  maxLength={20} autoComplete="off" inputMode="numeric"
                  value={form.numero_documento}
                  onChange={handleChange} onBlur={handleBlur}
                />
                {tocados.numero_documento && errores.numero_documento && (
                  <div className="rp-error-msg">{errores.numero_documento}</div>
                )}
              </div>

            </div>

            {/* ── Información médica y contacto ── */}
            <div className="rp-separador">Información médica y contacto</div>
            <div className="rp-row">

              <div className="rp-col-6">
                <label className="rp-label">Teléfono de contacto</label>
                <input
                  className={claseInput('telefono_contacto')}
                  name="telefono_contacto" type="tel"
                  placeholder="Ej. 3001234567"
                  maxLength={15} inputMode="tel"
                  value={form.telefono_contacto}
                  onChange={handleChange} onBlur={handleBlur}
                />
                {tocados.telefono_contacto && errores.telefono_contacto && (
                  <div className="rp-error-msg">{errores.telefono_contacto}</div>
                )}
              </div>

              <div className="rp-col-6">
                <label className="rp-label">EPS / Aseguradora</label>
                <input
                  className="rp-input"
                  name="eps_aseguradora" type="text"
                  placeholder="Ej. Sura, Sanitas…"
                  maxLength={60}
                  value={form.eps_aseguradora}
                  onChange={handleChange}
                />
              </div>

              <div className="rp-col-12">
                <label className="rp-label">Diagnóstico principal</label>
                <input
                  className="rp-input"
                  name="diagnostico_principal" type="text"
                  placeholder="Ej. Hipertensión arterial"
                  maxLength={120}
                  value={form.diagnostico_principal}
                  onChange={handleChange}
                />
              </div>

              <div className="rp-col-12">
                <label className="rp-label">Alergias conocidas</label>
                <input
                  className="rp-input"
                  name="alergias" type="text"
                  placeholder="Ej. Penicilina, aspirina… o 'Ninguna'"
                  maxLength={200}
                  value={form.alergias}
                  onChange={handleChange}
                />
              </div>

              <div className="rp-col-12">
                <label className="rp-label">Observaciones adicionales</label>
                <textarea
                  className="rp-textarea"
                  name="observaciones"
                  rows={3} maxLength={400}
                  placeholder="Notas relevantes para el cuidado del paciente…"
                  value={form.observaciones}
                  onChange={handleChange}
                />
                {/* Contador de caracteres — antes era un span actualizado con JS */}
                <div className="rp-contador">{form.observaciones.length} / 400</div>
              </div>

            </div>

            {/* Botones */}
            <button type="submit" className="rp-boton-guardar" disabled={cargando}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                <polyline points="17 21 17 13 7 13 7 21"/>
                <polyline points="7 3 7 8 15 8"/>
              </svg>
              {cargando ? 'Guardando…' : 'Guardar paciente'}
            </button>

            <button type="button" className="rp-boton-limpiar" onClick={limpiarFormulario}>
              Limpiar formulario
            </button>

            <button type="button" className="rp-link-volver" onClick={() => navigate('/dashboard')}>
              ← Volver al dashboard
            </button>

          </form>
        </div>
      </div>
    </>
  );
}