import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Dijze Pro", page_icon="🪚")

# 2. FUNCIÓN PARA LIMPIAR TODO
def limpiar_formulario():
    st.session_state["cliente"] = ""
    st.session_state["proyecto"] = ""
    st.session_state["maquila"] = 0.0
    st.session_state["accesorios"] = 0.0
    st.rerun()

# 3. REDONDEO
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

# 4. CONEXIÓN (Sin caché para evitar sobrescribir)
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🪚 Carpintería Dijze")

# 5. FORMULARIO CON LLAVES (KEYS) PARA LIMPIEZA
with st.form("cotizador_form"):
    st.text_input("Nombre del Cliente", key="cliente")
    st.text_input("Proyecto", key="proyecto")
    
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Costo de la maquila", min_value=0.0, step=100.0, key="maquila")
    with col2:
        st.number_input("Costo en accesorios", min_value=0.0, step=100.0, key="accesorios")
    
    submit = st.form_submit_button("Generar y Guardar")

# 6. ACCIÓN AL GUARDAR
if submit:
    # Extraemos los valores de las "keys"
    nombre = st.session_state["cliente"]
    proy = st.session_state["proyecto"]
    maq = st.session_state["maquila"]
    acc = st.session_state["accesorios"]

    if nombre and proy:
        inv_base = (maq + acc) / 0.7
        precio_final = redondear_psicologico_dijze(inv_base)
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        
        try:
            # Leemos la hoja actual (ttl=0 para datos frescos)
            df_actual = conn.read(ttl=0)
            
            # Creamos la fila nueva
            nueva_fila = pd.DataFrame([{
                "Fecha": fecha_hoy,
                "Cliente": nombre,
                "Proyecto": proy,
                "Inversion_Total": precio_final
            }])
            
            # Unimos y subimos todo
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(data=df_final)
            
            st.success(f"✅ Guardado: {nombre} - ${precio_final:,.0f}")
            
            # Mensaje WhatsApp
            mensaje = f"Hola {nombre}, presupuesto para {proy}: ${precio_final:,.0f}. ¿Agendamos?"
            st.text_area("Copia esto:", mensaje)
            
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Faltan datos")

# 7. BOTÓN DE REINICIO REAL
st.button("🔄 Nueva Cotización (Limpiar todo)", on_click=limpiar_formulario)
