from fastapi import FastAPI, UploadFile, File
import json
import os

app = FastAPI()

@app.post("/start-scraping/")
async def start_scraping(data: dict):
    """
    Recibe datos de la UI y ejecuta el scraping.
    """
    tematicas = data.get("tematicas", [])
    network = data.get("network", "")
    file_path = data.get("file", None)

    if not tematicas or not network:
        return {"error": "Faltan datos obligatorios"}

    # Simulación del proceso de scraping (Aquí luego se conectará con scraping real)
    response_data = {
        "message": "Scraping iniciado correctamente",
        "tematicas": tematicas,
        "network": network,
        "file_path": file_path
    }
    return response_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)