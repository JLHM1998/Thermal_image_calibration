import streamlit as st
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.io import MemoryFile
import datetime

# Configuración de la página
st.set_page_config(page_title="Calibración Térmica", layout="wide")

# Función para manejar la navegación
def navigate_to(section):
    st.experimental_set_query_params(section=section)

# Obtener el parámetro de consulta actual
query_params = st.experimental_get_query_params()
current_section = query_params.get("section", ["inicio"])[0]

# Panel de navegación dinámico
st.sidebar.title("Navegación")
menu_items = {
    "inicio": "Bienvenido a la aplicación de calibración térmica",
    "seleccionar-informacion": "Seleccionar información del vuelo",
    "seleccionar-hora": "Seleccionar hora del vuelo",
    "subir-imagen": "Subir tu imagen térmica (GeoTIFF)",
    "vista-previa-original": "Vista Previa - Imagen Original",
    "vista-previa-calibrada": "Vista Previa - Imagen Calibrada"
}

for key, value in menu_items.items():
    if st.sidebar.button(value):
        navigate_to(key)

# Diccionario de ecuaciones de calibración
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

# Mostrar contenido según la sección seleccionada
if current_section == "inicio":
    st.markdown("<a id='inicio'></a>", unsafe_allow_html=True)
    st.markdown("## Bienvenido a la aplicación de calibración térmica")
    st.markdown("""
    Esta aplicación permite cargar un ortomosaico térmico, aplicar una **ecuación de calibración** y visualizar los resultados.
    """)
    st.markdown("""
    La calibración indirecta de las imágenes térmicas obtenidas por la cámara H20T se realizó comparándolas con los datos medidos con un radiómetro en nueve coberturas. Para reescalar los valores de temperatura en las imágenes térmicas, se utilizó un radiómetro Apogee MI-210 (MI-210; Apogee Instruments, Inc., Logan, UT, USA). Este radiómetro se utilizó en nueve coberturas conocidas, incluyendo aluminio, hojas secas, hojas verdes, poliestireno expandido, tela amarilla, tela negra, tela roja, tela verde y suelo desnudo.
    """)

elif current_section == "seleccionar-informacion":
    st.markdown("<a id='seleccionar-informacion'></a>", unsafe_allow_html=True)
    st.markdown("## 🗺️ Seleccionar información del vuelo")
    region = st.selectbox("🌎 Seleccionar Región", ["Lambayeque", "Lima"])
    provincia = distrito = zona = None
    if region == "Lambayeque":
        provincia = st.selectbox("📍 Seleccionar Provincia", ["Ferreñafe", "Chiclayo"])
        if provincia == "Ferreñafe":
            zona = st.selectbox("🗺️ Seleccionar Zona", ["Capote"])
        elif provincia == "Chiclayo":
            distrito = st.selectbox("🏙️ Seleccionar Distrito", ["Chongoyape", "Picsi"])
            if distrito == "Chongoyape":
                zona = st.selectbox("🗺️ Seleccionar Zona", ["Carniche", "Paredones"])
            elif distrito == "Picsi":
                zona = "Picsi"
    elif region == "Lima":
        zona = st.selectbox("📍 Seleccionar Zona", ["La Molina"])
    if zona:
        st.write(f"Zona seleccionada: {zona}")

elif current_section == "seleccionar-hora":
    st.markdown("<a id='seleccionar-hora'></a>", unsafe_allow_html=True)
    st.markdown("## 🕒 Seleccionar hora del vuelo")
    hora = st.time_input("Selecciona la hora del vuelo:")
    if hora:
        st.write(f"Hora seleccionada: {hora}")

elif current_section == "subir-imagen":
    st.markdown("<a id='subir-imagen'></a>", unsafe_allow_html=True)
    st.markdown("## 📂 Subir tu imagen térmica (GeoTIFF)")
    uploaded_file = st.file_uploader("Selecciona tu archivo:", type=["tif", "tiff"])
    if uploaded_file is not None:
        with rasterio.open(uploaded_file) as src:
            profile = src.profile
            image = src.read(1).astype(np.float32)
        st.session_state["image"] = image
        st.write("Imagen cargada correctamente.")

elif current_section == "vista-previa-original":
    st.markdown("<a id='vista-previa-original'></a>", unsafe_allow_html=True)
    st.markdown("## 🗾 Vista Previa - Imagen Original")
    if "image" in st.session_state:
        image = st.session_state["image"]
        image_clipped = np.clip(image, 0, 70)
        vmin, vmax = np.percentile(image_clipped, [2, 98])
        fig, ax = plt.subplots(figsize=(6, 4))
        im = ax.imshow(image_clipped, cmap='inferno', vmin=vmin, vmax=vmax)
        ax.axis('off')
        cbar = fig.colorbar(im, ax=ax, label='Temperatura (°C)')
        st.pyplot(fig)
    else:
        st.warning("Por favor, sube una imagen primero.")

elif current_section == "vista-previa-calibrada":
    st.markdown("<a id='vista-previa-calibrada'></a>", unsafe_allow_html=True)
    st.markdown("## 🗾 Vista Previa - Imagen Calibrada")
    if "image" in st.session_state and "zona" in locals() and "hora" in locals():
        A, B = ecuaciones.get((zona, hora), (1.0, 0.0))
        calibrated = A * st.session_state["image"] + B
        calibrated = np.clip(calibrated, 0, 70)
        vmin, vmax = np.percentile(calibrated, [2, 98])
        fig, ax = plt.subplots(figsize=(6, 4))
        im = ax.imshow(calibrated, cmap='inferno', vmin=vmin, vmax=vmax)
        ax.axis('off')
        cbar = fig.colorbar(im, ax=ax, label='Temperatura Calibrada (°C)')
        st.pyplot(fig)
    else:
        st.warning("Por favor, selecciona una zona, una hora y sube una imagen primero.")

# Pie de página
st.markdown("""
    <footer style="text-align: center; padding: 10px; background-color: #1f6f8b; color: white; border-radius: 10px; margin-top: 50px;">
        © 2025 Universidad Nacional Agraria La Molina - Todos los derechos reservados.
        <br>
        Desarrollado por el Área Experimental de Riego - AER.
    </footer>
""", unsafe_allow_html=True)
