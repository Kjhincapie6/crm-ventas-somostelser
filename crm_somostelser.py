"""
SaaS Somostelser S.A.S. — Versión Optimizada
Distribuidor Autorizado Tigo Business

Mejoras aplicadas:
- Arquitectura de datos centralizada (cargar/guardar/buscar)
- ID_VENTA generado por max()+1 (nunca len+1)
- Validaciones robustas (sin IndexError, KeyError, FileNotFoundError)
- Session State correcto
- Dashboard completo con todos los KPIs
- Gráficas completas: estado, portafolio, asesor, mes
- Login con roles (admin / asesor)
- Alertas Telegram
- Descarga de reportes
- Preparado para migración SQL
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import requests as req
import io

# ─────────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SaaS Somostelser – Tigo Business",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────
# ESTILOS
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Fondo sidebar oscuro */
[data-testid="stSidebar"] { background-color: #0f172a; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
/* Cabecera */
.crm-header {
    background: linear-gradient(90deg, #0ea5e9 0%, #0369a1 100%);
    padding: 18px 24px; border-radius: 10px; margin-bottom: 18px;
    color: white; font-family: 'Segoe UI', sans-serif;
}
.crm-header h1 { margin: 0; font-size: 26px; font-weight: 700; }
.crm-header p  { margin: 4px 0 0 0; font-size: 13px; opacity: 0.85; }
/* Tarjetas KPI */
.kpi-card {
    background: #f8fafc; border-left: 5px solid #0ea5e9;
    border-radius: 8px; padding: 14px 18px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07); text-align: center;
}
.kpi-card.red  { border-left-color: #ef4444; }
.kpi-card.green{ border-left-color: #10b981; }
.kpi-card.orange{ border-left-color: #f59e0b; }
.kpi-card.purple{ border-left-color: #8b5cf6; }
.kpi-num { font-size: 28px; font-weight: 800; color: #1e293b; }
.kpi-lbl { font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: 600; }
/* Mensajes */
.alert-box {
    background: #fef3c7; border: 1px solid #f59e0b;
    border-radius: 8px; padding: 10px 14px; margin: 8px 0;
    font-size: 13px; color: #92400e;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# CONSTANTES DE NEGOCIO
# ─────────────────────────────────────────────────────────────────
CSV_PATH = "crm_sistema_maestro.csv"

COLUMNAS_REQUERIDAS = [
    "ID_VENTA", "ESTADO", "PORTAFOLIO", "SERVICIO",
    "ASESOR", "FECHA_REGISTRO", "NIT", "CLIENTE",
    "TEL_CONTACTO", "EMAIL_CLIENTE"
]

ESTADOS = [
    "Ingresada",
    "En proceso de firma",
    "Ingreso de pedido",
    "Enviado",
    "Instalacion y aprovisionamiento",
    "Instalado",
    "Pendiente activación",
    "Activado",
    "Devuelto",
    "Anulado",
]

PORTAFOLIOS = ["FIJO", "MOVIL"]
SERVICIOS   = ["BASICO", "AVANZADO"]

# Usuarios con roles (admin y asesores)
USUARIOS = {
    "admin": {
        "password": "admin2024",
        "rol": "admin",
        "nombre": "Administrador",
    },
    "kely.hincapie.distribuidor@asesorespymestigo.com": {
        "password": "tigo2024",
        "rol": "asesor",
        "nombre": "Kely Hincapié",
    },
}

# Telegram (ajustar con credenciales reales)
TELEGRAM_TOKEN   = ""   # ← colocar token real
TELEGRAM_CHAT_ID = ""   # ← colocar chat_id real

# ─────────────────────────────────────────────────────────────────
# CAPA DE DATOS — todas las operaciones CSV centralizadas aquí
# (Reemplazar solo este bloque al migrar a SQL)
# ─────────────────────────────────────────────────────────────────

def cargar_datos() -> pd.DataFrame:
    """Carga el CSV maestro. Devuelve DataFrame vacío si no existe."""
    try:
        df = pd.read_csv(CSV_PATH, dtype={"ID_VENTA": int, "NIT": str, "TEL_CONTACTO": str})
        # Garantizar columnas mínimas
        for col in COLUMNAS_REQUERIDAS:
            if col not in df.columns:
                df[col] = ""
        df["ID_VENTA"] = pd.to_numeric(df["ID_VENTA"], errors="coerce").fillna(0).astype(int)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=COLUMNAS_REQUERIDAS)
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        return pd.DataFrame(columns=COLUMNAS_REQUERIDAS)


def guardar_datos(df: pd.DataFrame) -> bool:
    """Guarda el DataFrame en el CSV maestro. Devuelve True si éxito."""
    try:
        df.to_csv(CSV_PATH, index=False)
        return True
    except Exception as e:
        st.error(f"❌ Error al guardar datos: {e}")
        return False


def crear_venta(registro: dict) -> tuple[bool, str]:
    """Agrega una nueva venta. Genera ID_VENTA seguro por max+1."""
    try:
        df = cargar_datos()
        if len(df) == 0 or df["ID_VENTA"].max() == 0:
            nuevo_id = 1
        else:
            nuevo_id = int(df["ID_VENTA"].max()) + 1

        registro["ID_VENTA"] = nuevo_id
        registro["FECHA_REGISTRO"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        nueva_fila = pd.DataFrame([registro])
        df = pd.concat([df, nueva_fila], ignore_index=True)

        if guardar_datos(df):
            return True, str(nuevo_id)
        return False, "No se pudo guardar"
    except Exception as e:
        return False, str(e)


def actualizar_venta(id_venta: int, campo: str, valor) -> bool:
    """Actualiza un campo de una venta existente por ID_VENTA."""
    try:
        df = cargar_datos()
        mask = df["ID_VENTA"] == id_venta
        if mask.sum() == 0:
            st.warning(f"⚠️ No se encontró la venta con ID {id_venta}.")
            return False
        df.loc[mask, campo] = valor
        return guardar_datos(df)
    except Exception as e:
        st.error(f"❌ Error al actualizar: {e}")
        return False


def buscar_venta(id_venta: int) -> pd.Series | None:
    """Busca y devuelve una venta por ID_VENTA. None si no existe."""
    try:
        df = cargar_datos()
        result = df[df["ID_VENTA"] == id_venta]
        if result.empty:
            return None
        return result.iloc[0]
    except Exception:
        return None


def obtener_opciones_ventas(df: pd.DataFrame) -> list:
    """Genera lista de opciones para SelectBox usando ID real + nombre cliente."""
    if df.empty:
        return []
    opciones = []
    for _, row in df.iterrows():
        try:
            opciones.append(f"{int(row['ID_VENTA'])} — {row['CLIENTE']}")
        except Exception:
            pass
    return opciones


def extraer_id_de_opcion(opcion: str) -> int | None:
    """Extrae el ID_VENTA de una opción del SelectBox. Soporta IDs de cualquier longitud."""
    try:
        parte_id = opcion.split("—")[0].strip()
        return int(parte_id)
    except Exception:
        return None

# ─────────────────────────────────────────────────────────────────
# TELEGRAM
# ─────────────────────────────────────────────────────────────────

def enviar_telegram(mensaje: str):
    """Envía alerta por Telegram. Silencia errores si no está configurado."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        req.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "HTML"}, timeout=5)
    except Exception:
        pass  # Telegram es opcional; nunca detener el CRM por esto

