import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './Layout';

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
import MetricasCalidad  from './pages/MetricasCalidad';

function RutaProtegida({ usuario, onCerrarSesion, children }) {
  if (!usuario) return <Navigate to="/login" replace />;
  return <Layout usuario={usuario} onCerrarSesion={onCerrarSesion}>{children}</Layout>;
}

export default function App() {
  const [usuario, setUsuario] = useState(() => {
    try {
      const raw = localStorage.getItem('medtrack_usuario');
      return raw ? JSON.parse(raw) : null;
    } catch { return null; }
  });

  function handleLoginExitoso(datos) {
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

  const [pacienteActivo] = useState(null);
  const [nombrePacienteActivo] = useState('Paciente');

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={usuario ? <Navigate to="/pacientes" replace /> : <Login onLoginExitoso={handleLoginExitoso} onIrARegistro={() => window.location.href = '/registro'} />} />
        <Route path="/registro" element={usuario ? <Navigate to="/pacientes" replace /> : <Registro onIrALogin={() => window.location.href = '/login'} />} />
        <Route path="/" element={<Navigate to={usuario ? '/pacientes' : '/login'} replace />} />
        <Route path="/pacientes" element={<RutaProtegida usuario={usuario} onCerrarSesion={handleCerrarSesion}><ListarPacientes /></RutaProtegida>} />
        <Route path="/registrar-paciente" element={<RutaProtegida usuario={usuario} onCerrarSesion={handleCerrarSesion}><RegistrarPaciente /></RutaProtegida>} />
        <Route path="/resumen-paciente" element={<RutaProtegida usuario={usuario} onCerrarSesion={handleCerrarSesion}><ResumenPaciente /></RutaProtegida>} />
        <Route path="/medicamentos" element={<RutaProtegida usuario={usuario} onCerrarSesion={handleCerrarSesion}><Medicamentos /></RutaProtegida>} />
        <Route path="/registrar-medicamento" element={<RutaProtegida usuario={usuario} onCerrarSesion={handleCerrarSesion}><RegistroMedicamento /></RutaProtegida>} />
        <Route path="/recordatorios" element={<RutaProtegida usuario={usuario} onCerrarSesion={handleCerrarSesion}><ListaRecordatorios pacienteId={pacienteActivo} onNuevoRecordatorio={() => window.location.href = '/crear-recordatorio'} /></RutaProtegida>} />
        <Route path="/crear-recordatorio" element={<RutaProtegida usuario={usuario} onCerrarSesion={handleCerrarSesion}><Recordatorios onVolver={() => window.location.href = '/recordatorios'} onGuardadoExitoso={() => window.location.href = '/recordatorios'} /></RutaProtegida>} />
        <Route path="/historial" element={<RutaProtegida usuario={usuario} onCerrarSesion={handleCerrarSesion}><HistorialTomas /></RutaProtegida>} />
        <Route path="/tomas" element={<RutaProtegida usuario={usuario} onCerrarSesion={handleCerrarSesion}><Tomas /></RutaProtegida>} />
        <Route path="/panel-dia" element={<RutaProtegida usuario={usuario} onCerrarSesion={handleCerrarSesion}><PanelDia /></RutaProtegida>} />
        <Route path="/lista-tomas" element={<RutaProtegida usuario={usuario} onCerrarSesion={handleCerrarSesion}><ListaTomas pacienteId={pacienteActivo} nombrePaciente={nombrePacienteActivo} /></RutaProtegida>} />
        <Route path="/metricas-calidad" element={<RutaProtegida usuario={usuario} onCerrarSesion={handleCerrarSesion}><MetricasCalidad /></RutaProtegida>} />
        <Route path="/dashboard" element={<Navigate to="/pacientes" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
