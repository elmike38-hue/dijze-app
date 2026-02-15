import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Dijze Pro", page_icon="🪚")

# Conectar a Google Sheets usando los Secrets configurados
conn = st.connection("gsheets", type=GSheetsConnection)

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
    c_maquila = st.number_input("Costo de la maquila", min_value=0.0, step=100.0)
    c_accesorios = st.number_input("Costo en accesorios", min_value=0.0, step=100.0)
    
    submit = st.form_submit_button("Generar Propuesta y Guardar")

if submit:
    if nombre_cliente and nombre_proyecto:
        inv_base = (c_maquila + c_accesorios) / 0.7
        precio_final = redondear_psicologico_dijze(inv_base)
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        
        # 1. Guardar en Google Sheets
        nueva_fila = pd.DataFrame([{
            "Fecha": fecha_hoy,
            "Cliente": nombre_cliente,
            "Proyecto": nombre_proyecto,
            "Inversion_Total": precio_final
        }])
        
        # Leer datos actuales y concatenar el nuevo
        df_existente = conn.read()
        df_actualizado = pd.concat([df_existente, nueva_fila], ignore_index=True)
        conn.update(data=df_actualizado)
        
        # 2. Mostrar Mensaje de WhatsApp
        st.success("✅ Guardado en Excel y Mensaje Generado")
        
        mensaje = (
            f"Hola {nombre_cliente}, que gusto saludarte, gracias por la confianza.\n\n"
            f"Revisando los requerimientos el valor de inversión del proyecto con los acabados requeridos\n"
            f"Fabricación y Ensamble de {nombre_proyecto} ${precio_final:,.0f}\n\n"
            f"Normalmente, un proyecto de esta naturaleza lo cotizamos un poco más elevado. "
            f"Sin embargo, tu al ser un cliente recomendado estamos ofreciendo una bonificación especial.\n\n"
            f"En este momento podemos ofrecerlo de esta forma ya que hemos estado trabajando en sitio. "
            f"Además, nuestra agenda de fabricación para las próximas semanas está por llenarse; "
            f"solo nos quedan unos días disponibles.\n\n"
            f"Sabiendo esto, cuéntame, ¿prefieres que agendemos próximos días acudir contigo "
            f"definir dimensiones, materiales y poder comenzar el trabajo en próximos días disponibles?"
        )
        
        st.text_area("Copia para WhatsApp:", mensaje, height=300)
    else:
        st.error("Por favor llena los nombres.")
