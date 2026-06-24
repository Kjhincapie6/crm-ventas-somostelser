import streamlit as st
import pandas as pd
import os

# ==========================================
# 1. PORTAFOLIO Y DATOS
# ==========================================
PLANES_MOVIL = {
    "Pospago Negocios 4.9 Plus+ (60 GB)": 44900.0,
    "Pospago Negocios 5.4 Plus+ (100 GB)": 53900.0,
    "Pospago 5.3 Empresarial (Ilim GB)": 113900.0,
    "Plan Datos Tigo Empresarial 6.9 (30 GB)": 38300.0,
    "Plan Datos Tigo Empresarial 6.10 (60 GB)": 47900.0,
    "Plan Datos Tigo Empresarial 6.11 (110 GB)": 57900.0,
    "Plan Datos Tigo Empresarial 6.12 (Ilim GB)": 113900.0,
    "Plan Datos Tigo Empresarial 6.8 FULL TIGO (Ilim GB)": 54900.0
}

PLANES_FIJO = {
    "Internet Business 300 Mbps (HFC/FTTx)": 88880.0,
    "Internet Business 500 Mbps (HFC/FTTx)": 115000.0,
    "Internet Business 700 Mbps (HFC/FTTx)": 180001.0,
    "Internet Full Tigo Business 500 Mbps": 144000.0,
    "Internet Full Tigo Business 700 Mbps": 174000.0,
    "Internet Full Tigo Business 1000 Mbps": 274000.0
}

# ==========================================
# 2. CONFIGURACIÓN E IDENTIDAD
# ==========================================
st.set_page_config(page_title="CRM Somos Telser - Junio 2026", layout="wide")

if 'correo_asesor' not in st.session_state:
    st.session_state.correo_asesor = "ASESOR.B2B@SOMOSTELSER.COM"

with st.sidebar:
    if os.path.exists("logo_somostelser.png"):
        st.image("logo_somostelser.png", use_container_width=True)
    st.markdown(f"👤 **Asesor:** `{st.session_state.correo_asesor}`")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.correo_asesor = None
        st.rerun()

st.title("🏢 Gestión Integral de Contratos B2B")
div = st.radio("Seleccione División:", ["Móvil", "Fijo"], key="div_radio", horizontal=True)

