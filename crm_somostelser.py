import streamlit as st
import pandas as pd
import os

# ==========================================
# 1. PORTAFOLIO Y DATOS (JUNIO 2026)
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
# 2. CONFIGURACIÓN E IDENTIDAD CORPORATIVA
# ==========================================
st.set_page_config(page_title="CRM Somos Telser - Junio 2026", layout="wide")

# Inicialización de Sesión (Simulada para el usuario conectado)
if 'correo_asesor' not in st.session_state:
    st.session_state.correo_asesor = "ASESOR.B2B@SOMOSTELSER.COM"

# Barra Lateral: Identidad y Control
with st.sidebar:
    if os.path.exists("logo_somostelser.png"):
        st.image("logo_somostelser.png", use_container_width=True)
    else:
        st.info("⚠️ Logo no encontrado (añade 'logo_somostelser.png')")
    
    st.markdown(f"👤 **Asesor:** `{st.session_state.correo_asesor}`")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.correo_asesor = None
        st.rerun()

# ==========================================
# 3. INTERFAZ DE REGISTRO OPTIMIZADA
# ==========================================
st.title("🏢 Gestión Integral de Contratos B2B")
st.markdown("---")

# Selector de división con reactividad
div = st.radio("Seleccione División:", ["Móvil", "Fijo"], key="div_radio", horizontal=True)

with st.form("registro_full"):
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
        estado = st.selectbox("Estado del Proceso:", [
            "En proceso de firma", "Enviado", "Ingreso de pedido", 
            "Instalacion y aprovisionamiento", "Instalado", "Activado", 
            "Cancelado", "Anulado"
        ])
        
        # Selección dinámica de planes
        tarifas = PLANES_MOVIL if div == "Móvil" else PLANES_FIJO
        servicio = st.selectbox("Servicio:", list(tarifas.keys()))
        lineas = st.number_input("Cantidad / Líneas:", min_value=1, value=1)

    # Cálculo del valor con descuento
    dcto = 30 if lineas >= 9 else (25 if lineas >= 6 else (20 if lineas >= 3 else (10 if lineas == 2 else 0)))
    valor = (tarifas[servicio] * lineas) * (1 - dcto/100)

    # --- AGENTE FINANCIERO INTELIGENTE ---
def calcular_rentabilidad_y_validar(valor_final, lineas):
    # Definimos un umbral de rentabilidad mínima (ejemplo: 35.000 COP)
    umbral_minimo = 35000.0
    
    # Lógica de Auditoría: ¿Es rentable la venta?
    es_rentable = valor_final >= umbral_minimo
    mensaje = "✅ Venta financieramente saludable." if es_rentable else "⚠️ Alerta: Rentabilidad baja, requiere aprobación."
    
    return es_rentable, mensaje

# En tu formulario, después del cálculo del 'valor':
es_rentable, mensaje_auditoria = calcular_rentabilidad_y_validar(valor, lineas)

# Mostrar el diagnóstico en tiempo real
if es_rentable:
    st.success(mensaje_auditoria)
else:
    st.warning(mensaje_auditoria)
    # Resumen visual mejorado
    st.info(f"💰 **Resumen:** División: **{div}** | Servicio: **{servicio}** | Descuento: **{dcto}%** | **Total: ${valor:,.0f} COP**")
    
    # Guardado de Venta
    if st.form_submit_button("💾 Guardar Venta Completa"):
        nueva_fila = pd.DataFrame([{
            'DIVISION': div, 'NIT': n_doc, 'CLIENTE': nombre, 'DIRECCION': dir, 
            'BARRIO': barrio, 'MUNICIPIO': muni, 'EMAIL': email_cli, 'MOVIL': movil_cli,
            'REP_LEGAL': nom_rep, 'CC_REP': cc_rep, 'MAIL_REP': mail_rep, 
            'SERVICIO': servicio, 'VALOR_TOTAL': valor, 'ESTADO': estado,
            'ASESOR_REGISTRO': st.session_state.correo_asesor
        }])
        
        archivo = "crm_sistema_maestro.csv"
        if os.path.exists(archivo):
            base = pd.read_csv(archivo)
            base = pd.concat([base, nueva_fila], ignore_index=True)
            base.to_csv(archivo, index=False)
        else:
            nueva_fila.to_csv(archivo, index=False)
            
        st.success("✅ Venta registrada correctamente con trazabilidad del asesor.")
