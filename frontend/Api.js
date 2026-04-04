/*
  api.js — Capa centralizada de comunicación con el backend MedTrack
  Todos los fetch del proyecto pasan por este objeto.
  Si cambia la URL base, solo se edita aquí.
*/

const api = (function () {

  const BASE_URL = 'http://localhost:8000';

  /*
    _request — método interno que envuelve fetch
    Devuelve siempre: { ok: boolean, body: objeto }
  */
  function _request(url, opciones) {
    return fetch(BASE_URL + url, opciones)
      .then(function (r) {
        return r.json().then(function (b) {
          return { ok: r.ok, body: b };
        });
      });
  }

  /* ── Pacientes ── */

  function registrarPaciente(datos) {
    return _request('/pacientes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    });
  }

  function obtenerPacientes() {
    return _request('/pacientes', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
  }

  /* ── Medicamentos ── */

  function registrarMedicamento(datos) {
    return _request('/medicamentos/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    });
  }

  /* ── Recordatorios ── */

  function obtenerRecordatorios(pacienteId) {
    const token = localStorage.getItem('medtrack_token') || 'test';
    return _request('/recordatorios/' + pacienteId, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    });
  }

  /* Exponemos solo los métodos públicos */
  return {
    registrarPaciente,
    obtenerPacientes,
    registrarMedicamento,
    obtenerRecordatorios
  };

})();