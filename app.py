import streamlit as st
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.io import MemoryFile
import datetime

# Configuración de la página
st.set_page_config(page_title="Calibración Térmica", layout="wide")

# Estilos personalizados
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=PT+Serif:wght@400;700&display=swap');

        body {
            background: linear-gradient(to bottom right, #1e3c72, #2a5298);
            color: white;
            font-family: 'PT Serif', serif;
        }

        .main-header {
            background-color: #ffa500;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            color: white;
            font-size: 32px;
            font-weight: bold;
        }

        .logo-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            padding: 10px 30px;
        }

        .logo-container img {
            height: 120px;
        }

        .stButton > button {
            background-color: #ffa500;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            font-family: 'PT Serif', serif;
            padding: 10px 20px;
        }

        .stDownloadButton > button {
            background-color: #28a745;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            font-family: 'PT Serif', serif;
            padding: 10px 20px;
        }

        .stNumberInput input {
            background-color: #f0f0f0;
            color: #333;
            font-family: 'PT Serif', serif;
        }

        h2, h3, .stMarkdown {
            color: #f0f0f0;
            font-family: 'PT Serif', serif;
        }

        .stFileUploader {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 10px;
        }

        footer {
            text-align: center;
            margin-top: 50px;
            font-size: 14px;
            color: #ccc;
        }
    </style>
""", unsafe_allow_html=True)

# Encabezado con logos y título alineados horizontalmente
st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; background-color: #ffa500; padding: 10px 20px; border-radius: 10px;">
        <img src="https://raw.githubusercontent.com/JLHM1998/thermal_image_calibration/master/assets/856x973_ESCUDOCOLOR.png" alt="Logo Izquierdo" style="height: 80px;">
        <h1 style="color: white; text-align: center; margin: 0; font-size: 24px; font-family: 'PT Serif', serif;">
            🔥 Calibración de Imágenes Térmicas
        </h1>
        <img src="https://raw.githubusercontent.com/JLHM1998/thermal_image_calibration/master/assets/logo_TyC.png" alt="Logo Derecho" style="height: 80px;">
    </div>
""", unsafe_allow_html=True)

# --- Encabezado y descripción ---
st.markdown("""
### Bienvenido a la aplicación de calibración térmica
Esta aplicación permite cargar un ortomosaico térmico, aplicar una **ecuación de calibración** y visualizar los resultados.

La calibración indirecta de las imágenes térmicas obtenidas por la cámara H20T se realizó comparándolas con los datos medidos con un radiómetro en nueve coberturas. Para reescalar los valores de temperatura en las imágenes térmicas, se utilizó un radiómetro Apogee MI-210 (MI-210; Apogee Instruments, Inc., Logan, UT, USA). Este radiómetro se utilizó en nueve coberturas conocidas, incluyendo aluminio, hojas secas, hojas verdes, poliestireno expandido, tela amarilla, tela negra, tela roja, tela verde y suelo desnudo.
""")

# --- Menús desplegables jerárquicos ---
st.markdown("### 🗺️ Seleccionar información del vuelo")

# Selección de región
region = st.selectbox("🌎 Seleccionar Región", ["Lambayeque", "Lima"])

# Inicializar variables
provincia = distrito = zona = None

# Opciones según la región seleccionada
if region == "Lambayeque":
    provincia = st.selectbox("📍 Seleccionar Provincia", ["Ferreñafe", "Chiclayo"])

    if provincia == "Ferreñafe":
        zona = st.selectbox("🗺️ Seleccionar Zona", ["Capote"])
    elif provincia == "Chiclayo":
        distrito = st.selectbox("🏙️ Seleccionar Distrito", ["Chongoyape", "Picsi"])

        if distrito == "Chongoyape":
            zona = st.selectbox("🗺️ Seleccionar Zona", ["Carniche", "Paredones"])
        elif distrito == "Picsi":
            zona = "Picsi"  # Selección directa
elif region == "Lima":
    zona = st.selectbox("📍 Seleccionar Zona", ["La Molina"])

# Mostrar la selección final
if zona:
    st.write(f"Zona seleccionada: {zona}")

# --- Selección de hora ---
st.markdown("### 🕒 Seleccionar hora del vuelo")
horas_disponibles = [datetime.time(hour, 0) for hour in range(9, 16)]
hora = st.selectbox("🕒 Hora del Vuelo (9:00 AM a 3:00 PM)", horas_disponibles)

st.write(f"Hora seleccionada: {hora}")

