import { useState } from "react";

const estilos = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
  :root {
    --color-menta: #2DD4BF; --color-menta-oscuro: #0F9D8A;
    --color-fondo: #0F1B2D; --color-campo: #1E2D3D; --color-tarjeta: #162030;
    --color-borde: #243447; --color-texto: #E2EAF4; --color-texto-suave: #7A95B0;
    --color-error: #F4726A; --color-exito: #4ADE80;
  }
  *, *::before, *::after { box-sizing: border-box; }
  .rg-body {
    margin: 0; min-height: 100vh; background-color: var(--color-fondo);
    font-family: 'DM Sans', sans-serif; color: var(--color-texto);
    display: flex; align-items: center; justify-content: center;
    padding: 2rem 1rem;
    background-image:
      radial-gradient(ellipse 60% 50% at 80% 10%, rgba(45,212,191,.13) 0%, transparent 70%),
      radial-gradient(ellipse 40% 40% at 10% 80%, rgba(45,212,191,.07) 0%, transparent 60%);
  }
  .rg-tarjeta {
    background: var(--color-tarjeta); border: 1px solid var(--color-borde);
    border-radius: 20px; width: 100%; max-width: 460px;
    padding: 2.5rem 2.5rem 2rem; box-shadow: 0 32px 80px rgba(0,0,0,.5);
    animation: rg-aparecer .45s ease both;
  }
  @keyframes rg-aparecer {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .rg-marca { display: flex; align-items: center; gap: .6rem; margin-bottom: 1.75rem; }
  .rg-marca-icono {
    width: 38px; height: 38px; background: var(--color-menta);
    border-radius: 10px; display: flex; align-items: center; justify-content: center;
  }
  .rg-marca-nombre { font-family: 'DM Serif Display', serif; font-size: 1.45rem; }
  .rg-titulo    { font-family: 'DM Serif Display', serif; font-size: 1.75rem; margin: 0 0 .25rem; }
  .rg-subtitulo { font-size: .88rem; color: var(--color-texto-suave); margin: 0 0 1.75rem; }
  .rg-etiqueta  { font-size: .82rem; font-weight: 500; color: var(--color-texto-suave); margin-bottom: .4rem; display: block; }
  .rg-etiqueta .obligatorio { color: var(--color-menta); }
  .rg-input, .rg-select {
    background: var(--color-campo); border: 1.5px solid var(--color-borde);
    color: var(--color-texto); border-radius: 10px;
    padding: .65rem .9rem; font-size: .92rem; font-family: 'DM Sans', sans-serif;
    transition: border-color .2s, box-shadow .2s; width: 100%; box-sizing: border-box;
  }
  .rg-input:focus, .rg-select:focus {
    background: var(--color-campo); border-color: var(--color-menta);
    color: var(--color-texto); box-shadow: 0 0 0 3px rgba(45,212,191,.18); outline: none;
  }
  .rg-input::placeholder { color: #4A6278; }
  .rg-select option { background: var(--color-campo); }
  .rg-invalido { border-color: var(--color-error) !important; box-shadow: none !important; }
  .rg-valido   { border-color: var(--color-exito) !important; box-shadow: none !important; }
  .rg-msg-error { font-size: .78rem; color: var(--color-error); margin-top: .3rem; }
  .rg-alerta-error {
    background: rgba(244,114,106,.12); border: 1px solid rgba(244,114,106,.4);
    color: var(--color-error); border-radius: 10px;
    padding: .7rem 1rem; font-size: .85rem; margin-top: 1rem;
  }
  .rg-alerta-exito {
    background: rgba(74,222,128,.12); border: 1px solid rgba(74,222,128,.4);
    color: var(--color-exito); border-radius: 10px;
    padding: .7rem 1rem; font-size: .85rem; margin-top: 1rem;
  }
  .rg-boton {
    background: var(--color-menta); color: var(--color-fondo);
    border: none; border-radius: 12px; padding: .75rem;
    font-size: .95rem; font-weight: 600; font-family: 'DM Sans', sans-serif;
    width: 100%; cursor: pointer; display: flex; align-items: center;
    justify-content: center; gap: .5rem;
    transition: background .2s, box-shadow .2s, transform .1s; margin-top: 1.25rem;
  }
  .rg-boton:hover  { background: var(--color-menta-oscuro); box-shadow: 0 8px 24px rgba(45,212,191,.3); }
  .rg-boton:active { transform: scale(.98); }
  .rg-boton:disabled { opacity: .6; cursor: not-allowed; }
  .rg-pie { text-align: center; margin-top: 1.5rem; font-size: .88rem; color: var(--color-texto-suave); }
  .rg-enlace {
    color: var(--color-menta); text-decoration: underline; cursor: pointer;
    background: none; border: none; font-size: inherit; font-family: inherit; padding: 0;
  }
  .rg-enlace:hover { color: var(--color-menta-oscuro); }
  .mb-3 { margin-bottom: 1rem; }
`;

const esEmail = v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);

export default function Registro({ onIrALogin }) {
  const [form, setForm] = useState({ nombre: "", correo: "", contrasena: "", confirmar: "", rol: "" });
  const [tocados, setTocados] = useState({});
  const [alertaError, setAlertaError] = useState("");
  const [alertaExito, setAlertaExito] = useState("");
  const [cargando, setCargando] = useState(false);

  const validarCampo = (campo, valor, todos = form) => {
    if (!valor.trim()) return true;
    if (campo === "correo" && !esEmail(valor.trim())) return true;
    if (campo === "contrasena" && valor.length < 6) return true;
    if (campo === "confirmar" && valor !== todos.contrasena) return true;
    return false;
  };

  const errores = {
    nombre:    validarCampo("nombre",    form.nombre),
    correo:    validarCampo("correo",    form.correo),
    contrasena: validarCampo("contrasena", form.contrasena),
    confirmar: validarCampo("confirmar", form.confirmar),
    rol:       !form.rol,
  };

  const cls = (campo) => {
    if (!tocados[campo]) return "rg-input";
    return `rg-input ${errores[campo] ? "rg-invalido" : "rg-valido"}`;
  };
  const clsSel = (campo) => {
    if (!tocados[campo]) return "rg-select";
    return `rg-select ${errores[campo] ? "rg-invalido" : "rg-valido"}`;
  };

  const touch = (campo) => setTocados(t => ({ ...t, [campo]: true }));
  const set   = (campo, val) => setForm(f => ({ ...f, [campo]: val }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setAlertaError(""); setAlertaExito("");
    const allTocados = { nombre: true, correo: true, contrasena: true, confirmar: true, rol: true };
    setTocados(allTocados);
    if (Object.values(errores).some(Boolean)) return;
    setCargando(true);
    try {
      const res = await fetch("http://localhost:8000/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre: form.nombre.trim(), username: form.correo.trim(), password: form.contrasena, rol: form.rol }),
      });
      const datos = await res.json();
      if (!res.ok) { setAlertaError(datos.detail); return; }
      setAlertaExito("¡Cuenta creada exitosamente! Redirigiendo al login...");
      setTimeout(() => onIrALogin?.(), 2000);
    } catch {
      setAlertaError("No se pudo conectar al servidor.");
    } finally {
      setCargando(false);
    }
  };

  return (
    <>
      <style>{estilos}</style>
      <div className="rg-body">
        <div className="rg-tarjeta">
          <div className="rg-marca">
            <div className="rg-marca-icono">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ width: 22, height: 22, color: "var(--color-fondo)" }}>
                <path d="M12 8v4m0 4h.01M3 12a9 9 0 1 0 18 0A9 9 0 0 0 3 12z"/>
              </svg>
            </div>
            <span className="rg-marca-nombre">MedTrack</span>
          </div>
          <h1 className="rg-titulo">Crear cuenta</h1>
          <p className="rg-subtitulo">Completa los datos para registrarte en MedTrack.</p>

          <form onSubmit={handleSubmit} noValidate>
            {[
              { id: "nombre",    label: "Nombre completo",       type: "text",     ph: "Tu nombre completo" },
              { id: "correo",    label: "Correo electrónico",    type: "email",    ph: "tu@correo.com" },
              { id: "contrasena",label: "Contraseña",            type: "password", ph: "Mínimo 6 caracteres" },
              { id: "confirmar", label: "Confirmar contraseña",  type: "password", ph: "Repite tu contraseña" },
            ].map(({ id, label, type, ph }) => (
              <div key={id} className="mb-3">
                <label className="rg-etiqueta" htmlFor={id}>{label} <span className="obligatorio">*</span></label>
                <input
                  id={id} type={type} className={cls(id)} placeholder={ph}
                  value={form[id]}
                  onChange={e => { set(id, e.target.value); if (tocados[id]) touch(id); }}
                  onBlur={() => touch(id)}
                />
                {tocados[id] && errores[id] && (
                  <div className="rg-msg-error">
                    {id === "nombre" && "Ingresa tu nombre completo."}
                    {id === "correo" && "Ingresa un correo válido."}
                    {id === "contrasena" && "La contraseña debe tener mínimo 6 caracteres."}
                    {id === "confirmar" && "Las contraseñas no coinciden."}
                  </div>
                )}
              </div>
            ))}

            <div className="mb-3">
              <label className="rg-etiqueta" htmlFor="rol">Rol <span className="obligatorio">*</span></label>
              <select id="rol" className={clsSel("rol")} value={form.rol}
                onChange={e => { set("rol", e.target.value); touch("rol"); }}
                onBlur={() => touch("rol")}>
                <option value="" disabled>Selecciona tu rol...</option>
                <option value="cuidador">Cuidador</option>
              </select>
              {tocados.rol && errores.rol && <div className="rg-msg-error">Selecciona un rol.</div>}
            </div>

            {alertaError && <div className="rg-alerta-error">{alertaError}</div>}
            {alertaExito && <div className="rg-alerta-exito">{alertaExito}</div>}

            <button type="submit" className="rg-boton" disabled={cargando}>
              {cargando ? "Creando cuenta..." : "Crear cuenta"}
            </button>
          </form>

          <p className="rg-pie">
            ¿Ya tienes cuenta?{" "}
            <button className="rg-enlace" onClick={onIrALogin}>Inicia sesión aquí</button>
          </p>
        </div>
      </div>
    </>
  );
}