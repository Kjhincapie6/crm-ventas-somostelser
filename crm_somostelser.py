import streamlit as st
import pandas as pd
import os

# ==========================================
# 1. PORTAFOLIO MANUAL (JUNIO 2026)
# ==========================================
PLANES_MOVIL = {
    "Pospago Negocios 4.9 Plus+ (60 GB)": 44900.0,
    "Pospago Negocios 5.4 Plus+ (100 GB)": 53900.0,
    "Pospago 5.3 Empresarial (Ilim GB)": 113900.0
}
PLANES_FIJO = {
    "Internet Business 300 Mbps": 88880.0,
    "Internet Business 500 Mbps": 115000.0,
    "Internet Full Tigo Business 1000 Mbps": 274000.0
}

# ==========================================
# 2. INTERFAZ DE REGISTRO COMPLETA
# ==========================================
st.set_page_config(page_title="CRM Somos Telser - Junio 2026", layout="wide")
st.title("🏢 Gestión Integral de Contratos B2B")

div = st.radio("Seleccione División:", ["Móvil", "Fijo"], key="div_radio")

with st.form("registro_full"):
    # Sección Cliente
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
        
        tarifas = PLANES_MOVIL if div == "Móvil" else PLANES_FIJO
        servicio = st.selectbox("Servicio:", list(tarifas.keys()))
        lineas = st.number_input("Cantidad / Líneas:", min_value=1, value=1)

    # Cálculo y Guardado
    dcto = 30 if lineas >= 9 else (25 if lineas >= 6 else (20 if lineas >= 3 else (10 if lineas == 2 else 0)))
    valor = (tarifas[servicio] * lineas) * (1 - dcto/100)
    
    st.info(f"💰 Resumen: {div} | Servicio: {servicio} | Dcto: {dcto}% | Total: ${valor:,.0f} COP")
    
    if st.form_submit_button("💾 Guardar Venta Completa"):
        # Guardado en CSV (incluyendo todos los nuevos campos)
        nueva_fila = pd.DataFrame([{
            'DIVISION': div, 'NIT': n_doc, 'CLIENTE': nombre, 'DIRECCION': dir, 
            'BARRIO': barrio, 'MUNICIPIO': muni, 'EMAIL': email_cli, 'MOVIL': movil_cli,
            'REP_LEGAL': nom_rep, 'CC_REP': cc_rep, 'MAIL_REP': mail_rep, 
            'SERVICIO': servicio, 'VALOR_TOTAL': valor, 'ESTADO': estado
        }])
        
        archivo = "crm_sistema_maestro.csv"
        if os.path.exists(archivo):
            base = pd.read_csv(archivo)
            base = pd.concat([base, nueva_fila], ignore_index=True)
            base.to_csv(archivo, index=False)
        else:
            nueva_fila.to_csv(archivo, index=False)
            
        st.success("✅ Venta registrada con toda la información técnica y legal.")
