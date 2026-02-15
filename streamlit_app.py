import streamlit as st
from datetime import datetime

# CONFIGURACIÓN ESTÉTICA
st.set_page_config(page_title="Dijze Cotizador", page_icon="🪚")

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

# --- INTERFAZ ---
st.title("🪚 Carpintería Dijze")
st.info("Versión 1.0 - Generador de Propuestas")

# Formulario de entrada
with st.container():
    nombre_cliente = st.text_input("Nombre del Cliente")
    nombre_proyecto = st.text_input("Proyecto (ej. Puerta principal)")
    
    col1, col2 = st.columns(2)
    with col1:
        c_maquila = st.number_input("Costo de la maquila ($)", min_value=0.0, step=100.0)
    with col2:
        c_accesorios = st.number_input("Costo en accesorios ($)", min_value=0.0, step=100.0)

# Botón de proceso
if st.button("Generar Propuesta Profesional"):
    if nombre_cliente and nombre_proyecto:
        inv_base = (c_maquila + c_accesorios) / 0.7
        precio_final = redondear_psicologico_dijze(inv_base)
        
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
        
        st.subheader("Mensaje listo para enviar:")
        st.text_area("Copia el texto aquí abajo:", mensaje, height=350)
        st.caption("Recuerda: Estás vendiendo el destino, no el avión.")
    else:
        st.warning("Completa los nombres para continuar.")
