import { useState } from "react";
import api from "../api";

const IconMedtrack = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
       strokeLinecap="round" strokeLinejoin="round" style={{ width: 22, height: 22, color: "var(--color-fondo)" }}>
    <path d="M12 8v4m0 4h.01M3 12a9 9 0 1 0 18 0A9 9 0 0 0 3 12z" />
  </svg>
);
const IconLogin = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
       strokeLinecap="round" strokeLinejoin="round" style={{ width: 18, height: 18 }}>
    <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
    <polyline points="10 17 15 12 10 7" />
    <line x1="15" y1="12" x2="3" y2="12" />
  </svg>
);
const IconEyeOpen = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
       strokeLinecap="round" strokeLinejoin="round" style={{ width: 18, height: 18 }}>
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);
const IconEyeClosed = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
       strokeLinecap="round" strokeLinejoin="round" style={{ width: 18, height: 18 }}>
    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
    <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
    <line x1="1" y1="1" x2="23" y2="23" />
  </svg>
);

// ── Estilos en objeto (equivalente al <style> del HTML original) ────────────
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
  .login-body {
    margin: 0;
    min-height: 100vh;
    background-color: var(--color-fondo);
    font-family: 'DM Sans', sans-serif;
    color: var(--color-texto);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
    background-image:
      radial-gradient(ellipse 60% 50% at 80% 10%, rgba(45,212,191,.13) 0%, transparent 70%),
      radial-gradient(ellipse 40% 40% at 10% 80%, rgba(45,212,191,.07) 0%, transparent 60%);
  }
  .login-tarjeta {
    background: var(--color-tarjeta);
    border: 1px solid var(--color-borde);
    border-radius: 20px;
    width: 100%;
    max-width: 460px;
    padding: 2.5rem 2.5rem 2rem;
    box-shadow: 0 32px 80px rgba(0,0,0,.5);
    animation: aparecer .45s ease both;
  }
  @keyframes aparecer {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .login-marca { display: flex; align-items: center; gap: .6rem; margin-bottom: 1.75rem; }
  .login-marca-icono {
    width: 38px; height: 38px;
    background: var(--color-menta);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
  }
  .login-marca-nombre { font-family: 'DM Serif Display', serif; font-size: 1.45rem; color: var(--color-texto); }
  .login-titulo   { font-family: 'DM Serif Display', serif; font-size: 1.75rem; margin: 0 0 .25rem; color: var(--color-texto); }
  .login-subtitulo { font-size: .88rem; color: var(--color-texto-suave); margin: 0 0 1.75rem; }
  .login-etiqueta {
    font-size: .82rem; font-weight: 500;
    color: var(--color-texto-suave);
    margin-bottom: .4rem; display: block; letter-spacing: .03em;
  }
  .login-etiqueta .obligatorio { color: var(--color-menta); margin-left: 2px; }
  .login-input {
    background: var(--color-campo);
    border: 1.5px solid var(--color-borde);
    color: var(--color-texto);
    border-radius: 10px;
    padding: .65rem .9rem;
    font-size: .92rem;
    font-family: 'DM Sans', sans-serif;
    transition: border-color .2s, box-shadow .2s;
    width: 100%;
    box-sizing: border-box;
    outline: none;
  }
  .login-input:focus {
    border-color: var(--color-menta);
    box-shadow: 0 0 0 3px rgba(45,212,191,.18);
  }
  .login-input::placeholder { color: #4A6278; }
  .login-input.invalido { border-color: var(--color-error) !important; box-shadow: none !important; }
  .login-input.valido   { border-color: var(--color-exito) !important; box-shadow: none !important; }
  .login-error-campo {
    font-size: .78rem; color: var(--color-error); margin-top: .3rem;
  }
  .login-alerta {
    background: rgba(244,114,106,.12);
    border: 1px solid rgba(244,114,106,.4);
    color: var(--color-error);
    border-radius: 10px;
    padding: .7rem 1rem;
    font-size: .85rem;
    margin-top: 1rem;
  }
  .login-grupo-contrasena { position: relative; }
  .login-grupo-contrasena .login-input { padding-right: 2.8rem; }
  .login-boton-ojo {
    position: absolute; right: .8rem; top: 50%; transform: translateY(-50%);
    background: none; border: none; color: var(--color-texto-suave);
    cursor: pointer; padding: 0; display: flex; align-items: center;
  }
  .login-boton-ojo:hover { color: var(--color-texto); }
  .login-boton-principal {
    background: var(--color-menta); color: var(--color-fondo);
    border: none; border-radius: 12px;
    padding: .75rem; font-size: .95rem; font-weight: 600;
    font-family: 'DM Sans', sans-serif; width: 100%;
    cursor: pointer; display: flex; align-items: center;
    justify-content: center; gap: .5rem;
    transition: background .2s, box-shadow .2s, transform .1s;
    margin-top: 1.25rem;
  }
  .login-boton-principal:hover  { background: var(--color-menta-oscuro); box-shadow: 0 8px 24px rgba(45,212,191,.3); }
  .login-boton-principal:active { transform: scale(.98); }
  .login-boton-principal:disabled { opacity: .6; cursor: not-allowed; }
  .login-pie { text-align: center; margin-top: 1.5rem; font-size: .88rem; color: var(--color-texto-suave); }
  .login-enlace {
    color: var(--color-menta); text-decoration: underline; cursor: pointer;
    background: none; border: none; font-size: inherit; font-family: inherit; padding: 0;
  }
  .login-enlace:hover { color: var(--color-menta-oscuro); }
  .mb-3 { margin-bottom: 1rem; }
  .mb-1 { margin-bottom: .25rem; }
`;

// ── Función de validación de correo ────────────────────────────────────────
const esCorreoValido = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);

// ── Componente principal ────────────────────────────────────────────────────
export default function Login({ onLoginExitoso, onIrARegistro }) {
  /*
    Props que puede recibir este componente desde el componente padre
    (por ejemplo App.jsx que maneja el routing):
    - onLoginExitoso: función que se llama cuando el login fue exitoso,
      recibe { token, usuario } para que el padre los guarde en estado global
    - onIrARegistro: función que navega a la pantalla de registro
  */

  const [correo,       setCorreo]       = useState("");
  const [contrasena,   setContrasena]   = useState("");
  const [mostrarPass,  setMostrarPass]  = useState(false);
  const [errorCorreo,  setErrorCorreo]  = useState("");
  const [errorPass,    setErrorPass]    = useState("");
  const [alertaError,  setAlertaError]  = useState("");
  const [cargando,     setCargando]     = useState(false);
  const [correoTocado, setCorreoTocado] = useState(false);
  const [passTocado,   setPassTocado]   = useState(false);

  // ── Lógica de validación individual ──────────────────────────────────────
  const validarCorreo = (valor) => {
    if (!valor.trim()) return "Ingresa un correo válido.";
    if (!esCorreoValido(valor.trim())) return "Ingresa un correo válido.";
    return "";
  };
  const validarPass = (valor) => {
    if (!valor) return "Ingresa tu contraseña.";
    return "";
  };

  // Clases del input según su estado de validación
  const claseInput = (tocado, error) => {
    if (!tocado) return "login-input";
    return `login-input ${error ? "invalido" : "valido"}`;
  };

  // ── Envío del formulario ──────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    setAlertaError("");

    // Forzar validación de ambos campos
    const errC = validarCorreo(correo);
    const errP = validarPass(contrasena);
    setErrorCorreo(errC);
    setErrorPass(errP);
    setCorreoTocado(true);
    setPassTocado(true);
    if (errC || errP) return;

    setCargando(true);
    try {
      // ✅ usa api.iniciarSesion — sin fetch directo ni URL hardcoded
      const respuesta = await api.iniciarSesion(correo.trim(), contrasena);
      const datos = respuesta.body;
      if (!respuesta.ok) {
        setAlertaError(datos.detail || "Credenciales incorrectas.");
        return;
      }
      // Guardar en localStorage (mismo comportamiento que el HTML original)
      localStorage.setItem("medtrack_token",   datos.token);
      localStorage.setItem("medtrack_usuario", JSON.stringify(datos.usuario));
      // Notificar al componente padre para que actualice el estado global y redirija
      onLoginExitoso?.(datos);
    } catch {
      setAlertaError("No se pudo conectar al servidor.");
    } finally {
      setCargando(false);
    }
  };

  return (
    <>
      {/* Inyectamos los estilos una sola vez */}
      <style>{estilos}</style>

      <div className="login-body">
        <div className="login-tarjeta">
          {/* Logo */}
          <div className="login-marca">
            <div className="login-marca-icono"><IconMedtrack /></div>
            <span className="login-marca-nombre">MedTrack</span>
          </div>

          <h1 className="login-titulo">Bienvenido de nuevo</h1>
          <p className="login-subtitulo">Ingresa tus credenciales para continuar.</p>

          <form onSubmit={handleSubmit} noValidate>
            {/* Campo correo */}
            <div className="mb-3">
              <label className="login-etiqueta" htmlFor="correo">
                Correo electrónico <span className="obligatorio">*</span>
              </label>
              <input
                id="correo"
                type="email"
                className={claseInput(correoTocado, errorCorreo)}
                placeholder="tu@correo.com"
                autoComplete="email"
                value={correo}
                onChange={(e) => {
                  setCorreo(e.target.value);
                  if (correoTocado) setErrorCorreo(validarCorreo(e.target.value));
                }}
                onBlur={() => {
                  setCorreoTocado(true);
                  setErrorCorreo(validarCorreo(correo));
                }}
              />
              {correoTocado && errorCorreo && (
                <div className="login-error-campo">{errorCorreo}</div>
              )}
            </div>

            {/* Campo contraseña */}
            <div className="mb-1">
              <label className="login-etiqueta" htmlFor="contrasena">
                Contraseña <span className="obligatorio">*</span>
              </label>
              <div className="login-grupo-contrasena">
                <input
                  id="contrasena"
                  type={mostrarPass ? "text" : "password"}
                  className={claseInput(passTocado, errorPass)}
                  placeholder="Tu contraseña"
                  autoComplete="current-password"
                  value={contrasena}
                  onChange={(e) => {
                    setContrasena(e.target.value);
                    if (passTocado) setErrorPass(validarPass(e.target.value));
                  }}
                  onBlur={() => {
                    setPassTocado(true);
                    setErrorPass(validarPass(contrasena));
                  }}
                />
                <button
                  type="button"
                  className="login-boton-ojo"
                  onClick={() => setMostrarPass((v) => !v)}
                  aria-label="Mostrar contraseña"
                >
                  {mostrarPass ? <IconEyeClosed /> : <IconEyeOpen />}
                </button>
              </div>
              {passTocado && errorPass && (
                <div className="login-error-campo">{errorPass}</div>
              )}
            </div>

            {alertaError && <div className="login-alerta">{alertaError}</div>}

            <button
              type="submit"
              className="login-boton-principal"
              disabled={cargando}
            >
              <IconLogin />
              {cargando ? "Ingresando…" : "Iniciar sesión"}
            </button>
          </form>

          <p className="login-pie">
            ¿No tienes cuenta?{" "}
            <button className="login-enlace" onClick={onIrARegistro}>
              Regístrate aquí
            </button>
          </p>
        </div>
      </div>
    </>
  );
}