<template>
  <div class="container">
    <h1>buscaTOR Scraper</h1>
    <ReportDownload v-if="scrapingCompleted" />
    
    <!-- Campo de texto para ingresar temáticas -->
    <div class="input-group">
      <label>Temáticas (máximo 3, separadas por comas)</label>
      <input
        v-model="inputTematica"
        type="text"
        placeholder="Ej: Shops, Market"
        @keydown="handleKeydown"
        :disabled="tematicas.length >= 3"
      />
      <p v-if="tematicas.length >= 3" class="error">Máximo de 3 temáticas alcanzado.</p>
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

    <!-- Botón para iniciar o reiniciar el scraping -->
    <button :class="scrapingCompleted ? 'reset-button' : ''" @click="scrapingCompleted ? resetApp() : startScraping()">
      {{ scrapingCompleted ? 'Nuevo Scraping' : 'Iniciar Scraping' }}
    </button>

    <!-- Mensaje de estado -->
    <p v-if="statusMessage" class="message">{{ statusMessage }}</p>
  </div>
</template>

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

.reset-button {
  background-color: #28a745 !important;
}

.reset-button:hover {
  background-color: #218838 !important;
}

.error {
  color: rgb(253, 67, 67);
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

.message {
  margin-top: 20px;
  font-weight: bold;
  color: green;
}
</style>

<script>
import { ref } from "vue";
import axios from "axios";
import ReportDownload from "./components/ReportDownload.vue";

export default {
  components: {
    ReportDownload
  },
  
  setup() {
    const inputTematica = ref("");
    const tematicas = ref([]);
    const network = ref("");
    const file = ref(null);
    const fileError = ref("");
    const statusMessage = ref("");
    const scrapingCompleted = ref(false);

    const handleKeydown = (event) => {
      if (event.key === "," && inputTematica.value.trim() !== "") {
        event.preventDefault();
        addTematica();
      }
    };

    const addTematica = () => {
      const nuevaTematica = inputTematica.value.replace(",", "").trim();
      if (nuevaTematica && !tematicas.value.includes(nuevaTematica) && tematicas.value.length < 3) {
        tematicas.value.push(nuevaTematica);
      }
      inputTematica.value = "";
    };

    const startScraping = async () => {
      if (!tematicas.value.length || !network.value) {
        statusMessage.value = "Por favor, completa todos los campos.";
        return;
      }
      try {
        statusMessage.value = "Realizando scraping...";
        scrapingCompleted.value = false;

        await axios.post("http://127.0.0.1:8000/start-scraping/", {
          tematicas: tematicas.value,
          network: network.value
        });

        statusMessage.value = "Scraping finalizado";
        scrapingCompleted.value = true;
      } catch {
        statusMessage.value = "Error al iniciar el scraping.";
      }
    };

    const resetApp = () => {
      tematicas.value = [];
      network.value = "";
      file.value = null;
      statusMessage.value = "";
      scrapingCompleted.value = false;
    };

    return { inputTematica, tematicas, handleKeydown, addTematica, network, fileError, statusMessage, scrapingCompleted, startScraping, resetApp };
  },
};
</script>