# --- Diccionario de ecuaciones ---
ecuaciones = {
    # Capote (Ferreñafe)
    ("Capote", datetime.time(9, 0)): (0.6341, 11.887),
    ("Capote", datetime.time(10, 0)): (0.8746, 12.76),
    ("Capote", datetime.time(11, 0)): (0.7291, 10.592),
    ("Capote", datetime.time(12, 0)): (0.7134, 11.998),
    ("Capote", datetime.time(13, 0)): (0.7134, 11.998),
    ("Capote", datetime.time(14, 0)): (0.8000, 12.500),
    ("Capote", datetime.time(15, 0)): (0.8500, 13.000),
    # Paredones (Chongoyape)
    ("Paredones", datetime.time(9, 0)): (0.85, 10.5),
    ("Paredones", datetime.time(10, 0)): (0.88, 11.2),
    ("Paredones", datetime.time(11, 0)): (0.90, 9.8),
    ("Paredones", datetime.time(12, 0)): (0.87, 10.0),
    ("Paredones", datetime.time(13, 0)): (0.89, 10.3),
    ("Paredones", datetime.time(14, 0)): (0.92, 11.0),
    ("Paredones", datetime.time(15, 0)): (0.95, 11.5),
    # Carniche (Chongoyape)
    ("Carniche", datetime.time(9, 0)): (0.92, 12.1),
    ("Carniche", datetime.time(10, 0)): (0.95, 11.5),
    ("Carniche", datetime.time(11, 0)): (0.93, 12.0),
    ("Carniche", datetime.time(12, 0)): (0.91, 11.8),
    ("Carniche", datetime.time(13, 0)): (0.94, 11.9),
    ("Carniche", datetime.time(14, 0)): (0.96, 12.3),
    ("Carniche", datetime.time(15, 0)): (0.98, 12.7),
    # Picsi
    ("Picsi", datetime.time(9, 0)): (0.6638, 12.615),
    ("Picsi", datetime.time(10, 0)): (0.6700, 12.700),
    ("Picsi", datetime.time(11, 0)): (0.6800, 12.800),
    ("Picsi", datetime.time(12, 0)): (0.6900, 12.900),
    ("Picsi", datetime.time(13, 0)): (0.7000, 13.000),
    ("Picsi", datetime.time(14, 0)): (0.7100, 13.100),
    ("Picsi", datetime.time(15, 0)): (0.7200, 13.200),
    # La Molina
    ("La Molina", datetime.time(9, 0)): (0.7134, 11.998),
    ("La Molina", datetime.time(10, 0)): (0.7200, 12.100),
    ("La Molina", datetime.time(11, 0)): (0.7300, 12.200),
    ("La Molina", datetime.time(12, 0)): (0.7400, 12.300),
    ("La Molina", datetime.time(13, 0)): (0.7500, 12.400),
    ("La Molina", datetime.time(14, 0)): (0.7600, 12.500),
    ("La Molina", datetime.time(15, 0)): (0.7700, 12.600),
}

# --- Obtener coeficientes ---
A, B = ecuaciones.get((zona, hora), (1.0, 0.0))


# --- Subida de imagen ---
st.markdown("### 📂 Subir tu imagen térmica (GeoTIFF)")
uploaded_file = st.file_uploader("Selecciona tu archivo:", type=["tif", "tiff"])

if uploaded_file is not None:
    with rasterio.open(uploaded_file) as src:
        profile = src.profile
        image = src.read(1).astype(np.float32)

    # Vista previa original
    st.markdown("### 🗾 Vista Previa - Imagen Original")
    image_clipped = np.clip(image, 0, 70)
    vmin, vmax = np.percentile(image_clipped, [2, 98])
    fig, ax = plt.subplots(figsize=(6, 4))
    im = ax.imshow(image_clipped, cmap='inferno', vmin=vmin, vmax=vmax)
    ax.axis('off')
    cbar = fig.colorbar(im, ax=ax, label='Temperatura (°C)')
    st.pyplot(fig)

    # Aplicar calibración
    calibrated = A * image + B
    calibrated = np.clip(calibrated, 0, 70)

    # Vista previa calibrada
    st.markdown("### 🗾 Vista Previa - Imagen Calibrada")
    vmin2, vmax2 = np.percentile(calibrated, [2, 98])
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    im2 = ax2.imshow(calibrated, cmap='inferno', vmin=vmin2, vmax=vmax2)
    ax2.axis('off')
    cbar2 = fig2.colorbar(im2, ax=ax2, label='Temperatura Calibrada (°C)')
    st.pyplot(fig2)

    # Guardar como GeoTIFF
    profile.update(dtype=rasterio.float32)
    with MemoryFile() as memfile:
        with memfile.open(**profile) as dst:
            dst.write(calibrated.astype(rasterio.float32), 1)
        mem_bytes = memfile.read()

    # Botón de descarga
    st.markdown("### 💾 Descargar Imagen Calibrada")
    st.download_button("📥 Descargar TIFF Calibrado", data=mem_bytes,
                       file_name=f"{zona}_{hora}_calibrada.tif", mime="image/tiff")
else:
    st.info("Por favor, sube una imagen térmica para comenzar.")

# Pie de página
st.markdown("""
    <footer>
        © 2025 Universidad Nacional Agraria La Molina - Todos los derechos reservados.
    </footer>
""", unsafe_allow_html=True)
