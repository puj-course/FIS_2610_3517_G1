import { useNavigate, useLocation } from 'react-router-dom';

const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
  .layout-root { display: flex; min-height: 100vh; background: #0F1B2D; font-family: 'DM Sans', sans-serif; color: #E2EAF4; }
  .layout-sidebar {
    width: 210px; min-height: 100vh; background: #111c2d; border-right: 1px solid #1e2d3d;
    display: flex; flex-direction: column; padding: 1.5rem 0; position: fixed; top: 0; left: 0; z-index: 100;
  }
  .layout-marca { display: flex; align-items: center; gap: .6rem; padding: 0 1.2rem 1.5rem; border-bottom: 1px solid #1e2d3d; margin-bottom: 1.2rem; }
  .layout-marca-icono { width: 32px; height: 32px; background: #2DD4BF; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
  .layout-marca-icono svg { width: 18px; height: 18px; color: #0F1B2D; }
  .layout-marca-nombre { font-family: 'DM Serif Display', serif; font-size: 1.2rem; color: #E2EAF4; }
  .layout-section-label { font-size: .68rem; text-transform: uppercase; letter-spacing: .08em; color: #4A6278; padding: .4rem 1.2rem .2rem; margin-top: .5rem; }
  .layout-nav-item {
    display: flex; align-items: center; gap: .6rem; padding: .55rem 1.2rem;
    color: #7A95B0; font-size: .88rem; cursor: pointer; border-radius: 0;
    transition: background .15s, color .15s; border: none; background: none; width: 100%; text-align: left;
    border-left: 3px solid transparent;
  }
  .layout-nav-item:hover { background: rgba(45,212,191,.07); color: #E2EAF4; }
  .layout-nav-item.activo { background: rgba(45,212,191,.12); color: #2DD4BF; border-left-color: #2DD4BF; }
  .layout-nav-item svg { width: 16px; height: 16px; flex-shrink: 0; }
  .layout-spacer { flex: 1; }
  .layout-user {
    padding: .8rem 1.2rem; border-top: 1px solid #1e2d3d; margin-top: .5rem;
  }
  .layout-user-info { display: flex; align-items: center; gap: .6rem; margin-bottom: .6rem; }
  .layout-avatar {
    width: 32px; height: 32px; background: rgba(45,212,191,.2); border: 1.5px solid #2DD4BF;
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: .8rem; font-weight: 700; color: #2DD4BF; flex-shrink: 0;
  }
  .layout-user-nombre { font-size: .85rem; font-weight: 500; line-height: 1.2; }
  .layout-user-rol { font-size: .72rem; color: #4A6278; }
  .layout-btn-salir {
    display: flex; align-items: center; gap: .5rem; width: 100%;
    background: transparent; border: 1px solid #1e2d3d; color: #7A95B0;
    border-radius: 8px; padding: .4rem .8rem; font-size: .8rem; font-family: 'DM Sans', sans-serif;
    cursor: pointer; transition: border-color .2s, color .2s;
  }
  .layout-btn-salir:hover { border-color: #F4726A; color: #F4726A; }
  .layout-btn-salir svg { width: 14px; height: 14px; }
  .layout-content { margin-left: 210px; flex: 1; min-height: 100vh; }
`;

const NAV = [
  {
    seccion: 'PRINCIPAL',
    items: [
      { label: 'Inicio', ruta: '/pacientes', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg> },
      { label: 'Panel del día', ruta: '/panel-dia', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg> },
    ]
  },
  {
    seccion: 'PACIENTES',
    items: [
      { label: 'Lista de pacientes', ruta: '/pacientes', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg> },
      { label: 'Nuevo paciente', ruta: '/registrar-paciente', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg> },
    ]
  },
  {
    seccion: 'MEDICAMENTOS',
    items: [
      { label: 'Ver medicamentos', ruta: '/medicamentos', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg> },
      { label: 'Registrar medicamento', ruta: '/registrar-medicamento', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> },
    ]
  },
  {
    seccion: 'SEGUIMIENTO',
    items: [
      { label: 'Marcar tomas', ruta: '/tomas', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg> },
      { label: 'Historial de tomas', ruta: '/historial', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg> },
    ]
  },
  {
    seccion: 'CALIDAD',
    items: [
      { label: 'Métricas de calidad', ruta: '/metricas-calidad', icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-7"/><path d="M7 19v-4"/><path d="M12 19v-8"/><path d="M17 19v-6"/></svg> },
    ]
  },
];

export default function Layout({ usuario, onCerrarSesion, children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const inicial = (usuario?.username || usuario?.nombre || 'U')[0].toUpperCase();
  const nombre = usuario?.username || usuario?.nombre || 'Usuario';
  const rol = usuario?.rol || usuario?.role || 'Enfermero/a';

  return (
    <>
      <style>{CSS}</style>
      <div className="layout-root">
        <aside className="layout-sidebar">
          <div className="layout-marca">
            <div className="layout-marca-icono">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
            </div>
            <span className="layout-marca-nombre">MedTrack</span>
          </div>

          {NAV.map(({ seccion, items }) => (
            <div key={seccion}>
              <div className="layout-section-label">{seccion}</div>
              {items.map(({ label, ruta, icon }) => (
                <button
                  key={ruta + label}
                  className={`layout-nav-item${location.pathname === ruta ? ' activo' : ''}`}
                  onClick={() => navigate(ruta)}
                >
                  {icon}{label}
                </button>
              ))}
            </div>
          ))}

          <div className="layout-spacer" />

          <div className="layout-user">
            <div className="layout-user-info">
              <div className="layout-avatar">{inicial}</div>
              <div>
                <div className="layout-user-nombre">{nombre}</div>
                <div className="layout-user-rol">{rol}</div>
              </div>
            </div>
            <button className="layout-btn-salir" onClick={onCerrarSesion}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
              Cerrar sesión
            </button>
          </div>
        </aside>
        <main className="layout-content">{children}</main>
      </div>
    </>
  );
}
