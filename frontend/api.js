
/*
Patrón Fachada
Centraliza todas las llamadas al backend en un mismo lugar.
Las interfaces HTML ya no hacen llamadas directas al backend,
sino que usan el objeto "api" como intermediario.
*/

const API_URL = 'http://localhost:8000';

const api = {
  // PACIENTES
  registrarPaciente: function(datos) {
    return fetch(API_URL + '/pacientes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    })
    .then(function(r) {
      return r.json().then(function(b) {
        return { ok: r.ok, body: b };
      });
    });
  },

  obtenerPacientes: function() {
    return fetch(API_URL + '/pacientes')
    .then(function(r) {
      return r.json().then(function(b) {
        return { ok: r.ok, body: b };
      });
    });
  },

  // MEDICAMENTOS
  registrarMedicamento: function(datos) {
    return fetch(API_URL + '/medicamentos/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    })
    .then(function(r) {
      return r.json().then(function(b) {
        return { ok: r.ok, body: b };
      });
    });
  },

  obtenerMedicamentos: function(pacienteId) {
    return fetch(API_URL + '/medicamentos/' + pacienteId)
    .then(function(r) {
      return r.json().then(function(b) {
        return { ok: r.ok, body: b };
      });
    });
  },

  // RECORDATORIOS
  crearRecordatorio: function(datos) {
    return fetch(API_URL + '/recordatorios/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    })
    .then(function(r) {
      return r.json().then(function(b) {
        return { ok: r.ok, body: b };
      });
    });
  },

  obtenerRecordatorios: function(pacienteId) {
    return fetch(API_URL + '/recordatorios/' + pacienteId)
    .then(function(r) {
      return r.json().then(function(b) {
        return { ok: r.ok, body: b };
      });
    });
  },

  // TOMAS
  registrarToma: function(datos) {
    return fetch(API_URL + '/tomas/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    })
    .then(function(r) {
      return r.json().then(function(b) {
        return { ok: r.ok, body: b };
      });
    });
  },

  obtenerTomas: function(pacienteId, fecha) {
    return fetch(API_URL + '/tomas/' + pacienteId + (fecha ? '?fecha=' + fecha : ''))
    .then(function(r) {
      return r.json().then(function(b) {
        return { ok: r.ok, body: b };
      });
    });
  },

  // PANEL DEL DÍA
  obtenerPanelDia: function() {
    return fetch(API_URL + '/panel-dia')
    .then(function(r) {
      return r.json().then(function(b) {
        return { ok: r.ok, body: b };
      });
    });
  }
};