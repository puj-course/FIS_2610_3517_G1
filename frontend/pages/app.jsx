import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// ── Páginas ──────────────────────────────────────────────────────────────────
import Login            from './pages/Login';
import Registro         from './pages/Registro';
import ListarPacientes  from './pages/ListarPacientes';
import RegistrarPaciente from './pages/RegistrarPaciente';
import ResumenPaciente  from './pages/ResumenPaciente';
import Medicamentos     from './pages/Medicamentos';
import RegistroMedicamento from './pages/RegistroMedicamento';
import ListaRecordatorios  from './pages/ListaRecordatorios';
import Recordatorios    from './pages/Recordatorios';
import HistorialTomas   from './pages/HistorialTomas';
import Tomas            from './pages/Tomas';
import PanelDia         from './pages/PanelDia';
import ListaTomas       from './pages/ListaTomas';

// ── Componente de ruta protegida ─────────────────────────────────────────────
function RutaProtegida({ usuario, children }) {
  if (!usuario) return <Navigate to="/login" replace />;
  return children;
}

// ── App principal ────────────────────────────────────────────────────────────
export default function App() {
  // Estado global de sesión
  // MongoDB: usuario.id es un string ObjectId
  const [usuario, setUsuario] = useState(() => {
    try {
      const raw = localStorage.getItem('medtrack_usuario');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });

  function handleLoginExitoso(datos) {
    // datos = { token, usuario }
    // El usuario de MongoDB puede venir con _id; lo normalizamos a "id"
    const u = datos.usuario || {};
    if (u._id && !u.id) u.id = u._id;
    localStorage.setItem('medtrack_token',   datos.token   || '');
    localStorage.setItem('medtrack_usuario', JSON.stringify(u));
    setUsuario(u);
  }

  function handleCerrarSesion() {
    localStorage.removeItem('medtrack_token');
    localStorage.removeItem('medtrack_usuario');
    setUsuario(null);
  }

  // pacienteId activo para componentes que lo necesitan como prop
  // MongoDB: es un string ObjectId
  const [pacienteActivo, setPacienteActivo] = useState(null);
  const [nombrePacienteActivo, setNombrePacienteActivo] = useState('Paciente');

  return (
    <BrowserRouter>
      <Routes>

        {/* ── Públicas ── */}
        <Route
          path="/login"
          element={
            usuario
              ? <Navigate to="/pacientes" replace />
              : <Login
                  onLoginExitoso={handleLoginExitoso}
                  onIrARegistro={() => window.location.href = '/registro'}
                />
          }
        />

        <Route
          path="/registro"
          element={
            usuario
              ? <Navigate to="/pacientes" replace />
              : <Registro onIrALogin={() => window.location.href = '/login'} />
          }
        />

        {/* ── Raíz ── */}
        <Route
          path="/"
          element={<Navigate to={usuario ? '/pacientes' : '/login'} replace />}
        />

        {/* ── Protegidas ── */}
        <Route
          path="/pacientes"
          element={
            <RutaProtegida usuario={usuario}>
              <ListarPacientes />
            </RutaProtegida>
          }
        />

        <Route
          path="/registrar-paciente"
          element={
            <RutaProtegida usuario={usuario}>
              <RegistrarPaciente />
            </RutaProtegida>
          }
        />

        {/*
          ResumenPaciente lee ?id= de la URL (window.location.search).
          La URL es: /resumen-paciente?id=<ObjectId>
        */}
        <Route
          path="/resumen-paciente"
          element={
            <RutaProtegida usuario={usuario}>
              <ResumenPaciente />
            </RutaProtegida>
          }
        />

        <Route
          path="/medicamentos"
          element={
            <RutaProtegida usuario={usuario}>
              <Medicamentos />
            </RutaProtegida>
          }
        />

        <Route
          path="/registrar-medicamento"
          element={
            <RutaProtegida usuario={usuario}>
              <RegistroMedicamento />
            </RutaProtegida>
          }
        />

        {/*
          ListaRecordatorios necesita pacienteId como prop.
          Lo pasamos desde el estado global; el usuario selecciona el paciente
          antes de llegar aquí (desde ListarPacientes → ResumenPaciente).
        */}
        <Route
          path="/recordatorios"
          element={
            <RutaProtegida usuario={usuario}>
              <ListaRecordatorios
                pacienteId={pacienteActivo}
                onNuevoRecordatorio={() => window.location.href = '/crear-recordatorio'}
              />
            </RutaProtegida>
          }
        />

        <Route
          path="/crear-recordatorio"
          element={
            <RutaProtegida usuario={usuario}>
              <Recordatorios
                onVolver={() => window.location.href = '/recordatorios'}
                onGuardadoExitoso={() => window.location.href = '/recordatorios'}
              />
            </RutaProtegida>
          }
        />

        <Route
          path="/historial"
          element={
            <RutaProtegida usuario={usuario}>
              <HistorialTomas />
            </RutaProtegida>
          }
        />

        <Route
          path="/tomas"
          element={
            <RutaProtegida usuario={usuario}>
              <Tomas />
            </RutaProtegida>
          }
        />

        <Route
          path="/panel-dia"
          element={
            <RutaProtegida usuario={usuario}>
              <PanelDia />
            </RutaProtegida>
          }
        />

        {/*
          ListaTomas necesita pacienteId y nombrePaciente como props.
          Se accede típicamente después de seleccionar un paciente.
        */}
        <Route
          path="/lista-tomas"
          element={
            <RutaProtegida usuario={usuario}>
              <ListaTomas
                pacienteId={pacienteActivo}
                nombrePaciente={nombrePacienteActivo}
              />
            </RutaProtegida>
          }
        />

        {/* Ruta de dashboard (alias de pacientes) */}
        <Route
          path="/dashboard"
          element={<Navigate to="/pacientes" replace />}
        />

        {/* 404 */}
        <Route path="*" element={<Navigate to="/" replace />} />

      </Routes>
    </BrowserRouter>
  );
}