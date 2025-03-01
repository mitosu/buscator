🕵️‍♂️ BuscaTOR - Web Scraper para Surface Web y Deep Web
BuscaTOR es una aplicación que permite realizar scraping de sitios web en la Surface Web y la Deep Web (dominios .onion). La aplicación obtiene información de los sitios, incluyendo título, descripción, tecnologías utilizadas y capturas de pantalla de la página principal.

🚀 Tecnologías utilizadas:

Frontend: Vue.js + Express.js
Backend: Python + FastAPI
Scraping: BeautifulSoup, Requests, Tor Browser
Captura de pantalla: Xvfb + Scrot + Tor Browser
Reportes: Generación en PDF y HTML
📌 Características
✔ Soporte para Surface Web y Deep Web (mediante Tor)
✔ Scraping automatizado según temáticas definidas por el usuario
✔ Extracción de información clave (<title>, <meta description>, tecnologías detectadas)
✔ Captura de pantalla de la página principal del sitio
✔ Generación de reportes en formato PDF y HTML
✔ Interfaz de usuario amigable con Vue.js
✔ Ejecución segura en entornos Linux (Kali, CSI Linux, Ubuntu)

📥 Instalación
1️⃣ Clonar el repositorio
bash
Copy
Edit
git clone https://github.com/tuusuario/buscaTOR.git
cd buscaTOR
2️⃣ Configurar el Backend (FastAPI)
📌 Crear y activar entorno virtual:
bash
Copy
Edit
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
📌 Instalar dependencias:
bash
Copy
Edit
pip install -r requirements.txt
📌 Ejecutar el Backend:
bash
Copy
Edit
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
3️⃣ Configurar el Frontend (Vue.js + Express.js)
📌 Instalar dependencias:
bash
Copy
Edit
cd frontend
npm install
📌 Ejecutar el servidor de desarrollo:
bash
Copy
Edit
npm run dev
🕵️ Modo de Uso
1️⃣ Definir los criterios de búsqueda:

Escribir temáticas separadas por comas (Ej: Shops, Market)
Seleccionar la red de búsqueda (Surface Web o Deep Web)
Cargar un archivo .csv con dominios o dejarlo vacío para que el sistema los busque automáticamente
2️⃣ Ejecutar el Scraper:

Se realizará scraping en los sitios web que coincidan con la temática dada
Si es Deep Web, se ejecutará con Tor Browser en segundo plano
Se capturará una screenshot de la página principal
3️⃣ Generación de Reportes:

Al finalizar, se podrá descargar un reporte en PDF o HTML
🔧 Requisitos Previos
📌 Para Surface Web: No se requieren configuraciones especiales.
📌 Para Deep Web: Se debe tener instalado Tor Browser y configurar la conexión automática.
📌 Dependencias adicionales para capturas:

bash
Copy
Edit
sudo apt install -y xvfb scrot torbrowser-launcher
⚠️ Notas Importantes
Asegúrate de tener Xvfb corriendo antes de ejecutar la aplicación para capturas de pantalla.
La búsqueda en Deep Web requiere Tor Browser correctamente instalado y ejecutándose en modo automático.
La aplicación fue desarrollada y probada en Kali Linux y CSI Linux, por lo que puede requerir ajustes en otros sistemas.
🤝 Créditos y Agradecimientos
💡 Tutor: Fran Rodríguez
🎯 Equipo de Desarrollo (Grupo C): Gemma, Eva, Oriol y Miguel Torres

📜 Licencia
Este proyecto está bajo la licencia MIT. Puedes utilizarlo, modificarlo y distribuirlo libremente, siempre y cuando se reconozca la autoría original.

⭐ Contribuir
Si deseas contribuir con mejoras, abre un issue o envía un pull request. ¡Toda ayuda es bienvenida! 🚀