# ==========================================
# 3. INTERFAZ Y AGENTE FINANCIERO
# ==========================================
with st.form("registro_full", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏢 Datos del Cliente")
        t_doc = st.selectbox("Tipo Doc:", ["NIT", "Cédula", "CE", "PPT"])
        n_doc = st.text_input("Número de Documento:")
        nombre = st.text_input("Razón Social o Nombre:")
        dir = st.text_input("Dirección de instalación:")
        barrio = st.text_input("Barrio:")
        muni = st.text_input("Municipio / Departamento:")
        email_cli = st.text_input("Correo Electrónico del Cliente:")
        movil_cli = st.text_input("Móvil de Contacto:")
    with c2:
        st.subheader("👤 Representante Legal")
        nom_rep = st.text_input("Nombre del Rep. Legal:")
        cc_rep = st.text_input("Cédula Rep. Legal:")
        mail_rep = st.text_input("Correo Rep. Legal:")
        tel_rep = st.text_input("Móvil Rep. Legal:")
        st.subheader("📊 Estado y Plan")
        estado = st.selectbox("Estado del Proceso:", ["En proceso de firma", "Enviado", "Ingreso de pedido", "Instalacion y aprovisionamiento", "Instalado", "Activado", "Cancelado", "Anulado"])
        
        tarifas = PLANES_MOVIL if div == "Móvil" else PLANES_FIJO
        servicio = st.selectbox("Servicio:", list(tarifas.keys()))
        lineas = st.number_input("Cantidad / Líneas:", min_value=1, value=1)

    # Lógica de Agente Financiero
    dcto = 30 if lineas >= 9 else (25 if lineas >= 6 else (20 if lineas >= 3 else (10 if lineas == 2 else 0)))
    valor = (tarifas[servicio] * lineas) * (1 - dcto/100)
    umbral = 35000.0
    
    # Validaciones visuales (Sin mover tus elementos de sitio)
    if n_doc and nombre and valor > 0:
        es_rentable = valor >= umbral
        if es_rentable:
            st.success("✅ Venta financieramente saludable.")
        else:
            st.warning("⚠️ Alerta: Rentabilidad baja, requiere aprobación gerencial.")
    else:
        st.info("ℹ️ Complete los datos del cliente para auditar la rentabilidad.")
        
    st.info(f"💰 **Resumen:** {div} | {servicio} | Dcto: {dcto}% | **Total: ${valor:,.0f} COP**")
    
    guardar = st.form_submit_button("💾 Guardar Venta Completa")

# Lógica de guardado fuera del form
if guardar:
    if n_doc and nombre:
        estado_financiero = "APROBADO" if valor >= umbral else "REVISION"
        nueva_fila = pd.DataFrame([{
            'DIVISION': div, 'NIT': n_doc, 'CLIENTE': nombre, 'DIRECCION': dir, 
            'BARRIO': barrio, 'MUNICIPIO': muni, 'EMAIL': email_cli, 'MOVIL': movil_cli,
            'REP_LEGAL': nom_rep, 'CC_REP': cc_rep, 'MAIL_REP': mail_rep, 
            'SERVICIO': servicio, 'VALOR_TOTAL': valor, 'ESTADO': estado,
            'ESTADO_FINANCIERO': estado_financiero,
            'ASESOR_REGISTRO': st.session_state.correo_asesor
        }])
        archivo = "crm_sistema_maestro.csv"
        pd.concat([pd.read_csv(archivo) if os.path.exists(archivo) else pd.DataFrame(), nueva_fila]).to_csv(archivo, index=False)
        st.success("✅ Venta registrada correctamente.")
    else:
        st.error("⚠️ Error: Debe ingresar el Documento y el Nombre del Cliente.")
# ... (tu código del formulario sigue igual hasta aquí) ...
    guardar = st.form_submit_button("💾 Guardar Venta Completa")

# Lógica de guardado y Agente Financiero
if guardar:
    if n_doc and nombre:
        # Generar Consecutivo (ID_VENTA)
        archivo = "crm_sistema_maestro.csv"
        if os.path.exists(archivo):
            df_existente = pd.read_csv(archivo)
            nuevo_id = len(df_existente) + 1
        else:
            nuevo_id = 1
        
        estado_financiero = "APROBADO" if valor >= umbral else "REVISION"
        
        nueva_fila = pd.DataFrame([{
            'ID_VENTA': nuevo_id, # <--- ¡Aquí se asigna el número!
            'DIVISION': div, 'NIT': n_doc, 'CLIENTE': nombre, 'DIRECCION': dir, 
            'BARRIO': barrio, 'MUNICIPIO': muni, 'EMAIL': email_cli, 'MOVIL': movil_cli,
            'REP_LEGAL': nom_rep, 'CC_REP': cc_rep, 'MAIL_REP': mail_rep, 
            'SERVICIO': servicio, 'VALOR_TOTAL': valor, 'ESTADO': estado,
            'ESTADO_FINANCIERO': estado_financiero,
            'ASESOR_REGISTRO': st.session_state.correo_asesor
        }])
        
        # Guardar en archivo
        pd.concat([pd.read_csv(archivo) if os.path.exists(archivo) else pd.DataFrame(), nueva_fila]).to_csv(archivo, index=False)
        st.success(f"✅ Venta #{nuevo_id} registrada correctamente.")
    else:
        st.error("⚠️ Error: Debe ingresar el Documento y el Nombre del Cliente.")

# ==========================================
# 4. DASHBOARD EJECUTIVO (VISUALIZACIÓN)
# ==========================================
st.markdown("---")
st.subheader("📊 Dashboard de Rendimiento de Ventas")
# ... (tu código del dashboard sigue aquí) ...
# ==========================================
# 4. DASHBOARD EJECUTIVO (VISUALIZACIÓN)
# ==========================================
st.markdown("---")
st.subheader("📊 Dashboard de Rendimiento de Ventas")

# Verificamos si el archivo existe y tiene datos
if os.path.exists("crm_sistema_maestro.csv"):
    df_ventas = pd.read_csv("crm_sistema_maestro.csv")
    
    if not df_ventas.empty:
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.write("### Ventas por División")
            st.bar_chart(df_ventas['DIVISION'].value_counts())
            
        with col_g2:
            st.write("### Auditoría Financiera")
            st.bar_chart(df_ventas['ESTADO_FINANCIERO'].value_counts())
    else:
        st.warning("⚠️ El archivo de datos está vacío. Realiza tu primera venta para visualizar el dashboard.")
else:
    st.info("ℹ️ Sistema listo: Realiza la primera venta para generar el Dashboard de rendimiento.")
