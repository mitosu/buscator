<template>
    <div class="download-section">
      <h2>Descargar Reporte</h2>
      <button @click="downloadReport('pdf')" class="btn btn-primary">Descargar PDF</button>
      <button @click="downloadReport('html')" class="btn btn-secondary">Descargar HTML</button>
    </div>
  </template>
  
  <script>
  export default {
    methods: {
      async downloadReport(type) {
        try {
          const response = await fetch(`http://127.0.0.1:8000/download-report/?report_type=${type}`);
          
          if (!response.ok) {
            alert("Error: No se pudo descargar el reporte.");
            return;
          }
  
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `scraping_report.${type}`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        } catch (error) {
          console.error("Error al descargar el reporte:", error);
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .download-section {
    margin-top: 20px;
    text-align: center;
  }
  button {
    margin: 10px;
    padding: 10px 20px;
    font-size: 16px;
  }
  .btn-primary {
    background-color: #007bff;
    color: white;
    border: none;
    cursor: pointer;
  }
  .btn-secondary {
    background-color: #28a745;
    color: white;
    border: none;
    cursor: pointer;
  }
  </style>
  