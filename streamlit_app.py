import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dijze Pro", page_icon="🪚")

# 2. FUNCIÓN DE REDONDEO PSICOLÓGICO
def redondear_psicologico_dijze(numero):
    numero = int(numero)
    # Terminaciones que nos gustan para que el precio se vea "atractivo"
    terminaciones = [36, 38, 39, 63, 68, 69, 83, 86, 89, 93, 96, 98]
    # Sumamos un margen de seguridad de 550 antes de redondear
    objetivo = numero + 550 
    base_centena = (objetivo // 100) * 100
    unidad_y_decena = objetivo % 100
    
    for t in terminaciones:
        if t > unidad_y_decena:
            # Evitamos que la centena y la decena sean iguales (ej. 336)
            if (base_centena // 100) % 10 != t // 10:
                return base_centena + t
    # Si no encuentra en la centena actual, salta a la siguiente
    return (base_centena + 100) + terminaciones[0]

# 3. CONEXIÓN A GOOGLE SHEETS
# Esta conexión usa los Secrets que pegamos en Streamlit Cloud
conn = st.connection("gsheets", type=GSheetsConnection)

# 4. INTERFAZ DE USUARIO
st.title("🪚 Carpintería Dijze")
st.markdown("### Cotizador Profesional v1.2")

# Formulario para evitar recargas innecesarias
with st.form("cotizador_form", clear_on_submit=False):
    nombre_cliente = st.text_input("Nombre del Cliente")
    nombre_proyecto = st.text_input("Proyecto (ej. Closet de Cedro)")
    
    col1, col2 = st.columns(2)
    with col1:
        c_maquila = st.number_input("Costo de la maquila", min_value=0.0, step=100.0)
    with col2:
        c_accesorios = st.number_input("Costo en accesorios", min_value=0.0, step=100.0)
    
    # Botón principal del formulario
    submit = st.form_submit_button("Generar Propuesta y Guardar")

# 5. LÓGICA AL ENVIAR EL FORMULARIO
if submit:
    if nombre_cliente and nombre_proyecto:
        # Cálculo base: Margen del 30% (Dividir entre 0.7)
        inv_base = (c_maquila + c_accesorios) / 0.7
        precio_final = redondear_psicologico_dijze(inv_base)
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        
        # --- GUARDAR EN GOOGLE SHEETS ---
        # Creamos un pequeño DataFrame para anexar
        nueva_fila = pd.DataFrame([{
            "Fecha": fecha_hoy,
            "Cliente": nombre_cliente,
            "Proyecto": nombre_proyecto,
            "Inversion_Total": precio_final
        }])
        
        try:
            # Leemos lo que hay actualmente
            df_existente = conn.read()
            # Concatenamos la nueva fila al final
            df_actualizado = pd.concat([df_existente, nueva_fila], ignore_index=True)
            # Actualizamos la hoja completa (esto evita que se repitan filas en el mismo renglón)
            conn.update(data=df_actualizado)
            st.success("✅ Datos guardados en Google Sheets")
        except Exception as e:
            st.error(f"Error al guardar en la nube: {e}")
        
        # --- GENERAR MENSAJE ---
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
        
        st.subheader("Mensaje para WhatsApp:")
        st.text_area("Copia este texto:", mensaje, height=300)
        
    else:
        st.warning("⚠️ Por favor completa el nombre del cliente y el proyecto.")

# 6. BOTÓN DE REINICIO (Fuera del formulario)
if st.button("🔄 Nueva Cotización"):
    st.rerun()
