/*
Patrón Fachada
Centraliza todas las llamadas al backend en un mismo lugar.
Las páginas HTML no hacen fetch() directo; usan el objeto api.
*/

const API_URL = 'http://127.0.0.1:8000';

function procesarRespuesta(response) {
  return response.text().then(function(texto) {
    let body = {};
    try {
      body = texto ? JSON.parse(texto) : {};
    } catch (e) {
      body = { detail: texto };
    }

    return {
      ok: response.ok,
      status: response.status,
      body: body
    };
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
      .then(function(resultado) {
        if (!resultado.ok && resultado.status === 404 && indice < urls.length - 1) {
          indice += 1;
          return intentar();
        }
        return resultado;
      })
      .catch(function(error) {
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
  // PACIENTES
  registrarPaciente: function(datos) {
    return fetchJson(API_URL + '/pacientes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    });
  },

  obtenerPacientes: function() {
    return fetchJson(API_URL + '/pacientes');
  },

  // MEDICAMENTOS
  registrarMedicamento: function(datos) {
    return fetchJson(API_URL + '/medicamentos/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    });
  },

  obtenerMedicamentos: function(pacienteId) {
    return fetchJson(API_URL + '/medicamentos/paciente/' + pacienteId);
  },

  // RECORDATORIOS
  crearRecordatorio: function(datos) {
    return fetchJson(API_URL + '/recordatorios/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    });
  },

  obtenerRecordatorios: function(pacienteId) {
    return fetchJson(API_URL + '/recordatorios/' + pacienteId);
  },

  obtenerPanelDia: function(pacienteId, fecha) {
    if (pacienteId) {
      const query = fecha ? ('?fecha=' + fecha) : '';
      return fetchConFallback([
        API_URL + '/recordatorios/panel-dia/' + pacienteId,
        API_URL + '/tomas/dia/' + pacienteId + query,
        API_URL + '/tomas/' + pacienteId + query
      ]);
    }

    return fetchJson(API_URL + '/recordatorios/panel-dia');
  },

  obtenerPanelDiaPaciente: function(pacienteId) {
    return fetchConFallback([
      API_URL + '/recordatorios/panel-dia/' + pacienteId,
      API_URL + '/tomas/dia/' + pacienteId,
      API_URL + '/tomas/' + pacienteId
    ]);
  },

  obtenerRecordatoriosRetrasados: function(pacienteId) {
    return fetchJson(API_URL + '/recordatorios/retrasados/' + pacienteId);
  },

  marcarRecordatorioTomado: function(recordatorioId) {
    return fetchJson(API_URL + '/recordatorios/' + recordatorioId + '/tomado', {
      method: 'PATCH'
    });
  },

  // TOMAS
  registrarToma: function(datos) {
    return fetchJson(API_URL + '/tomas/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    });
  },

  obtenerTomas: function(pacienteId, fecha) {
    if (!pacienteId) {
      return Promise.resolve({
        ok: false,
        status: 400,
        body: { detail: 'pacienteId es obligatorio' }
      });
    }

    const query = fecha ? ('?fecha=' + fecha) : '';

    return fetchConFallback([
      API_URL + '/tomas/dia/' + pacienteId + query,
      API_URL + '/tomas/' + pacienteId + query
    ]);
  },

  obtenerTomasDelDia: function(pacienteId, fecha) {
    return this.obtenerTomas(pacienteId, fecha);
  },

  // HISTORIAL
  obtenerHistorial: function(pacienteId) {
    if (!pacienteId) {
      return Promise.resolve({
        ok: false,
        status: 400,
        body: { detail: 'pacienteId es obligatorio' }
      });
    }

    return fetchConFallback([
      API_URL + '/tomas/historial/' + pacienteId,
      API_URL + '/historial/' + pacienteId
    ]);
  },

  // AUTH
  iniciarSesion: function(username, password) {
    return fetchJson(API_URL + '/signin', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username,
        password: password
      })
    });
  },

  registrarUsuario: function(datos) {
    return fetchJson(API_URL + '/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    });
  },

  obtenerPaciente: function(pacienteId) {
    return fetchJson(API_URL + '/pacientes/' + pacienteId);
  },

  // HU-43: obtener resumen detallado del paciente (Task #522)
  obtenerResumen: function(pacienteId) {
    return fetchJson(API_URL + '/resumen/' + pacienteId);
  }
};
