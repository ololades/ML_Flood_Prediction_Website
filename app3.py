import gradio as gr
import joblib
import numpy as np
import os

# ---------------- CSS ----------------
UI_css = """
.gradio-container {
    background-color: #f2f2f2 !important;
    color: white;
    max-width: 1400px !important;
}

h1 {
    text-align: center;
    font-size: 26px;
    color: #1e90ff;
}

#map-panel {
    border: 3px solid #1e90ff;
    border-radius: 12px;
    overflow: hidden;
    padding: 5px;
}

#form-panel {
    padding: 20px;
    background-color: #1f1f1f;
    border-radius: 12px;
}

button {
    background-color: #1e90ff !important;
    color: white !important;
    border-radius: 8px !important;
}
"""

# ---------------- Load model safely ----------------
MODEL_PATH = "model_pkl/RF_model.pkl"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at: {MODEL_PATH}")

model = joblib.load(MODEL_PATH)

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
def predict_flood(elevation, landuse, rainfall, population, soil):

    # Validate inputs
    if None in [elevation, landuse, rainfall, population, soil]:
        return "⚠️ Please fill all fields"

    try:
        elevation = float(elevation)
        rainfall = float(rainfall)
        population = float(population)

        landuse_val = landuse_map.get(landuse)
        soil_val = soil_map.get(soil)

        if landuse_val is None or soil_val is None:
            return "⚠️ Invalid categorical input selected"

        X = np.array([[elevation, landuse_val, rainfall, population, soil_val]])
        pred = model.predict(X)[0]

        return "🚨 High Flood Risk" if pred == 1 else "🟢 Low Flood Risk"

    except Exception as e:
        return f"❌ Error: {str(e)}"


# ---------------- Map ----------------
nigeria_map_html = """
<iframe 
    width="100%" 
    height="500"
    frameborder="0"
    style="border:0; border-radius:12px;"
    src="https://www.openstreetmap.org/export/embed.html?bbox=2.7,4.0,14.7,14.0&layer=mapnik">
</iframe>
"""

# ---------------- UI ----------------
with gr.Blocks(css=UI_css) as demo:

    gr.Markdown("# 🌧️ Flood Susceptibility Prediction Dashboard")

    with gr.Row():

        with gr.Column(scale=1, elem_id="map-panel"):
            gr.Markdown("### 🗺️ Nigeria Study Area")
            gr.HTML(nigeria_map_html)

        with gr.Column(scale=1, elem_id="form-panel"):

            gr.Markdown("### 🌧️ Input Parameters")

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

            btn = gr.Button("🚀 Predict Flood Risk")
            output = gr.Textbox(label="Result")

            btn.click(
                predict_flood,
                inputs=[elevation, landuse, rainfall, population, soil],
                outputs=output
            )

demo.launch()