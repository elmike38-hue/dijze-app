import streamlit as st
import pandas as pd
from datetime import datetime

# CONFIGURACIÓN
st.set_page_config(page_title="Dijze Cotizador", page_icon="🪚")

# --- AQUÍ PEGA TU URL DE GOOGLE SHEETS ---
# Importante: El enlace debe terminar en /export?format=csv
SHEET_ID = "ID_DE_TU_HOJA" # El código largo que sale en la URL de tu Excel
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

def redondear_psicologico_dijze(numero):
    numero = int(numero)
    terminaciones = [36, 38, 39, 63, 68, 69, 83, 86, 89, 93, 96, 98]
    objetivo = numero + 550 
    base_centena = (objetivo // 100) * 100
    unidad_y_decena = objetivo % 100
    for t in terminaciones:
        if t > unidad_y_decena:
            if (base_centena // 100) % 10 != t // 10:
                return base_centena + t
    return (base_centena + 100) + terminaciones[0]

st.title("🪚 Carpintería Dijze")

with st.form("cotizador"):
    nombre_cliente = st.text_input("Nombre del Cliente")
    nombre_proyecto = st.text_input("Proyecto")
    c_maquila = st.number_input("Costo de la maquila ($)", min_value=0.0)
    c_accesorios = st.number_input("Costo en accesorios ($)", min_value=0.0)
    submit = st.form_submit_button("Generar y Guardar en Excel")

if submit:
    if nombre_cliente and nombre_proyecto:
        inv_base = (c_maquila + c_accesorios) / 0.7
        precio_final = redondear_psicologico_dijze(inv_base)
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        
        # MOSTRAR MENSAJE
        st.success(f"Propuesta generada para {nombre_cliente}")
        st.code(f"Fabricación y Ensamble de {nombre_proyecto}: ${precio_final:,.0f}")
        
        # --- LÓGICA DE GUARDADO (SIMPLIFICADA) ---
        # Nota: Para guardado directo desde el iPhone, lo ideal es usar la 
        # conexión nativa de Streamlit llamada 'st.connection("gsheets")'.
        st.info("Para que el guardado sea automático, necesitamos configurar los 'Secrets' en Streamlit Cloud.")
