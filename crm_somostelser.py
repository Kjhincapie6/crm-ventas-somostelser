import streamlit as st
import pandas as pd
import os

# 1. DATOS
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

# 2. CONFIGURACIÓN
st.set_page_config(page_title="Portal de Ventas Somos Telser", layout="wide")

# 3. INTERFAZ
st.title("📡 Portal de Ventas Somos Telser")

# Usamos un contenedor para que el radio button fuerce un recálculo
div = st.radio("Seleccione División:", ["Móvil", "Fijo"], horizontal=True)

# ASIGNACIÓN DINÁMICA DE TARIFAS
tarifas = PLANES_MOVIL if div == "Móvil" else PLANES_FIJO

with st.form("registro_full", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏢 Datos del Cliente")
        n_doc = st.text_input("Número de Documento:")
        nombre = st.text_input("Razón Social o Nombre:")
    with c2:
        st.subheader("📊 Plan y Estado")
        # Aquí es clave que 'tarifas' ya esté definido arriba según el radio button
        servicio = st.selectbox("Servicio:", list(tarifas.keys()))
        lineas = st.number_input("Cantidad / Líneas:", min_value=1, value=1)
        
        # CÁLCULO PRECISO:
        # Se asegura de buscar el precio en el diccionario que corresponde a la división activa
        precio_unitario = tarifas[servicio]
        dcto = 30 if lineas >= 9 else (25 if lineas >= 6 else (20 if lineas >= 3 else (10 if lineas == 2 else 0)))
        valor = (precio_unitario * lineas) * (1 - dcto/100)
        
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; border-left: 5px solid #1f77b4;">
            <p style="margin: 0; font-size: 1.1em;">💰 <b>Total a Pagar:</b> ${valor:,.0f} COP</p>
            <p style="margin: 0; font-size: 0.9em; color: #555;">Incluye descuento por volumen ({dcto}%)</p>
        </div>
        """, unsafe_allow_html=True)
        
        guardar = st.form_submit_button("💾 Guardar Venta")

if guardar:
    if n_doc and nombre:
        archivo = "crm_sistema_maestro.csv"
        df_ex = pd.read_csv(archivo) if os.path.exists(archivo) else pd.DataFrame()
        nueva_fila = pd.DataFrame([{'NIT': n_doc, 'CLIENTE': nombre, 'SERVICIO': servicio, 'VALOR_TOTAL': valor}])
        pd.concat([df_ex, nueva_fila]).to_csv(archivo, index=False)
        st.success("✅ Venta registrada.")
        st.rerun()
    else:
        st.error("⚠️ Faltan datos.")
# ==========================================
# 3. INTERFAZ Y AGENTE FINANCIERO
# ==========================================
st.title("📡 Portal de Ventas Somos Telser")
st.subheader("Gestión Inteligente de Contratos B2B")
div = st.radio("Seleccione División:", ["Móvil", "Fijo"], key="div_radio", horizontal=True)

with st.form("registro_full", clear_on_submit=True):
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("🏢 Datos del Cliente")
        t_doc = st.selectbox("Tipo Doc:", ["NIT", "Cédula", "CE", "PPT"])
        n_doc = st.text_input("Número de Documento:")
        nombre = st.text_input("Razón Social o Nombre:")
        dir = st.text_input("Dirección:")
        barrio = st.text_input("Barrio:")
        muni = st.text_input("Municipio:")
        email_cli = st.text_input("Correo Cliente:")
        movil_cli = st.text_input("Móvil Cliente:")
    
    with c2:
        st.subheader("👤 Representante Legal")
        nom_rep = st.text_input("Nombre Rep. Legal:")
        cc_rep = st.text_input("Cédula Rep. Legal:")
        mail_rep = st.text_input("Correo Rep. Legal:")
        tel_rep = st.text_input("Móvil Rep. Legal:")
        
        st.subheader("📊 Estado y Plan")
        estado = st.selectbox("Estado:", ["En proceso de firma", "Ingreso de pedido", "Activado"])
        bitacora = st.text_area("📝 Notas / Bitácora:")
        
        tarifas = PLANES_MOVIL if div == "Móvil" else PLANES_FIJO
        servicio = st.selectbox("Servicio:", list(tarifas.keys()))
        lineas = st.number_input("Líneas:", min_value=1, value=1)
        
        # --- CÁLCULO FINANCIERO DINÁMICO MEJORADO ---
        dcto = 30 if lineas >= 9 else (25 if lineas >= 6 else (20 if lineas >= 3 else (10 if lineas == 2 else 0)))
        valor = (tarifas[servicio] * lineas) * (1 - dcto/100)
        
        # Nota mejorada: Diseño más limpio y profesional
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; border-left: 5px solid #1f77b4;">
            <p style="margin: 0; font-size: 1.1em;">💰 <b>Total a Pagar:</b> ${valor:,.0f} COP</p>
            <p style="margin: 0; font-size: 0.9em; color: #555;">Incluye descuento por volumen ({dcto}%)</p>
        </div>
        """, unsafe_allow_html=True)
        
        guardar = st.form_submit_button("💾 Guardar Venta")

if guardar:
    if n_doc and nombre:
        archivo = "crm_sistema_maestro.csv"
        df_ex = pd.read_csv(archivo) if os.path.exists(archivo) else pd.DataFrame()
        nueva_fila = pd.DataFrame([{
            'ID_VENTA': len(df_ex) + 1, 'DIVISION': div, 'NIT': n_doc, 'CLIENTE': nombre,
            'SERVICIO': servicio, 'VALOR_TOTAL': valor, 'BITACORA': bitacora,
            'ESTADO_FINANCIERO': ("APROBADO" if valor >= 35000 else "REVISION")
        }])
        pd.concat([df_ex, nueva_fila]).to_csv(archivo, index=False)
        st.success("✅ Venta registrada correctamente.")
        st.rerun()
    else:
        st.error("⚠️ Faltan datos obligatorios.")
