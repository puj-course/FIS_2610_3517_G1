/*
  Patrón Fachada — centraliza todas las llamadas al backend.
  Adaptado para MongoDB: los IDs son strings (ObjectId), no enteros.
  Importar con: import api from './api';
*/

const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

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
  // ── AUTH ────────────────────────────────────────────────────────────────
  iniciarSesion: (username, password) =>
    fetchJson(API_URL + '/signin', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    }),

  registrarUsuario: (datos) =>
    fetchJson(API_URL + '/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos),
    }),

  // ── PACIENTES ───────────────────────────────────────────────────────────
  // MongoDB devuelve _id (string ObjectId); el backend lo puede exponer como "id"
  registrarPaciente: (datos) =>
    fetchJson(API_URL + '/pacientes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos),
    }),

  obtenerPacientes: () => fetchJson(API_URL + '/pacientes'),

  // pacienteId es un string ObjectId de MongoDB
  obtenerPaciente: (pacienteId) =>
    fetchJson(API_URL + '/pacientes/' + pacienteId),

  // ── MEDICAMENTOS ────────────────────────────────────────────────────────
  registrarMedicamento: (datos) =>
    fetchJson(API_URL + '/medicamentos/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos),
    }),

  // pacienteId es string ObjectId
  obtenerMedicamentos: (pacienteId) =>
    fetchJson(API_URL + '/medicamentos/paciente/' + pacienteId),

  // ── RECORDATORIOS ───────────────────────────────────────────────────────
  crearRecordatorio: (datos) =>
    fetchJson(API_URL + '/recordatorios/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos),
    }),

  obtenerRecordatorios: (pacienteId) =>
    fetchJson(API_URL + '/recordatorios/' + pacienteId),

  obtenerPanelDia: (pacienteId, fecha) => {
    if (pacienteId) {
      const query = fecha ? '?fecha=' + fecha : '';
      return fetchConFallback([
        API_URL + '/recordatorios/panel-dia/' + pacienteId,
        API_URL + '/tomas/dia/' + pacienteId + query,
        API_URL + '/tomas/' + pacienteId + query,
      ]);
    }
    return fetchJson(API_URL + '/recordatorios/panel-dia');
  },

  obtenerPanelDiaPaciente: (pacienteId) =>
    fetchConFallback([
      API_URL + '/recordatorios/panel-dia/' + pacienteId,
      API_URL + '/tomas/dia/' + pacienteId,
      API_URL + '/tomas/' + pacienteId,
    ]),

  obtenerRecordatoriosRetrasados: (pacienteId) =>
    fetchJson(API_URL + '/recordatorios/retrasados/' + pacienteId),

  marcarRecordatorioTomado: (recordatorioId) =>
    fetchJson(API_URL + '/recordatorios/' + recordatorioId + '/tomado', {
      method: 'PATCH',
    }),

  // ── TOMAS ───────────────────────────────────────────────────────────────
  registrarToma: (datos) =>
    fetchJson(API_URL + '/tomas/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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
    ]);
  },

  obtenerTomasDelDia(pacienteId, fecha) {
    return this.obtenerTomas(pacienteId, fecha);
  },

  // ── HISTORIAL ───────────────────────────────────────────────────────────
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
    ]);
  },

  // ── RESUMEN ─────────────────────────────────────────────────────────────
  obtenerResumen: (pacienteId) =>
    fetchJson(API_URL + '/resumen/' + pacienteId),
};

export default api;