/*
Patrón fachada
decidimos implementar el patrón de diseño Fachada, ya que la idea es centralizar todas las llamadas al backend en un mismo lugar
Así las interfaces HTML ya no hacen llamadas directas al backend, sino que usan el objeto "api" como intermediario.
Entonces ya no tenemos que duplicar el código del fetch, reducimos el acoplamiento entre en front y el backend 
sino que simplente llamamos las funciones.
*/
// Esta variable guarda la dirección del servidor backend.
// Si algún día cambia el puerto o la dirección, solo se cambia aqui y automáticamente funciona en todo el proyecto.
const API_URL = 'http://localhost:8000';


// En lugar de escribir el fetch completo en cada HTML, aquí lo definimos, que viene siendo la fachada del sistem
// una sola vez y lo reutilizamos desde cualquier página.
const api = {

  //PACIENTES 

  // Esta función recibe los datos del formulario y los envía al backend
  // para registrar un paciente nuevo en la base de datos.
  // datos es el objeto con nombre, apellidos, documento y demas datos del paciente

  // Método de la fachada para registrar un paciente
  registrarPaciente: function(datos) {
    return fetch(API_URL + '/pacientes', {
      method: 'POST',                                    // POST ya que estamos creando algo nuevo
      headers: { 'Content-Type': 'application/json' },  // le decimos al backend que mandamos JSON
      body: JSON.stringify(datos)                        // convertimos el objeto a texto JSON
    })
    .then(function(r) {
      // r.json() lee la respuesta del servidor
      // lo combinamos con r.ok para saber si fue exitoso con true o tuvo error con false
      return r.json().then(function(b) {
        return { ok: r.ok, body: b };
      });
    });
  },

  // Esta función le pide al backend la lista de todos los pacientes registrados
  // Método de la fachada para obtener todos los pacientes.
  obtenerPacientes: function() {
    return fetch(API_URL + '/pacientes')
    .then(function(r) {
      return r.json().then(function(b) {
        return { ok: r.ok, body: b };
      });
    });
  },

  // MEDICAMENTOS
  // Esta función envía los datos de un medicamento nuevo al backend.
  // datos incluye nombre, dosis, frecuencia, horario y el id del paciente.

   // Método de la fachada para registrar un medicamento
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

  // Esta función trae todos los medicamentos de un paciente específico
  obtenerMedicamentos: function(pacienteId) {
    return fetch(API_URL + '/medicamentos/' + pacienteId)
    .then(function(r) {
      return r.json().then(function(b) {
        return { ok: r.ok, body: b };
      });
    });
  },

  //RECORDATORIOS

  // Esta función crea un recordatorio nuevo en el backend
  // datos contiene el id del medicamento, la hora y la fecha de inicio
  // Método de la fachada para crear un recordatorio.
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
  //Método de la fachada para obtener recordatorios de un paciente
  // Esta función trae todos los recordatorios activos de un paciente
  obtenerRecordatorios: function(pacienteId) {
    return fetch(API_URL + '/recordatorios/' + pacienteId)
    .then(function(r) {
      return r.json().then(function(b) {
        return { ok: r.ok, body: b };
      });
    });
  }

};