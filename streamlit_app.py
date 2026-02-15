import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dijze Pro", page_icon="🪚")

# 2. FUNCIÓN DE REDONDEO
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

# 3. CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🪚 Carpintería Dijze")

# 4. FORMULARIO
with st.form("cotizador_form", clear_on_submit=True):
    nombre = st.text_input("Nombre del Cliente")
    proyecto = st.text_input("Proyecto")
    
    col1, col2 = st.columns(2)
    with col1:
        maquila = st.number_input("Costo de la maquila", min_value=0.0, step=100.0)
    with col2:
        accesorios = st.number_input("Costo en accesorios", min_value=0.0, step=100.0)
    
    submit = st.form_submit_button("Generar y Guardar")

# 5. LÓGICA DE GUARDADO Y MENSAJE
if submit:
    if nombre and proyecto:
        inv_base = (maquila + accesorios) / 0.7
        precio_final = redondear_psicologico_dijze(inv_base)
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        
        try:
            # Leer y actualizar Excel
            df_actual = conn.read(ttl=0)
            nueva_fila = pd.DataFrame([{
                "Fecha": fecha_hoy,
                "Cliente": nombre,
                "Proyecto": proyecto,
                "Inversion_Total": precio_final
            }])
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(data=df_final)
            
            st.success(f"✅ Guardado con éxito")
            
            # --- GENERAR MENSAJE ---
            mensaje = (
                f"Hola {nombre}, que gusto saludarte, gracias por la confianza.\n\n"
                f"Revisando los requerimientos el valor de inversión del proyecto con los acabados requeridos\n"
                f"Fabricación y Ensamble de {proyecto} ${precio_final:,.0f}\n\n"
                f"Normalmente, un proyecto de esta naturaleza lo cotizamos un poco más elevado. "
                f"Sin embargo, tu al ser un cliente recomendado estamos ofreciendo una bonificación especial.\n\n"
                f"Sabiendo esto, cuéntame, ¿prefieres que agendemos próximos días?"
            )
            
            st.markdown("### 📋 Mensaje para copiar:")
            # Este bloque crea el cuadro con el botón de copiar automático
            st.code(mensaje, language=None)
            
        except Exception as e:
            st.error(f"Error al guardar: {e}")
    else:
        st.error("⚠️ Por favor rellena el nombre y el proyecto.")

# 6. BOTÓN DE REINICIO
if st.button("🔄 Nueva Cotización (Limpiar Pantalla)"):
    st.rerun()
