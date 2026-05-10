/*
  Patrón Fachada — centraliza todas las llamadas al backend.
  Adaptado para MongoDB: los IDs son strings (ObjectId), no enteros.
  Importar con: import api from './api';
*/
const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

// Lee el token guardado en localStorage después del login
function getToken() {
  return localStorage.getItem('medtrack_token') || '';
}

// Headers para endpoints protegidos (requieren autenticación)
function headersAuth() {
  return {
    'Content-Type': 'application/json',
    'authorization': 'Bearer ' + getToken(),
  };
}

// Headers solo para endpoints públicos (signin, signup)
const headersPublicos = {
  'Content-Type': 'application/json',
};

function procesarRespuesta(response) {
  return response.text().then(function (texto) {
    let body = {};
    try {
      body = texto ? JSON.parse(texto) : {};
    } catch (e) {
      body = { detail: texto };
    }
    return { ok: response.ok, status: response.status, body };
  });
}

function fetchJson(url, options) {
  return fetch(url, options).then(procesarRespuesta);
}

function fetchConFallback(urls, options) {
  let indice = 0;
  function intentar() {
    return fetch(urls[indice], options)
      .then(procesarRespuesta)
      .then(function (resultado) {
        if (!resultado.ok && resultado.status === 404 && indice < urls.length - 1) {
          indice += 1;
          return intentar();
        }
        return resultado;
      })
      .catch(function (error) {
        if (indice < urls.length - 1) {
          indice += 1;
          return intentar();
        }
        throw error;
      });
  }
  return intentar();
}

const api = {
  //  AUTH (públicos, no necesitan token) 
  iniciarSesion: (username, password) =>
    fetchJson(API_URL + '/signin', {
      method: 'POST',
      headers: headersPublicos,
      body: JSON.stringify({ username, password }),
    }),

  registrarUsuario: (datos) =>
    fetchJson(API_URL + '/signup', {
      method: 'POST',
      headers: headersPublicos,
      body: JSON.stringify(datos),
    }),

  //  PACIENTES 
  registrarPaciente: (datos) =>
    fetchJson(API_URL + '/pacientes', {
      method: 'POST',
      headers: headersAuth(),
      body: JSON.stringify(datos),
    }),

  obtenerPacientes: () =>
    fetchJson(API_URL + '/pacientes', {
      headers: headersAuth(),
    }),

  obtenerPaciente: (pacienteId) =>
    fetchJson(API_URL + '/pacientes/' + pacienteId, {
      headers: headersAuth(),
    }),

  //  MEDICAMENTOS 
  registrarMedicamento: (datos) =>
    fetchJson(API_URL + '/medicamentos/', {
      method: 'POST',
      headers: headersAuth(),
      body: JSON.stringify(datos),
    }),

  obtenerMedicamentos: (pacienteId) =>
    fetchJson(API_URL + '/medicamentos/paciente/' + pacienteId, {
      headers: headersAuth(),
    }),

  // ── RECORDATORIOS ───────────────────────────────────────────────────────
  crearRecordatorio: (datos) =>
    fetchJson(API_URL + '/recordatorios/', {
      method: 'POST',
      headers: headersAuth(),
      body: JSON.stringify(datos),
    }),

  obtenerRecordatorios: (pacienteId) =>
    fetchJson(API_URL + '/recordatorios/' + pacienteId, {
      headers: headersAuth(),
    }),

  obtenerPanelDia: (pacienteId, fecha) => {
    const opciones = { headers: headersAuth() };
    if (pacienteId) {
      const query = fecha ? '?fecha=' + fecha : '';
      return fetchConFallback([
        API_URL + '/recordatorios/panel-dia/' + pacienteId,
        API_URL + '/tomas/dia/' + pacienteId + query,
        API_URL + '/tomas/' + pacienteId + query,
      ], opciones);
    }
    return fetchJson(API_URL + '/recordatorios/panel-dia', opciones);
  },

  obtenerPanelDiaPaciente: (pacienteId) =>
    fetchConFallback([
      API_URL + '/recordatorios/panel-dia/' + pacienteId,
      API_URL + '/tomas/dia/' + pacienteId,
      API_URL + '/tomas/' + pacienteId,
    ], { headers: headersAuth() }),

  obtenerRecordatoriosRetrasados: (pacienteId) =>
    fetchJson(API_URL + '/recordatorios/retrasados/' + pacienteId, {
      headers: headersAuth(),
    }),

  marcarRecordatorioTomado: (recordatorioId) =>
    fetchJson(API_URL + '/recordatorios/' + recordatorioId + '/tomado', {
      method: 'PATCH',
      headers: headersAuth(),
    }),

  //  TOMAS 
  registrarToma: (datos) =>
    fetchJson(API_URL + '/tomas/', {
      method: 'POST',
      headers: headersAuth(),
      body: JSON.stringify(datos),
    }),

  obtenerTomas: (pacienteId, fecha) => {
    if (!pacienteId) {
      return Promise.resolve({
        ok: false,
        status: 400,
        body: { detail: 'pacienteId es obligatorio' },
      });
    }
    const query = fecha ? '?fecha=' + fecha : '';
    return fetchConFallback([
      API_URL + '/tomas/dia/' + pacienteId + query,
      API_URL + '/tomas/' + pacienteId + query,
    ], { headers: headersAuth() });
  },

  obtenerTomasDelDia(pacienteId, fecha) {
    return this.obtenerTomas(pacienteId, fecha);
  },

  //  HISTORIAL 
  obtenerHistorial: (pacienteId) => {
    if (!pacienteId) {
      return Promise.resolve({
        ok: false,
        status: 400,
        body: { detail: 'pacienteId es obligatorio' },
      });
    }
    return fetchConFallback([
      API_URL + '/tomas/historial/' + pacienteId,
      API_URL + '/historial/' + pacienteId,
    ], { headers: headersAuth() });
  },

  //  RESUMEN
  obtenerResumen: (pacienteId) =>
    fetchJson(API_URL + '/resumen/' + pacienteId, {
      headers: headersAuth(),
    }),
};

export default api;