# ─────────────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────────────

def pantalla_login():
    st.markdown("""
    <div class='crm-header'>
      <h1>📡 CRM Somostelser — Tigo Business</h1>
      <p>Sistema de Gestión Comercial B2B</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Iniciar Sesión")
        usuario = st.text_input("Usuario / Correo", key="login_usuario")
        contrasena = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Ingresar", type="primary", use_container_width=True):
            if usuario in USUARIOS and USUARIOS[usuario]["password"] == contrasena:
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = usuario
                st.session_state["rol"] = USUARIOS[usuario]["rol"]
                st.session_state["nombre"] = USUARIOS[usuario]["nombre"]
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos.")


def verificar_autenticacion():
    if not st.session_state.get("autenticado"):
        pantalla_login()
        st.stop()

# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────

def renderizar_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align:center; padding:16px 0 8px 0;'>
          <div style='font-size:36px;'>📡</div>
          <div style='font-size:18px; font-weight:700; color:#38bdf8;'>CRM Somostelser</div>
          <div style='font-size:12px; color:#94a3b8; margin-top:4px;'>Tigo Business B2B</div>
        </div>
        <hr style='border-color:#1e3a5f; margin:8px 0;'>
        """, unsafe_allow_html=True)

        st.markdown(f"👤 **{st.session_state.get('nombre', '')}**  \n🔑 Rol: `{st.session_state.get('rol', '')}`")
        st.markdown("<hr style='border-color:#1e3a5f; margin:8px 0;'>", unsafe_allow_html=True)

        pestanas = [
            "📊 Dashboard",
            "➕ Registrar Venta",
            "📋 Base de Datos",
            "🔄 Actualizar Estado",
            "📥 Exportar Reportes",
        ]
        if st.session_state.get("rol") == "admin":
            pestanas.append("⚙️ Configuración")

        opcion = st.radio("Navegación", pestanas, key="nav_radio")

        st.markdown("<hr style='border-color:#1e3a5f; margin:12px 0;'>", unsafe_allow_html=True)
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    return opcion

