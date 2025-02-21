<template>
  <div class="container">
    <h1>buscaTOR Scraper</h1>

    <!-- Campo de texto para ingresar temáticas -->
    <div class="input-group">
      <label>Temáticas (separadas por comas)</label>
      <input v-model="inputTematica" type="text" placeholder="Ej: Shops, Market" @keydown="handleKeydown" />
    </div>

    <!-- Lista de temáticas agregadas -->
    <div class="tematicas-container">
      <div v-for="(tematica, index) in tematicas" :key="index" class="tematica">
        {{ tematica }}
        <span class="close-btn" @click="removeTematica(index)">×</span>
      </div>
    </div>

    <!-- Radio Buttons para la selección de red -->
    <div class="input-group">
      <label>Selecciona la Red:</label>
      <div>
        <input type="radio" id="surface" value="surface" v-model="network" />
        <label for="surface">Surface Web</label>

        <input type="radio" id="deep" value="deep" v-model="network" />
        <label for="deep">Deep Web</label>
      </div>
    </div>

    <!-- Campo para subir archivo CSV -->
    <div class="input-group">
      <label>Cargar lista de dominios (CSV)</label>
      <input type="file" @change="handleFileUpload" accept=".csv" />
      <p v-if="fileError" class="error">{{ fileError }}</p>
    </div>

    <!-- Botón para iniciar el scraping -->
    <button @click="startScraping">Iniciar Scraping</button>

    <!-- Mensaje de estado -->
    <p v-if="statusMessage">{{ statusMessage }}</p>
  </div>
</template>

<script>
import { ref } from "vue";

export default {
  setup() {
    const inputTematica = ref("");
    const tematicas = ref([]);
    const network = ref("");
    const file = ref(null);
    const fileError = ref("");
    const statusMessage = ref("");

    // Manejar entrada de teclado en el campo de temáticas
    const handleKeydown = (event) => {
      if (event.key === "," && inputTematica.value.trim() !== "") {
        event.preventDefault();
        addTematica();
      }
    };

    // Añadir una temática
    const addTematica = () => {
      const nuevaTematica = inputTematica.value.replace(",", "").trim();
      if (nuevaTematica && !tematicas.value.includes(nuevaTematica)) {
        tematicas.value.push(nuevaTematica);
      }
      inputTematica.value = "";
    };

    // Eliminar una temática
    const removeTematica = (index) => {
      tematicas.value.splice(index, 1);
    };

    // Manejar la carga del archivo CSV
    const handleFileUpload = (event) => {
      fileError.value = "";
      const uploadedFile = event.target.files[0];

      if (uploadedFile) {
        if (!uploadedFile.name.endsWith(".csv")) {
          fileError.value = "Por favor, sube un archivo CSV válido.";
          return;
        }

        // Guardar el archivo
        file.value = uploadedFile;
      }
    };

    // Enviar datos al backend
    const startScraping = () => {
      if (!tematicas.value.length || !network.value) {
        statusMessage.value = "Por favor, completa todos los campos.";
        return;
      }

      console.log("Enviando datos:", {
        tematicas: tematicas.value,
        network: network.value,
        file: file.value ? file.value.name : null,
      });

      statusMessage.value = "Scraping en proceso...";
    };

    return { inputTematica, tematicas, handleKeydown, addTematica, removeTematica, network, handleFileUpload, startScraping, fileError, statusMessage };
  },
};
</script>

<style>
.container {
  max-width: 600px;
  margin: 50px auto;
  padding: 20px;
  border-radius: 8px;
  background: #004d40;
  text-align: center;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  color: white;
}

.input-group {
  margin-bottom: 15px;
}

input[type="text"],
input[type="file"] {
  width: 100%;
  padding-top: 10px;
  padding-bottom: 10px;
  padding-left: 10px;
  margin-top: 5px;
  border-radius: 4px;
  border: 1px solid #ccc;
}

button {
  padding: 10px 20px;
  background-color: #007bff;
  color: #fff;
  border: none;
  cursor: pointer;
  border-radius: 4px;
}

button:hover {
  background-color: #0056b3;
}

.error {
  color: red;
  font-size: 14px;
}

/* Estilos para las temáticas */
.tematicas-container {
  display: flex;
  flex-wrap: wrap;
  margin-top: 10px;
}

.tematica {
  background-color: #26a69a;
  color: white;
  padding: 5px 10px;
  margin: 5px;
  border-radius: 5px;
  display: flex;
  align-items: center;
}

.close-btn {
  margin-left: 8px;
  cursor: pointer;
  font-weight: bold;
  font-size: 16px;
}
</style>