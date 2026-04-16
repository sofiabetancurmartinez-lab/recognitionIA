import os
import base64
import streamlit as st
import numpy as np
from PIL import Image
from openai import OpenAI
from streamlit_drawable_canvas import st_canvas

# -----------------------------
# Configuración general
# -----------------------------
st.set_page_config(page_title="Tablero Inteligente", page_icon="🎨", layout="centered")

st.title("🎨 Tablero Inteligente")
st.markdown("Dibuja algo y deja que la IA lo interprete, lo mejore y proponga una idea creativa basada en tu boceto.")

# -----------------------------
# Funciones auxiliares
# -----------------------------
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.subheader("⚙️ Configuración")
    st.write("En esta aplicación la IA interpreta el boceto y propone una versión más clara y creativa.")

    stroke_width = st.slider("Grosor del trazo", 1, 30, 5)
    canvas_width = st.slider("Ancho del lienzo", 300, 800, 400, 50)
    canvas_height = st.slider("Alto del lienzo", 200, 600, 300, 50)

    stroke_color = "#000000"
    bg_color = "#FFFFFF"

    clear_canvas = st.button("🗑️ Limpiar lienzo")

# -----------------------------
# Canvas de dibujo
# -----------------------------
st.subheader("🖌️ Dibuja aquí tu idea")

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.2)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=canvas_height,
    width=canvas_width,
    drawing_mode="freedraw",
    key=f"canvas_{clear_canvas}_{canvas_width}_{canvas_height}",
)

# -----------------------------
# API Key
# -----------------------------
st.subheader("🔑 API Key")
api_key = st.text_input("Ingresa tu OpenAI API Key", type="password")

analyze_button = st.button("✨ Analizar dibujo", type="primary")

# -----------------------------
# Lógica principal
# -----------------------------
if analyze_button:
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
    elif canvas_result.image_data is None:
        st.warning("Por favor dibuja algo antes de analizar.")
    else:
        try:
            client = OpenAI(api_key=api_key)

            with st.spinner("Analizando tu dibujo..."):
                # Convertir el canvas a imagen
                input_numpy_array = np.array(canvas_result.image_data)
                input_image = Image.fromarray(input_numpy_array.astype("uint8"), "RGBA")
                image_path = "img.png"
                input_image.save(image_path)

                # Codificar imagen
                base64_image = encode_image_to_base64(image_path)

                prompt_text = """
                Analiza este boceto hecho a mano.
                Responde en español y con este formato exacto:

                1. ¿Qué parece ser?
                2. Descripción breve del dibujo
                3. ¿Cómo podría mejorarse visualmente?
                4. Una idea creativa o funcional basada en ese dibujo
                5. Un prompt final para convertir este boceto en una ilustración digital clara y atractiva

                Sé claro, útil y breve.
                """

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=500,
                )

                result = response.choices[0].message.content

                st.success("Análisis completado")
                st.subheader("🧠 Resultado de la IA")
                st.write(result)

                st.subheader("🖼️ Tu dibujo")
                st.image(image_path, caption="Boceto enviado a la IA", use_container_width=True)

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