# ─────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────

def kpi(label: str, valor, color: str = ""):
    return f"<div class='kpi-card {color}'><div class='kpi-num'>{valor}</div><div class='kpi-lbl'>{label}</div></div>"


def tab_dashboard(df: pd.DataFrame):
    st.markdown("<div class='crm-header'><h1>📊 Dashboard Ejecutivo</h1><p>Vista general del pipeline comercial</p></div>", unsafe_allow_html=True)

    if df.empty:
        st.info("📭 No hay datos registrados aún.")
        return

    # ── KPIs principales ──
    total        = len(df)
    instalados   = len(df[df["ESTADO"] == "Instalado"])
    activados    = len(df[df["ESTADO"] == "Activado"])
    anulados     = len(df[df["ESTADO"] == "Anulado"])
    pendientes   = len(df[df["ESTADO"] == "Pendiente activación"])
    en_gestion   = len(df[~df["ESTADO"].isin(["Instalado", "Activado", "Anulado"])])
    fijo_count   = len(df[df["PORTAFOLIO"] == "FIJO"])
    movil_count  = len(df[df["PORTAFOLIO"] == "MOVIL"])
    avanzado_c   = len(df[df["SERVICIO"] == "AVANZADO"])

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi("Total Ventas", total), unsafe_allow_html=True)
    with c2: st.markdown(kpi("Instaladas", instalados, "green"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Activadas", activados, "purple"), unsafe_allow_html=True)
    with c4: st.markdown(kpi("Anuladas", anulados, "red"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c5, c6, c7, c8 = st.columns(4)
    with c5: st.markdown(kpi("En Gestión", en_gestion, "orange"), unsafe_allow_html=True)
    with c6: st.markdown(kpi("Pendiente Act.", pendientes), unsafe_allow_html=True)
    with c7: st.markdown(kpi("Portafolio Fijo", fijo_count, "green"), unsafe_allow_html=True)
    with c8: st.markdown(kpi("Portafolio Móvil", movil_count, "purple"), unsafe_allow_html=True)

    st.markdown("---")

    # ── Gráficas ──
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📈 Ventas por Estado")
        conteo_estado = df["ESTADO"].value_counts().reset_index()
        conteo_estado.columns = ["Estado", "Cantidad"]
        fig1 = px.bar(conteo_estado, x="Estado", y="Cantidad", color="Estado",
                      template="plotly_white", color_discrete_sequence=px.colors.qualitative.Bold)
        fig1.update_layout(height=320, showlegend=False, margin=dict(l=0, r=0, t=20, b=80))
        fig1.update_xaxes(tickangle=30)
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.subheader("📊 Activadas vs Anuladas")
        datos_av = pd.DataFrame({
            "Estado": ["Activadas", "Anuladas", "Instaladas"],
            "Cantidad": [activados, anulados, instalados]
        })
        fig2 = px.pie(datos_av, names="Estado", values="Cantidad",
                      color_discrete_map={"Activadas": "#10b981", "Anuladas": "#ef4444", "Instaladas": "#0ea5e9"},
                      template="plotly_white")
        fig2.update_layout(height=320, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig2, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("🗂️ Fijo vs Móvil")
        datos_pf = pd.DataFrame({
            "Portafolio": ["FIJO", "MOVIL"],
            "Cantidad": [fijo_count, movil_count]
        })
        fig3 = px.bar(datos_pf, x="Portafolio", y="Cantidad", color="Portafolio",
                      color_discrete_map={"FIJO": "#0ea5e9", "MOVIL": "#8b5cf6"},
                      template="plotly_white")
        fig3.update_layout(height=280, showlegend=False, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        st.subheader("🏷️ Básico vs Avanzado")
        datos_sv = df["SERVICIO"].value_counts().reset_index()
        datos_sv.columns = ["Servicio", "Cantidad"]
        fig4 = px.pie(datos_sv, names="Servicio", values="Cantidad",
                      color_discrete_sequence=["#f59e0b", "#0ea5e9"],
                      template="plotly_white")
        fig4.update_layout(height=280, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig4, use_container_width=True)

    # ── Ventas por Asesor ──
    st.subheader("👤 Ventas por Asesor")
    por_asesor = df.groupby("ASESOR")["ID_VENTA"].count().reset_index()
    por_asesor.columns = ["Asesor", "Ventas"]
    por_asesor["Asesor_corto"] = por_asesor["Asesor"].apply(
        lambda x: x.split("@")[0] if "@" in str(x) else str(x)
    )
    fig5 = px.bar(por_asesor, x="Asesor_corto", y="Ventas",
                  color="Ventas", template="plotly_white",
                  color_continuous_scale="Blues")
    fig5.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig5, use_container_width=True)

    # ── Ventas Mensuales ──
    st.subheader("📅 Ventas Mensuales")
    try:
        df_tiempo = df.copy()
        df_tiempo["FECHA_REGISTRO"] = pd.to_datetime(df_tiempo["FECHA_REGISTRO"], errors="coerce")
        df_tiempo = df_tiempo.dropna(subset=["FECHA_REGISTRO"])
        df_tiempo["MES"] = df_tiempo["FECHA_REGISTRO"].dt.to_period("M").astype(str)
        por_mes = df_tiempo.groupby("MES")["ID_VENTA"].count().reset_index()
        por_mes.columns = ["Mes", "Ventas"]
        fig6 = px.line(por_mes, x="Mes", y="Ventas", markers=True,
                       template="plotly_white", color_discrete_sequence=["#0ea5e9"])
        fig6.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=60))
        fig6.update_xaxes(tickangle=30)
        st.plotly_chart(fig6, use_container_width=True)
    except Exception as e:
        st.warning(f"No se pudo generar la gráfica mensual: {e}")

# ─────────────────────────────────────────────────────────────────
# REGISTRAR VENTA
# ─────────────────────────────────────────────────────────────────

def tab_registrar_venta():
    st.markdown("<div class='crm-header'><h1>➕ Registrar Nueva Venta</h1><p>Complete todos los campos del formulario</p></div>", unsafe_allow_html=True)

    with st.form("form_nueva_venta", clear_on_submit=True):
        st.markdown("#### 📋 Datos del Cliente")
        c1, c2 = st.columns(2)
        with c1:
            nit = st.text_input("NIT / Documento *", key="nv_nit")
            cliente = st.text_input("Nombre del Cliente *", key="nv_cliente")
        with c2:
            tel = st.text_input("Teléfono de Contacto *", key="nv_tel")
            email = st.text_input("Email del Cliente *", key="nv_email")

        st.markdown("#### 📦 Información Comercial")
        c3, c4, c5 = st.columns(3)
        with c3:
            portafolio = st.selectbox("Portafolio *", PORTAFOLIOS, key="nv_portafolio")
        with c4:
            servicio = st.selectbox("Servicio *", SERVICIOS, key="nv_servicio")
        with c5:
            estado = st.selectbox("Estado Inicial *", ESTADOS, key="nv_estado")

        asesor = st.text_input(
            "Asesor *",
            value=st.session_state.get("usuario", ""),
            disabled=(st.session_state.get("rol") != "admin"),
            key="nv_asesor"
        )

        observaciones = st.text_area("Observaciones", key="nv_obs")

        submitted = st.form_submit_button("💾 Registrar Venta", type="primary", use_container_width=True)

    if submitted:
        # Validaciones
        errores = []
        if not nit.strip():       errores.append("NIT / Documento es obligatorio.")
        if not cliente.strip():   errores.append("Nombre del Cliente es obligatorio.")
        if not tel.strip():       errores.append("Teléfono es obligatorio.")
        if not email.strip():     errores.append("Email es obligatorio.")
        if not asesor.strip():    errores.append("Asesor es obligatorio.")

        if errores:
            for err in errores:
                st.error(f"❌ {err}")
            return

        registro = {
            "ESTADO":          estado,
            "PORTAFOLIO":      portafolio,
            "SERVICIO":        servicio,
            "ASESOR":          asesor.strip(),
            "NIT":             nit.strip(),
            "CLIENTE":         cliente.strip(),
            "TEL_CONTACTO":    tel.strip(),
            "EMAIL_CLIENTE":   email.strip(),
        }

        ok, resultado = crear_venta(registro)
        if ok:
            st.success(f"✅ Venta registrada exitosamente. **ID_VENTA: {resultado}**")
            msg_tg = (
                f"🆕 <b>Nueva Venta Registrada</b>\n"
                f"📋 ID: {resultado}\n"
                f"👤 Cliente: {cliente.strip()}\n"
                f"📦 Portafolio: {portafolio} | Servicio: {servicio}\n"
                f"📍 Estado: {estado}\n"
                f"🧑 Asesor: {asesor.strip()}\n"
                f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            )
            enviar_telegram(msg_tg)
        else:
            st.error(f"❌ Error al registrar la venta: {resultado}")

# ─────────────────────────────────────────────────────────────────
# BASE DE DATOS
# ─────────────────────────────────────────────────────────────────

def tab_base_datos(df: pd.DataFrame):
    st.markdown("<div class='crm-header'><h1>📋 Base de Datos</h1><p>Consulta, búsqueda y filtros del pipeline</p></div>", unsafe_allow_html=True)

    if df.empty:
        st.info("📭 No hay datos registrados aún.")
        return

    # Filtros
    with st.expander("🔍 Filtros de Búsqueda", expanded=True):
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            f_cliente = st.text_input("Buscar Cliente", key="db_cliente")
        with fc2:
            f_estado = st.selectbox("Estado", ["TODOS"] + ESTADOS, key="db_estado")
        with fc3:
            f_portafolio = st.selectbox("Portafolio", ["TODOS"] + PORTAFOLIOS, key="db_portafolio")
        with fc4:
            f_servicio = st.selectbox("Servicio", ["TODOS"] + SERVICIOS, key="db_servicio")

    df_filtrado = df.copy()
    if f_cliente:
        df_filtrado = df_filtrado[
            df_filtrado["CLIENTE"].str.contains(f_cliente, case=False, na=False) |
            df_filtrado["NIT"].astype(str).str.contains(f_cliente, case=False, na=False)
        ]
    if f_estado != "TODOS":
        df_filtrado = df_filtrado[df_filtrado["ESTADO"] == f_estado]
    if f_portafolio != "TODOS":
        df_filtrado = df_filtrado[df_filtrado["PORTAFOLIO"] == f_portafolio]
    if f_servicio != "TODOS":
        df_filtrado = df_filtrado[df_filtrado["SERVICIO"] == f_servicio]

    st.markdown(f"**{len(df_filtrado)} registros encontrados**")
    st.dataframe(
        df_filtrado.sort_values("ID_VENTA", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID_VENTA":     st.column_config.NumberColumn("ID Venta", width="small"),
            "FECHA_REGISTRO": st.column_config.TextColumn("Fecha Registro", width="medium"),
            "CLIENTE":      st.column_config.TextColumn("Cliente", width="large"),
            "ESTADO":       st.column_config.TextColumn("Estado", width="medium"),
            "PORTAFOLIO":   st.column_config.TextColumn("Portafolio", width="small"),
            "SERVICIO":     st.column_config.TextColumn("Servicio", width="small"),
        }
    )

# ─────────────────────────────────────────────────────────────────
# ACTUALIZAR ESTADO
# ─────────────────────────────────────────────────────────────────

def tab_actualizar_estado(df: pd.DataFrame):
    st.markdown("<div class='crm-header'><h1>🔄 Actualizar Estado de Venta</h1><p>Cambia el estado del pipeline para una venta específica</p></div>", unsafe_allow_html=True)

    if df.empty:
        st.info("📭 No hay ventas registradas aún.")
        return

    opciones = obtener_opciones_ventas(df)
    if not opciones:
        st.warning("⚠️ No hay ventas disponibles para actualizar.")
        return

    # Filtro previo opcional
    f_buscar = st.text_input("🔍 Buscar venta por nombre o ID:", key="act_buscar")
    opciones_filtradas = opciones
    if f_buscar.strip():
        opciones_filtradas = [o for o in opciones if f_buscar.lower() in o.lower()]

    if not opciones_filtradas:
        st.warning("No se encontraron ventas con ese criterio.")
        return

    seleccion = st.selectbox("Seleccionar Venta", opciones_filtradas, key="act_select")
    id_venta = extraer_id_de_opcion(seleccion)

    if id_venta is None:
        st.error("❌ No se pudo identificar el ID de la venta seleccionada.")
        return

    venta = buscar_venta(id_venta)
    if venta is None:
        st.error(f"❌ No se encontró la venta con ID {id_venta}.")
        return

    # Mostrar datos actuales
    with st.expander("📄 Datos actuales de la venta", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**ID_VENTA:** {id_venta}")
            st.markdown(f"**Cliente:** {venta.get('CLIENTE', 'N/A')}")
            st.markdown(f"**NIT:** {venta.get('NIT', 'N/A')}")
        with c2:
            st.markdown(f"**Estado actual:** `{venta.get('ESTADO', 'N/A')}`")
            st.markdown(f"**Portafolio:** {venta.get('PORTAFOLIO', 'N/A')}")
            st.markdown(f"**Servicio:** {venta.get('SERVICIO', 'N/A')}")
        with c3:
            st.markdown(f"**Asesor:** {venta.get('ASESOR', 'N/A')}")
            st.markdown(f"**Teléfono:** {venta.get('TEL_CONTACTO', 'N/A')}")
            st.markdown(f"**Email:** {venta.get('EMAIL_CLIENTE', 'N/A')}")

    estado_actual = venta.get("ESTADO", ESTADOS[0])
    idx_actual = ESTADOS.index(estado_actual) if estado_actual in ESTADOS else 0

    nuevo_estado = st.selectbox(
        "Nuevo Estado",
        ESTADOS,
        index=idx_actual,
        key="act_nuevo_estado"
    )

    observacion = st.text_area("Observación del cambio (opcional)", key="act_obs")

    if st.button("✅ Confirmar Actualización", type="primary"):
        if nuevo_estado == estado_actual:
            st.info("ℹ️ El estado seleccionado es el mismo que el actual. No se realizó ningún cambio.")
            return

        ok = actualizar_venta(id_venta, "ESTADO", nuevo_estado)
        if ok:
            st.success(f"✅ Estado actualizado a **{nuevo_estado}** para la venta ID {id_venta}.")
            msg_tg = (
                f"🔄 <b>Cambio de Estado</b>\n"
                f"📋 ID: {id_venta} | Cliente: {venta.get('CLIENTE', 'N/A')}\n"
                f"📍 {estado_actual} → {nuevo_estado}\n"
                f"💬 {observacion or 'Sin observación'}\n"
                f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            )
            enviar_telegram(msg_tg)
        else:
            st.error("❌ No se pudo actualizar el estado.")

# ─────────────────────────────────────────────────────────────────
# EXPORTAR REPORTES
# ─────────────────────────────────────────────────────────────────

def tab_exportar(df: pd.DataFrame):
    st.markdown("<div class='crm-header'><h1>📥 Exportar Reportes</h1><p>Descarga la base de datos y reportes filtrados</p></div>", unsafe_allow_html=True)

    if df.empty:
        st.info("📭 No hay datos para exportar.")
        return

    st.subheader("📊 Reporte Completo")
    csv_completo = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Descargar Base Completa (CSV)",
        data=csv_completo,
        file_name=f"crm_somostelser_completo_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.markdown("---")
    st.subheader("🎯 Reporte Filtrado por Estado")
    estado_export = st.selectbox("Seleccionar Estado", ["TODOS"] + ESTADOS, key="exp_estado")

    df_exp = df.copy()
    if estado_export != "TODOS":
        df_exp = df_exp[df_exp["ESTADO"] == estado_export]

    st.markdown(f"**{len(df_exp)} registros**")
    st.dataframe(df_exp, use_container_width=True, hide_index=True)

    csv_filtrado = df_exp.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"⬇️ Descargar Reporte — {estado_export}",
        data=csv_filtrado,
        file_name=f"crm_reporte_{estado_export.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.markdown("---")
    st.subheader("🚨 Reporte de Anulados / Retención")
    df_anulados = df[df["ESTADO"] == "Anulado"].copy()
    df_anulados["NIVEL_RIESGO"] = df_anulados["SERVICIO"].apply(
        lambda s: "🚨 CRÍTICO" if str(s).upper() == "AVANZADO" else "⚠️ MODERADO"
    )
    df_anulados["ACCION_SUGERIDA"] = df_anulados["SERVICIO"].apply(
        lambda s: "Downgrade a BÁSICO con 25% de descuento" if str(s).upper() == "AVANZADO"
        else "Plan Retención Pyme — 15% de descuento o congelamiento 90 días"
    )
    st.dataframe(df_anulados, use_container_width=True, hide_index=True)
    csv_ren = df_anulados.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Descargar Reporte de Retención",
        data=csv_ren,
        file_name=f"crm_retencion_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# ─────────────────────────────────────────────────────────────────
# CONFIGURACIÓN (solo admin)
# ─────────────────────────────────────────────────────────────────

def tab_configuracion():
    st.markdown("<div class='crm-header'><h1>⚙️ Configuración</h1><p>Gestión de usuarios y sistema (solo administrador)</p></div>", unsafe_allow_html=True)

    if st.session_state.get("rol") != "admin":
        st.error("❌ Acceso denegado. Solo el administrador puede acceder a esta sección.")
        return

    st.subheader("👥 Usuarios Activos")
    for usr, datos in USUARIOS.items():
        st.markdown(f"- **{datos['nombre']}** — `{usr}` — Rol: `{datos['rol']}`")

    st.markdown("---")
    st.subheader("📡 Configuración Telegram")
    st.info("Para activar las alertas de Telegram, edita las variables `TELEGRAM_TOKEN` y `TELEGRAM_CHAT_ID` en la cabecera del archivo `crm_somostelser.py`.")

    st.markdown("---")
    st.subheader("🗄️ Información del Sistema")
    df = cargar_datos()
    st.markdown(f"""
    - **Archivo de datos:** `{CSV_PATH}`
    - **Total de registros:** {len(df)}
    - **Último ID_VENTA:** {df['ID_VENTA'].max() if not df.empty else 'N/A'}
    - **Próximo ID_VENTA:** {int(df['ID_VENTA'].max()) + 1 if not df.empty else 1}
    """)

    st.markdown("---")
    st.subheader("🔁 Preparación para Migración SQL")
    st.info("""
    La arquitectura actual centraliza todas las operaciones de datos en las funciones:
    `cargar_datos()`, `guardar_datos()`, `crear_venta()`, `actualizar_venta()`, `buscar_venta()`.
    
    Para migrar a SQLite / PostgreSQL / MySQL, solo se reemplaza el cuerpo de estas funciones
    sin modificar ninguna pantalla, formulario, dashboard ni lógica de negocio.
    """)

# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def main():
    # Inicializar session state
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    verificar_autenticacion()

    opcion = renderizar_sidebar()

    # Cargar datos una sola vez por sesión/interacción
    df = cargar_datos()

    # Routing de pestañas
    if opcion == "📊 Dashboard":
        tab_dashboard(df)
    elif opcion == "➕ Registrar Venta":
        tab_registrar_venta()
    elif opcion == "📋 Base de Datos":
        tab_base_datos(df)
    elif opcion == "🔄 Actualizar Estado":
        tab_actualizar_estado(df)
    elif opcion == "📥 Exportar Reportes":
        tab_exportar(df)
    elif opcion == "⚙️ Configuración":
        tab_configuracion()


if __name__ == "__main__":
    main()
