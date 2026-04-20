/*
Patrón Fachada
Centraliza todas las llamadas al backend en un mismo lugar.
Las interfaces HTML ya no hacen llamadas directas al backend,
sino que usan el objeto "api" como intermediario.
*/

const API_URL = 'http://127.0.0.1:8000';

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
    if (!pacienteId) {
      return Promise.resolve({
        ok: false,
        body: { detail: 'pacienteId es obligatorio' }
      });
    }

    return fetch(API_URL + '/tomas/dia/' + pacienteId + (fecha ? '?fecha=' + fecha : ''))
    .then(function(r) {
      return r.json().then(function(b) {
        return { ok: r.ok, body: b };
      });
    });
  },

  obtenerHistorial: function(pacienteId) {
    if (!pacienteId) {
      return Promise.resolve({
        ok: false,
        body: { detail: 'pacienteId es obligatorio' }
      });
    }

    return fetch(API_URL + '/tomas/historial/' + pacienteId)
    .then(function(r) {
      return r.json().then(function(b) {
        return { ok: r.ok, body: b };
      });
    });
  },

  // PANEL DEL DÍA
  // Como el backend actual no tiene /panel-dia,
  // esta función reutiliza la ruta de tomas del día.
  obtenerPanelDia: function(pacienteId, fecha) {
    if (!pacienteId) {
      return Promise.resolve({
        ok: false,
        body: { detail: 'pacienteId es obligatorio para cargar el panel del día' }
      });
    }

    return fetch(API_URL + '/tomas/dia/' + pacienteId + (fecha ? '?fecha=' + fecha : ''))
    .then(function(r) {
      return r.json().then(function(b) {
        return { ok: r.ok, body: b };
      });
    });
  }
};