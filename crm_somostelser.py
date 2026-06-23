import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de Marca y Estilo de la Aplicación Corporativa
st.set_page_config(
    page_title="CRM Inteligente - Somostelser S.A.S.",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado para un look profesional moderno
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #0ea5e9; margin-bottom: 5px; }
    .subtitle { font-size: 16px; color: #64748b; margin-bottom: 25px; }
    .metric-card { background-color: #f8fafc; border-left: 5px solid #0ea5e9; padding: 15px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# 2. Carga Segura de Datos Optimizado para Streamlit
@st.cache_data
def cargar_datos_maestros():
    try:
        # Intentamos leer la base de datos ya procesada por el Agente Financiero
        df = pd.read_csv("crm_sistema_maestro.csv")
    except FileNotFoundError:
        # Respaldo en caso de leer el archivo base original
        df = pd.read_csv("Somostelser.csv")
        df.columns = [col.upper() for col in df.columns]
        if 'CONTRATO' in df.columns:
            df['CONTRATO'] = pd.to_numeric(df['CONTRATO'], errors='coerce').fillna(0)
            
        # Lógica del Agente Financiero integrada en el backend del frontend
        def auditar(fila):
            if str(fila.get('ESTADO')).strip().upper() == 'ANULADO':
                servicio = str(fila.get('SERVICIO')).upper()
                contrato = fila.get('CONTRATO')
                if 'AVANZADO' in servicio:
                    return ('🚨 CRÍTICO', f'Downgrade a plan BÁSICO con 25% de desc. sobre tarifa de ${contrato:,.0f}')
                return ('⚠️ MODERADO', 'Plan Retención Pyme con 15% de desc. o congelación de tarifa.')
            return ('✅ ESTABLE', 'Cliente activo. Monitoreo regular.')
            
        auditoria = df.apply(auditar, axis=1)
        df['RIESGO_IA'] = [r[0] for r in auditoria]
        df['RECOMENDACION_AGENTE'] = [r[1] for r in auditoria]
    return df

df_crm = cargar_datos_maestros()

# 3. Panel Lateral: Buscador y Filtros Interactivos del CRM
st.sidebar.image("https://via.placeholder.com/150x50.png?text=Somostelser", use_container_width=True)
st.sidebar.markdown("### 🔍 Panel de Búsqueda B2B")

buscar_cliente = st.sidebar.text_input("Buscar por Nombre de Cliente:")
filtro_estado = st.sidebar.selectbox("Filtrar por Estado:", ['TODOS'] + list(df_crm['ESTADO'].unique()))
filtro_servicio = st.sidebar.selectbox("Filtrar por Servicio:", ['TODOS'] + list(df_crm['SERVICIO'].unique()))

# Aplicar las consultas del usuario a la base del CRM en tiempo real
df_filtrado = df_crm.copy()
if buscar_cliente:
    df_filtrado = df_filtrado[df_filtrado['NOMBRE_CLIENTE'].str.contains(buscar_cliente, case=False, na=False)]
if filtro_estado != 'TODOS':
    df_filtrado = df_filtrado[df_filtrado['ESTADO'] == filtro_estado]
if filtro_servicio != 'TODOS':
    df_filtrado = df_filtrado[df_filtrado['SERVICIO'] == filtro_servicio]

# 4. Panel Principal: Interfaz Gráfica de Usuario (GUI)
st.markdown('<p class="main-title">🏢 Sistema CRM Inteligente — Somostelser S.A.S.</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Módulo de Auditoría Comercial Integrado con Agente Financiero Autónomo</p>', unsafe_allow_html=True)

# Fila de Indicadores Clave de Rendimiento (KPIs)
total_leads = len(df_filtrado)
alertas_criticas = len(df_filtrado[df_filtrado['ESTADO'] == 'Anulado'])

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
with col_kpi1:
    st.markdown(f'<div class="metric-card"><h4>Muestra en Pantalla</h4><h2>{total_leads} Leads</h2></div>', unsafe_allow_html=True)
with col_kpi2:
    st.markdown(f'<div class="metric-card" style="border-left-color: #ef4444;"><h4>Alertas del Agente</h4><h2>{alertas_criticas} Casos Riesgo</h2></div>', unsafe_allow_html=True)
with col_kpi3:
    st.markdown(f'<div class="metric-card" style="border-left-color: #10b981;"><h4>Estado Core IA</h4><h2>Activo (Local)</h2></div>', unsafe_allow_html=True)

st.markdown("---")

# Visualización del Pipeline en el CRM
st.subheader("📊 Distribución Analítica de las Cuentas")
fig_pipeline = px.histogram(
    df_filtrado, x="ESTADO", color="RIESGO_IA",
    template="plotly_white", barmode="stack",
    color_discrete_map={'🚨 CRÍTICO': '#ef4444', '⚠️ MODERADO': '#f59e0b', '✅ ESTABLE': '#10b981'}
)
fig_pipeline.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0))
st.plotly_chart(fig_pipeline, use_container_width=True)

# Tabla de Datos Corporativos Dinámica
st.subheader("📋 Consola de Gestión de Clientes B2B")
columnas_visibles = ['ID', 'NOMBRE_CLIENTE', 'ESTADO', 'SERVICIO', 'CONTRATO', 'RIESGO_IA', 'RECOMENDACION_AGENTE']
st.dataframe(df_filtrado[columnas_visibles], use_container_width=True, hide_index=True)

# Botón de Descarga Inmediata para el Equipo de Retención
csv_data = df_filtrado[columnas_visibles].to_csv(index=False).encode('utf-8')
st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 Descargar Reporte Comercial",
    data=csv_data,
    file_name="crm_reporte_somostelser.csv",
    mime="text/csv"
)
