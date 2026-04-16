import os
import base64
import streamlit as st
import numpy as np
from PIL import Image
from openai import OpenAI
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Tablero Inteligente", page_icon="🎨")

st.title("🎨 Tablero Inteligente")

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

stroke_width = st.sidebar.slider("Grosor del trazo", 1, 30, 5)

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.2)",
    stroke_width=stroke_width,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=300,
    width=400,
    drawing_mode="freedraw",
    key="canvas",
)

api_key = st.text_input("Ingresa tu API key", type="password")

if st.button("Probar API"):
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Responde solo: API funcionando"}
            ],
            max_tokens=20,
        )
        st.success(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error de prueba: {type(e).__name__}: {e}")

if st.button("Analizar dibujo"):
    try:
        if not api_key:
            st.warning("Ingresa tu API key.")
        elif canvas_result.image_data is None:
            st.warning("Dibuja algo primero.")
        else:
            client = OpenAI(api_key=api_key)

            input_numpy_array = np.array(canvas_result.image_data)
            input_image = Image.fromarray(input_numpy_array.astype("uint8"), "RGBA")
            input_image.save("img.png")

            base64_image = encode_image_to_base64("img.png")

            prompt_text = "Describe en español brevemente qué contiene este dibujo."

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
                max_tokens=200,
            )

            st.write(response.choices[0].message.content)

    except Exception as e:
        st.error(f"Ocurrió un error: {type(e).__name__}: {e}")
