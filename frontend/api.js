/*
  api.js — Patrón Fachada
  Centraliza todas las llamadas al backend en un solo lugar.
  Ninguna página HTML hace fetch() directamente: siempre llama a api.algo().

  ENDPOINTS REALES DEL BACKEND (FastAPI localhost:8000):
    POST   /pacientes                          → registrar paciente
    GET    /pacientes                          → lista de pacientes (retorna array directo)
    POST   /medicamentos/                      → registrar medicamento
    GET    /medicamentos/paciente/{id}         → medicamentos de un paciente  ← NUEVO en backend
    POST   /recordatorios/                     → crear recordatorio
    GET    /recordatorios/{paciente_id}        → recordatorios de un paciente
    GET    /recordatorios/panel-dia            → panel del día (TODOS los pacientes)
    GET    /recordatorios/panel-dia/{id}       → panel del día de un paciente
    GET    /recordatorios/retrasados/{id}      → recordatorios retrasados
    PATCH  /recordatorios/{id}/tomado         → marcar recordatorio como tomado
    POST   /tomas/                             → registrar toma
    GET    /tomas/{paciente_id}               → tomas del día de un paciente
    GET    /historial/{paciente_id}           → historial completo de tomas
    POST   /signin                             → iniciar sesión
    POST   /signup                             → registrar usuario
*/

const API_URL = 'http://localhost:8000';

const api = {

  // ─── PACIENTES ───────────────────────────────────────────

  registrarPaciente: function(datos) {
    return fetch(API_URL + '/pacientes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    }).then(function(r) {
      return r.json().then(function(b) { return { ok: r.ok, body: b }; });
    });
  },

  // Devuelve: array directo de pacientes (cada uno con campo "id")
  obtenerPacientes: function() {
    return fetch(API_URL + '/pacientes')
      .then(function(r) {
        return r.json().then(function(b) { return { ok: r.ok, body: b }; });
      });
  },

  // ─── MEDICAMENTOS ─────────────────────────────────────────

  registrarMedicamento: function(datos) {
    return fetch(API_URL + '/medicamentos/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    }).then(function(r) {
      return r.json().then(function(b) { return { ok: r.ok, body: b }; });
    });
  },

  // GET /medicamentos/paciente/{paciente_id}
  // IMPORTANTE: este endpoint debe existir en tu backend.
  // Si aún no lo tienes, agrega esta función a medication_route.py (ver nota al pie).
  obtenerMedicamentos: function(pacienteId) {
    return fetch(API_URL + '/medicamentos/paciente/' + pacienteId)
      .then(function(r) {
        return r.json().then(function(b) { return { ok: r.ok, body: b }; });
      });
  },

  // ─── RECORDATORIOS ────────────────────────────────────────

  crearRecordatorio: function(datos) {
    return fetch(API_URL + '/recordatorios/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    }).then(function(r) {
      return r.json().then(function(b) { return { ok: r.ok, body: b }; });
    });
  },

  obtenerRecordatorios: function(pacienteId) {
    return fetch(API_URL + '/recordatorios/' + pacienteId)
      .then(function(r) {
        return r.json().then(function(b) { return { ok: r.ok, body: b }; });
      });
  },

  // Panel del día de TODOS los pacientes → GET /recordatorios/panel-dia
  obtenerPanelDia: function() {
    return fetch(API_URL + '/recordatorios/panel-dia')
      .then(function(r) {
        return r.json().then(function(b) { return { ok: r.ok, body: b }; });
      });
  },

  // Panel del día de UN paciente → GET /recordatorios/panel-dia/{paciente_id}
  obtenerPanelDiaPaciente: function(pacienteId) {
    return fetch(API_URL + '/recordatorios/panel-dia/' + pacienteId)
      .then(function(r) {
        return r.json().then(function(b) { return { ok: r.ok, body: b }; });
      });
  },

  obtenerRecordatoriosRetrasados: function(pacienteId) {
    return fetch(API_URL + '/recordatorios/retrasados/' + pacienteId)
      .then(function(r) {
        return r.json().then(function(b) { return { ok: r.ok, body: b }; });
      });
  },

  marcarRecordatorioTomado: function(recordatorioId) {
    return fetch(API_URL + '/recordatorios/' + recordatorioId + '/tomado', {
      method: 'PATCH'
    }).then(function(r) {
      return r.json().then(function(b) { return { ok: r.ok, body: b }; });
    });
  },

  // ─── TOMAS ────────────────────────────────────────────────

  // POST /tomas/ — requiere: paciente_id, medicamento_id, recordatorio_id,
  //                           fecha_programada, fecha_hora_toma, estado, observaciones
  registrarToma: function(datos) {
    return fetch(API_URL + '/tomas/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    }).then(function(r) {
      return r.json().then(function(b) { return { ok: r.ok, body: b }; });
    });
  },

  // GET /tomas/{paciente_id}?fecha=YYYY-MM-DD
  obtenerTomasDelDia: function(pacienteId, fecha) {
    var url = API_URL + '/tomas/' + pacienteId;
    if (fecha) url += '?fecha=' + fecha;
    return fetch(url)
      .then(function(r) {
        return r.json().then(function(b) { return { ok: r.ok, body: b }; });
      });
  },

  // ─── HISTORIAL ────────────────────────────────────────────

  // GET /historial/{paciente_id}
  // Devuelve: { historial: [...], resumen: { total, a_tiempo, tarde, omitidas, porcentaje_cumplimiento } }
  obtenerHistorial: function(pacienteId) {
    return fetch(API_URL + '/historial/' + pacienteId)
      .then(function(r) {
        return r.json().then(function(b) { return { ok: r.ok, body: b }; });
      });
  },

  // ─── AUTH ─────────────────────────────────────────────────

  iniciarSesion: function(username, password) {
    return fetch(API_URL + '/signin', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username, password: password })
    }).then(function(r) {
      return r.json().then(function(b) { return { ok: r.ok, body: b }; });
    });
  },

  registrarUsuario: function(datos) {
    return fetch(API_URL + '/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    }).then(function(r) {
      return r.json().then(function(b) { return { ok: r.ok, body: b }; });
    });
  }

};
