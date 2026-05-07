import gradio as gr
import joblib
import numpy as np
import pandas as pd
import folium
import os

# ---------------- CSS ----------------
UI_css = """
.gradio-container {
    background-color: #d9d9d9 !important;
    max-width: 1500px !important;
}

h1 {
    text-align: center;
    font-size: 26px;
    color: #1e90ff;
}

#map-panel {
    border: 3px solid #ff6600;
    border-radius: 35px;
    overflow: hidden;
    padding: 55px;
}

#form-panel {
    padding: 2px;
    background-color: #ff6600;
    border-radius: 12px;
    color: white;
}



/* INPUT FIX (WHITE FIELDS) */
#form-panel input,
#form-panel textarea,
#form-panel select {
    background-color: white !important;
    color: black !important;
    border-radius: 6px !important;
}

/* BUTTON */
button {
    background-color: #1e90ff !important;
    color: white !important;
    border-radius: 8px !important;
}
"""

# ---------------- Load model ----------------
MODEL_PATH = "model_pkl/RandomForest_model.pkl"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at: {MODEL_PATH}")

model = joblib.load(MODEL_PATH)

def default_map():
    m = folium.Map(
        location=[9, 8],   # center of Nigeria
        zoom_start=5,
        tiles="CartoDB positron"
    )
    return m._repr_html_()
default_map_html = default_map()


# ---------------- Encoders ----------------
soil_map = {
    "Fluvisols": 11,
    "Acrisols": 0,
    "Cambisols": 6,
    "Gleysols": 12,
    "Vertisols": 29,
    "Arenosols": 4,
    "Lixisols": 17,
    "Luvisols": 18
}

landuse_map = {
    "Rangeland": 7,
    "Built Area": 2,
    "Bare Ground": 1,
    "Wetland": 11,
    "Trees": 8,
    "Flooded Vegetation": 5,
    "Crops": 4
}



# ---------------- Prediction function ----------------
def predict_flood(elevation, landuse, rainfall, population, soil, lat, lon):

    if None in [elevation, landuse, rainfall, population, soil, lat, lon]:
        return "⚠️ Please fill all fields", ""

    try:
        # Convert inputs
        elevation = float(elevation)
        rainfall = float(rainfall)
        population = float(population)
        lat = float(lat)
        lon = float(lon)

        landuse_val = landuse_map.get(landuse)
        soil_val = soil_map.get(soil)

        # ---------------- FIX: DataFrame (removes sklearn warning) ----------------
        X = pd.DataFrame([{
            "elevation": elevation,
            "landuse": landuse_val,
            "rainfall": rainfall,
            "population": population,
            "soil": soil_val
        }])

        pred = model.predict(X)[0]

        # ---------------- RESULT ----------------
        if pred == 1:
            result = "🚨 High Flood Risk"
            color = "red"
        else:
            result = "🟢 Low Flood Risk"
            color = "green"

        # ---------------- MAP ----------------
        m = folium.Map(
            location=[lat, lon],
            zoom_start=10,
            tiles="CartoDB positron"
        )

        folium.CircleMarker(
            location=[lat, lon],
            radius=12,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=result
        ).add_to(m)

        folium.Circle(
            location=[lat, lon],
            radius=3000,
            color=color,
            fill=True,
            fill_opacity=0.2
        ).add_to(m)

        return result, m._repr_html_()

    except Exception as e:
        return f"❌ Error: {str(e)}", ""


# ---------------- UI ----------------
with gr.Blocks(css=UI_css) as demo:

    gr.Markdown("# 🌧️ ML Flood Prediction System")

    with gr.Row():

        # ---------------- MAP ----------------
        with gr.Column(scale=1, elem_id="map-panel"):
            gr.Markdown("### 🗺️ Flood Location Map")
            map_output = gr.HTML(value=default_map_html)

        # ---------------- FORM ----------------
        with gr.Column(scale=1, elem_id="form-panel"):

            gr.Markdown("### Enter Values")

            with gr.Row():
                elevation = gr.Number(label="Elevation")
                rainfall = gr.Number(label="Rainfall")

            population = gr.Number(label="Population Density")

            with gr.Row():
                landuse = gr.Dropdown(
                    choices=list(landuse_map.keys()),
                    label="Land Use"
                )

                soil = gr.Dropdown(
                    choices=list(soil_map.keys()),
                    label="Soil Type"
                )

            with gr.Row():
                lat = gr.Number(label="Latitude")
                lon = gr.Number(label="Longitude")

            btn = gr.Button("🚀 Predict Flood Risk")
            output = gr.Textbox(label="Result")

            btn.click(
                predict_flood,
                inputs=[
                    elevation,
                    landuse,
                    rainfall,
                    population,
                    soil,
                    lat,
                    lon
                ],
                outputs=[output, map_output]
            )

# ---------------- LAUNCH (Gradio 6 fix) ----------------
demo.launch()