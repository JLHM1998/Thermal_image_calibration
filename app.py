import streamlit as st
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.io import MemoryFile
import datetime

st.set_page_config(page_title="Thermal Calibration", layout="centered")

# --- Encabezado y descripción ---
st.markdown("""
This app allows you to upload a thermal orthomosaic, apply a **calibration equation**, and visualize the results.

The indirect calibration of the thermal images obtained by the H20T camera was performed by comparing them with the data measured with a radiometer in nine coverages. To rescale the temperature values in the thermal images, an Apogee MI-210 radiometer (MI-210; Apogee Instruments, Inc., Logan, UT, USA) was used. This radiometer was used on nine known coverslips, including aluminum, dry leaves, green leaves, expanded polystyrene, yellow cloth, black cloth, red cloth, green cloth, and bare soil.
""")

# --- Menús desplegables jerárquicos ---
st.subheader("🗺️ Select flight info")

# Selección de región
region = st.selectbox("🌎 Select Region", ["Lambayeque", "Lima"])

# Inicializar variables
provincia = distrito = zona = None

# Opciones según la región seleccionada
if region == "Lambayeque":
    provincia = st.selectbox("📍 Select Province", ["Ferreñafe", "Chiclayo"])

    if provincia == "Ferreñafe":
        zona = st.selectbox("🗺️ Select Zone", ["Capote"])
    elif provincia == "Chiclayo":
        distrito = st.selectbox("🏙️ Select District", ["Chongoyape", "Picsi"])

        if distrito == "Chongoyape":
            zona = st.selectbox("🗺️ Select Zone", ["Carniche", "Paredones"])
        elif distrito == "Picsi":
            zona = "Picsi"  # Selección directa
elif region == "Lima":
    zona = st.selectbox("📍 Select Zone", ["La Molina"])

# Mostrar la selección final
if zona:
    st.write(f"Selected Zone: {zona}")

# --- Selección de hora ---
horas_disponibles = [datetime.time(hour, 0) for hour in range(9, 16)]
hora = st.selectbox("🕒 Flight Time (9:00 AM to 3:00 PM)", horas_disponibles)

st.write(f"Selected flight time: {hora}")

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
st.write(f"Calibration coefficients: A = {A}, B = {B}")

# --- Subida de imagen ---
st.subheader("📂 Upload your thermal image (GeoTIFF)")
uploaded_file = st.file_uploader("Select your file:", type=["tif", "tiff"])

if uploaded_file is not None:
    with rasterio.open(uploaded_file) as src:
        profile = src.profile
        image = src.read(1).astype(np.float32)

    # Vista previa original
    st.subheader("🗾 Preview - Original Image")
    image_clipped = np.clip(image, 0, 70)
    vmin, vmax = np.percentile(image_clipped, [2, 98])
    fig, ax = plt.subplots(figsize=(6, 4))
    im = ax.imshow(image_clipped, cmap='inferno', vmin=vmin, vmax=vmax)
    ax.axis('off')
    cbar = fig.colorbar(im, ax=ax, label='Temperature (°C)')
    st.pyplot(fig)

    # Aplicar calibración
    calibrated = A * image + B
    calibrated = np.clip(calibrated, 0, 70)

    # Vista previa calibrada
    st.subheader("🗾 Preview - Calibrated Image")
    vmin2, vmax2 = np.percentile(calibrated, [2, 98])
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    im2 = ax2.imshow(calibrated, cmap='inferno', vmin=vmin2, vmax=vmax2)
    ax2.axis('off')
    cbar2 = fig2.colorbar(im2, ax=ax2, label='Calibrated Temperature (°C)')
    st.pyplot(fig2)

    # Guardar como GeoTIFF
    profile.update(dtype=rasterio.float32)
    with MemoryFile() as memfile:
        with memfile.open(**profile) as dst:
            dst.write(calibrated.astype(rasterio.float32), 1)
        mem_bytes = memfile.read()

    # Botón de descarga
    st.subheader("💾 Download Calibrated Image")
    st.download_button("📥 Download Calibrated TIFF", data=mem_bytes,
                       file_name=f"{zona}_{hora}_calibrated.tif", mime="image/tiff")
else:
    st.info("Please upload a thermal image to begin.")
