# SaaS SOMOS TELSER — Portal de Ventas
# Versión Optimizada — Diseño 100% fiel al original
# ============================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import os
import requests as req
import random
from zoneinfo import ZoneInfo

# Zona horaria Colombia
TZ = ZoneInfo("America/Bogota")

# ─── CONFIGURACIÓN DE PÁGINA ───────────────────────────────
st.set_page_config(
    page_title="CRM de Ventas B2B con Analítica e Inteligencia Artificial",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── ESTILOS GLOBALES (fiel al original) ───────────────────
st.markdown("""
<style>
/* Ocultar menú hamburguesa y footer de Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Tabs: estilo original con subrayado azul */
div[data-testid="stTabs"] button {
    font-size: 13px !important;
    padding: 6px 14px !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    border-bottom: 2px solid #00aaff !important;
    color: #00aaff !important;
    font-weight: 600 !important;
}

/* Sidebar blanco con borde derecho suave */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e5e7eb;
}
[data-testid="stSidebar"] * { color: #1e293b !important; }

/* Botón principal azul tipo el original */
div.stButton > button[kind="primary"],
div.stButton > button {
    background-color: #00aaff;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    width: 100%;
}
div.stButton > button:hover {
    background-color: #0088cc;
}

/* Botón Cerrar Sesión negro */
button[data-testid="cerrar_sesion"] {
    background-color: #000000 !important;
}

/* Input fields */
input, textarea, select { border-radius: 4px !important; }

/* Título principal */
h1.portal-title {
    font-size: 28px;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 2px;
}

/* Separador sidebar */
hr.sidebar-sep {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# ─── DATOS GEOGRÁFICOS ─────────────────────────────────────
DEPARTAMENTOS_MUNICIPIOS = {
    "Antioquia": ["Medellín","Bello","Itagüí","Envigado","Sabaneta","La Estrella","Caldas","Copacabana","Girardota","Barbosa","Rionegro","Guarne","Marinilla","El Carmen de Viboral","La Ceja","La Unión","El Retiro","El Santuario","Caucasia","Turbo","Apartadó","Carepa","Chigorodó"],
    "Bogotá D.C.": ["Bogotá"],
    "Valle del Cauca": ["Cali","Buenaventura","Palmira","Tuluá","Buga","Jamundí","Cartago","Yumbo","Roldanillo"],
    "Atlántico": ["Barranquilla","Soledad","Malambo","Galapa","Puerto Colombia"],
    "Bolívar": ["Cartagena","Turbaco","Magangué","El Carmen de Bolívar"],
    "Cundinamarca": ["Soacha","Facatativá","Zipaquirá","Chía","Cajicá","Mosquera","Funza","Fusagasugá"],
    "Santander": ["Bucaramanga","Floridablanca","Girón","Piedecuesta","Barrancabermeja","San Gil"],
    "Norte de Santander": ["Cúcuta","Los Patios","Villa del Rosario","Ocaña"],
    "Risaralda": ["Pereira","Dosquebradas","La Virginia","Santa Rosa de Cabal"],
    "Caldas": ["Manizales","Villamaría","Chinchiná","Riosucio"],
    "Quindío": ["Armenia","Calarcá","Circasia","Montenegro"],
    "Boyacá": ["Tunja","Duitama","Sogamoso","Chiquinquirá"],
    "Córdoba": ["Montería","Cereté","Lorica","Sahagún"],
    "Sucre": ["Sincelejo","Corozal","Sampués"],
    "Cesar": ["Valledupar","Aguachica","Codazzi"],
    "Magdalena": ["Santa Marta","Ciénaga","Fundación"],
    "Meta": ["Villavicencio","Acacías","Granada"],
    "Cauca": ["Popayán","Santander de Quilichao","Puerto Tejada"],
    "Nariño": ["Pasto","Tumaco","Ipiales"],
    "Huila": ["Neiva","Pitalito","Garzón"],
    "Tolima": ["Ibagué","Espinal","Melgar","Honda"],
}

# ─── PLANES TIGO BUSINESS ──────────────────────────────────
# Fuente: Ayuda Venta Tigo Junio 2026
 
# Precios base por plan (1 línea, sin descuento)
PLANES_MOVIL = {
    "Negocios 5.0": {
        "Pospago Fidelización Negocios 4.9 Plus+ — 60GB": 44900,
        "Pospago Negocios 5.4 Plus+ — 100GB":             53900,
        "Pospago 5.3 Empresarial — Ilimitado":           113900,
    },
    "Empresarial 6.0": {
        "Plan Datos Tigo Empresarial 6.9 — 30GB":         38300,
        "Plan Datos Tigo Empresarial 6.10 — 60GB":        47900,
        "Plan Datos Tigo Empresarial 6.11 — 110GB":       57900,
        "Plan Datos Tigo Empresarial 6.12 — Ilimitado":  113900,
        "Plan Datos Tigo Empresarial 6.7 Full Equipo — Ilimitado": 89900,
        "Plan Datos Tigo Empresarial 6.8 Full Tigo — Ilimitado":   54900,
    }
}
 
# Tabla de descuentos exactos por volumen según ayuda venta
# Negocios 5.0: 1L=0%, 2L=10%, 3-5L=20%, 6-8L=25%, 9+L=30%
# Empresarial 6.0: 1-2L=0%, 3-5L=13%, 6-9L=25%, 10+L=30%
# Ambas: 50% de descuento en el primer mes por portación
 
# Precios por número de líneas para Negocios 5.0 (por línea)
PRECIOS_5_POR_LINEA = {
    "Pospago Fidelización Negocios 4.9 Plus+ — 60GB": {
        1: 44900, 2: 40410, "3-5": 35920, "6-8": 33675, "9+": 31430
    },
    "Pospago Negocios 5.4 Plus+ — 100GB": {
        1: 53900, 2: 48510, "3-5": 43120, "6-8": 40425, "9+": 37730
    },
    "Pospago 5.3 Empresarial — Ilimitado": {
        1: 113900, 2: 102510, "3-5": 91120, "6-8": 85425, "9+": 79730
    },
}
 
# Precios por número de líneas para Empresarial 6.0 (por línea)
PRECIOS_6_POR_LINEA = {
    "Plan Datos Tigo Empresarial 6.9 — 30GB": {
        1: 38300, "3-5": 33321, "6-9": 28725, "10+": 26810
    },
    "Plan Datos Tigo Empresarial 6.10 — 60GB": {
        1: 47900, "3-5": 41673, "6-9": 35925, "10+": 33530
    },
    "Plan Datos Tigo Empresarial 6.11 — 110GB": {
        1: 57900, "3-5": 50373, "6-9": 43425, "10+": 40530
    },
    "Plan Datos Tigo Empresarial 6.12 — Ilimitado": {
        1: 113900, "3-5": 99093, "6-9": 85425, "10+": 79730
    },
    "Plan Datos Tigo Empresarial 6.7 Full Equipo — Ilimitado": {
        1: 89900, "3-5": 89900, "6-9": 89900, "10+": 89900
    },
    "Plan Datos Tigo Empresarial 6.8 Full Tigo — Ilimitado": {
        1: 54900, "3-5": 54900, "6-9": 54900, "10+": 54900
    },
}
 
DESCUENTOS_5 = {1: 0.0, 2: 0.10, "3-5": 0.20, "6-8": 0.25, "9+": 0.30}
DESCUENTOS_6 = {1: 0.0, "3-5": 0.13, "6-9": 0.25, "10+": 0.30}

PLANES_FIJO = {
    "Internet Business 300Mbps": 88880,
    "Internet Business 500Mbps": 115000,
    "Internet Business 700Mbps": 180001,
    "Internet Business Seguro 300Mbps": 117880,
    "Internet Business Seguro 500Mbps": 144000,
    "Internet Business Seguro 700Mbps": 209000,
    "Full Tigo Business 500Mbps + Móvil 6.8": 169900,
    "Full Tigo Business 700Mbps + Móvil 6.8": 199900,
    "Full Tigo Business 1000Mbps + Móvil 6.8": 299900,
    "Internet Avanzado GPON 50Mbps": 248740,
    "Internet Avanzado GPON 100Mbps": 298438,
    "Internet Avanzado GPON 200Mbps": 425049,
    "Internet Avanzado GPON 300Mbps": 457638,
    "Internet Avanzado GPON 500Mbps": 518174,
    "Televisión HFC Digital Medellín": 80553,
    "Televisión HFC Digital Barranquilla/Cúcuta": 93665,
    "Telefonía IP Voz Sin Fronteras Plus": 64528,
}

# ─── ESTADOS DEL NEGOCIO ───────────────────────────────────
ESTADOS = [
    "Cotizado",
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

TIPOS_SEGUIMIENTO = ["Llamada", "Visita", "Email", "WhatsApp", "Reunión virtual"]
TIPOS_DOC = ["NIT", "CV", "Pasaporte", "CE" , "PPT"]

# ─── USUARIOS Y ROLES ──────────────────────────────────────
USUARIOS = {
    "admin@somostelser.com": {
        "password": "admin2024",
        "rol": "admin",
        "nombre": "Admin",
        "display": "ADMIN@SOMOSTELSER.COM",
    },
    "kely.hincapie.distribuidor@asesorespymestigo.com": {
        "password": "tigo2024",
        "rol": "asesor",
        "nombre": "Kely Hincapié",
        "display": "kely.hincapie.distribuidor@asesorespymestigo.com",
    },
}

# Telegram
TELEGRAM_TOKEN = "8942591199:AAFi8vkAvNyL4LLkUPO9TXKhC2bjukEDmcg"
TELEGRAM_CHAT_ID = "1415966548"

# CSV
CSV_PATH = "crm_sistema_maestro.csv"
COLUMNAS = ["ID_VENTA","ESTADO","PORTAFOLIO","SERVICIO","ASESOR","FECHA_REGISTRO",
            "NIT","CLIENTE","TEL_CONTACTO","EMAIL_CLIENTE","TIPO_DOC","RAZON_SOCIAL",
            "DIRECCION","BARRIO","DEPARTAMENTO","MUNICIPIO","EMAIL_CONTACTO",
            "NOMBRE_CONTACTO","MOVIL_CONTACTO","NOMBRE_REP","CEDULA_REP",
            "EMAIL_REP","MOVIL_REP","DIVISION","FAMILIA_PLAN","PLAN","LINEAS",
            "VALOR_TOTAL","NOTAS","FECHA_SEGUIMIENTO","TIPO_SEGUIMIENTO"]


# ════════════════════════════════════════════════════════════
# CAPA DE DATOS — Centralizada (preparada para migración SQL)
# ════════════════════════════════════════════════════════════
@st.cache_data
def cargar_datos() -> pd.DataFrame:
    try:
        df = pd.read_csv(CSV_PATH, dtype=str)
        df["ID_VENTA"] = pd.to_numeric(
            df["ID_VENTA"],
            errors="coerce"
        ).fillna(0).astype(int)

        # Asegurar que existan todas las columnas
        for col in COLUMNAS:
            if col not in df.columns:
                df[col] = ""

        return df

    except FileNotFoundError:
        return pd.DataFrame(columns=COLUMNAS)

    except Exception as e:
        st.error(f"❌ Error cargando datos: {e}")
        return pd.DataFrame(columns=COLUMNAS)


def guardar_datos(df: pd.DataFrame) -> bool:
    try:
        df.to_csv(CSV_PATH, index=False)
        return True
    except Exception as e:
        st.error(f"❌ Error guardando datos: {e}")
        return False


def crear_venta(registro: dict) -> tuple:
    try:
        df = cargar_datos()
        if df.empty or df["ID_VENTA"].max() == 0:
            nuevo_id = 1
        else:
            nuevo_id = int(df["ID_VENTA"].max()) + 1
        registro["ID_VENTA"] = nuevo_id
        registro["FECHA_REGISTRO"] = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
        nueva = pd.DataFrame([registro])
        df = pd.concat([df, nueva], ignore_index=True)
        if guardar_datos(df):
            return True, str(nuevo_id)
        return False, "No se pudo guardar"
    except Exception as e:
        return False, str(e)


def actualizar_venta(id_venta: int, campos: dict) -> bool:
    try:
        df = cargar_datos()
        mask = df["ID_VENTA"] == id_venta
        if mask.sum() == 0:
            return False
        for campo, valor in campos.items():
            df.loc[mask, campo] = valor
        return guardar_datos(df)
    except Exception as e:
        st.error(f"❌ Error actualizando: {e}")
        return False


def buscar_venta(id_venta: int):
    try:
        df = cargar_datos()
        result = df[df["ID_VENTA"] == id_venta]
        if result.empty:
            return None
        return result.iloc[0]
    except Exception:
        return None


def extraer_id_opcion(opcion: str):
    try:
        return int(opcion.split("—")[0].strip())
    except Exception:
        return None


def opciones_ventas(df: pd.DataFrame) -> list:
    if df.empty:
        return []
    items = []
    for _, row in df.iterrows():
        try:
            id_str = str(int(row["ID_VENTA"])).zfill(4)
            cliente = str(row.get("CLIENTE", "")).strip()
            estado  = str(row.get("ESTADO", "")).strip()
            items.append(f"{id_str} — {cliente} | {estado}")
        except Exception:
            pass
    return items

# ─── TELEGRAM ──────────────────────────────────────────────
def enviar_telegram(msg: str):
    """Envía una notificación al chat de Telegram."""
    
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        st.warning("⚠️ Telegram no está configurado.")
        return

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        response = req.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": msg,
                "parse_mode": "HTML",
            },
            timeout=10,
        )

        # Verifica que Telegram respondió correctamente
        response.raise_for_status()

    except req.exceptions.RequestException as e:
        st.error(f"❌ Error enviando notificación a Telegram:\n{e}")

# ─── CÁLCULO DE PRECIO MÓVIL ───────────────────────────────
def calcular_precio_movil(familia: str, plan: str, lineas: int) -> int:
    planes = PLANES_MOVIL.get(familia, {})
    base = planes.get(plan, 0)
    if familia == "Negocios 5.0":
        if lineas == 1:   pct = 0.0
        elif lineas == 2: pct = 0.10
        elif lineas <= 5: pct = 0.20
        elif lineas <= 8: pct = 0.25
        else:             pct = 0.30
    else:
        if lineas == 1:    pct = 0.0
        elif lineas <= 5:  pct = 0.13
        elif lineas <= 9:  pct = 0.25
        else:              pct = 0.30
    return int(base * (1 - pct) * lineas)

# ════════════════════════════════════════════════════════════
# LOGIN
# ════════════════════════════════════════════════════════════

def pantalla_login():
    st.markdown("## 🔒 CRM de Ventas B2B con Analítica e Inteligencia Artificial")
    st.caption("Selecciona tu perfil e ingresa la contraseña:")
    st.markdown("")
    lista_usuarios = list(USUARIOS.keys())
    usuario = st.selectbox("Usuario:", lista_usuarios, key="login_user")
    password = st.text_input("Contraseña:", type="password", key="login_pass")
    if st.button("Ingresar al Portal", key="btn_login"):
        datos = USUARIOS.get(usuario, {})
        if datos.get("password") == password:
            st.session_state["auth"]    = True
            st.session_state["usuario"] = usuario
            st.session_state["rol"]     = datos["rol"]
            st.session_state["nombre"]  = datos["nombre"]
            st.session_state["display"] = datos["display"]
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")


def check_auth():
    if not st.session_state.get("auth"):
        pantalla_login()
        st.stop()

# ════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════

def sidebar_render(df: pd.DataFrame):
    with st.sidebar:

        # Logo
        LOGO_LOCAL = "logo_somostelser.png"
        LOGO_GITHUB = "https://raw.githubusercontent.com/TU_USUARIO/TU_REPOSITORIO/main/imagenes/logo_somostelser.png"

        if os.path.exists(LOGO_LOCAL):
            st.image(LOGO_LOCAL, use_container_width=True)
        else:
            st.image(LOGO_GITHUB, use_container_width=True)

        st.markdown("---")

        # Usuario conectado
        rol_label = "👑 Admin" if st.session_state.get("rol") == "admin" else "👤 Asesor"
        st.markdown(
            f"**{rol_label}:** `{st.session_state.get('display', '')}`"
        )

        st.markdown(
            "<hr style='border-top:1px solid #e2e8f0; margin:10px 0;'>",
            unsafe_allow_html=True
        )

        # =====================================================
        # TAREAS PENDIENTES
        # ====================================================

        st.markdown("### 📅 Agenda de Seguimientos")

        if not df.empty:
            hoy = datetime.now(TZ).date()

            ICONOS_SEG = {
                "Llamada":         "📞",
                "Visita":          "🤝",
                "Email":           "📧",
                "WhatsApp":        "💬",
                "Reunión virtual": "🖥️",
            }

            ESTADOS_ACTIVOS = [
                "Cotizado", "Ingresada", "En proceso de firma",
                "Ingreso de pedido", "Enviado",
                "Instalacion y aprovisionamiento", "Pendiente activación",
            ]

            df_seg = df[
                df["ESTADO"].isin(ESTADOS_ACTIVOS) &
                df["FECHA_SEGUIMIENTO"].notna() &
                (df["FECHA_SEGUIMIENTO"].astype(str).str.strip() != "") &
                (df["FECHA_SEGUIMIENTO"].astype(str).str.lower() != "nan")
            ].copy()

            if not df_seg.empty:
                from datetime import timedelta

                def _parsear(f):
                    try:
                        return datetime.strptime(str(f).strip(), "%Y-%m-%d").date()
                    except Exception:
                        return None

                df_seg["_fecha"] = df_seg["FECHA_SEGUIMIENTO"].apply(_parsear)
                df_seg = df_seg[df_seg["_fecha"].notna()].sort_values("_fecha")

                vencidos = df_seg[df_seg["_fecha"] < hoy]
                hoy_df   = df_seg[df_seg["_fecha"] == hoy]
                proximos = df_seg[
                    (df_seg["_fecha"] > hoy) &
                    (df_seg["_fecha"] <= hoy + timedelta(days=7))
                ]

                # ── Vencidos ─────────────────────────────
                if not vencidos.empty:
                    st.markdown(
                        f"<div style='background:#fee2e2;border-left:4px solid #ef4444;"
                        f"border-radius:6px;padding:7px 10px;margin-bottom:5px;'>"
                        f"<b style='color:#dc2626;font-size:12px;'>⚠️ {len(vencidos)} vencido(s)</b>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    for _, r in vencidos.iterrows():
                        icono   = ICONOS_SEG.get(str(r.get("TIPO_SEGUIMIENTO","")), "📌")
                        cliente = str(r.get("CLIENTE",""))[:20]
                        dias_v  = (hoy - r["_fecha"]).days
                        st.markdown(
                            f"<div style='background:#fef2f2;border-radius:5px;"
                            f"padding:5px 9px;margin:2px 0;font-size:11px;'>"
                            f"{icono} <b>{cliente}</b><br>"
                            f"<span style='color:#ef4444;'>Venció hace {dias_v}d</span> · "
                            f"<span style='color:#64748b;'>{r.get('TIPO_SEGUIMIENTO','')}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

                # ── Hoy ──────────────────────────────────
                if not hoy_df.empty:
                    st.markdown(
                        f"<div style='background:#fef9c3;border-left:4px solid #f59e0b;"
                        f"border-radius:6px;padding:7px 10px;margin:5px 0;'>"
                        f"<b style='color:#b45309;font-size:12px;'>🔔 {len(hoy_df)} HOY</b>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    for _, r in hoy_df.iterrows():
                        icono   = ICONOS_SEG.get(str(r.get("TIPO_SEGUIMIENTO","")), "📌")
                        cliente = str(r.get("CLIENTE",""))[:20]
                        st.markdown(
                            f"<div style='background:#fefce8;border-radius:5px;"
                            f"padding:5px 9px;margin:2px 0;font-size:11px;'>"
                            f"{icono} <b>{cliente}</b><br>"
                            f"<span style='color:#f59e0b;'>📅 Hoy</span> · "
                            f"<span style='color:#64748b;'>{r.get('TIPO_SEGUIMIENTO','')}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

                # ── Próximos 7 días ───────────────────────
                if not proximos.empty:
                    st.markdown(
                        f"<div style='background:#f0fdf4;border-left:4px solid #22c55e;"
                        f"border-radius:6px;padding:7px 10px;margin:5px 0;'>"
                        f"<b style='color:#15803d;font-size:12px;'>✅ {len(proximos)} próximo(s)</b>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    for _, r in proximos.iterrows():
                        icono   = ICONOS_SEG.get(str(r.get("TIPO_SEGUIMIENTO","")), "📌")
                        cliente = str(r.get("CLIENTE",""))[:20]
                        dias_f  = (r["_fecha"] - hoy).days
                        label   = "Mañana" if dias_f == 1 else f"En {dias_f}d"
                        st.markdown(
                            f"<div style='background:#f0fdf4;border-radius:5px;"
                            f"padding:5px 9px;margin:2px 0;font-size:11px;'>"
                            f"{icono} <b>{cliente}</b><br>"
                            f"<span style='color:#22c55e;'>📅 {label} · {r['_fecha'].strftime('%d/%m')}</span> · "
                            f"<span style='color:#64748b;'>{r.get('TIPO_SEGUIMIENTO','')}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

                if vencidos.empty and hoy_df.empty and proximos.empty:
                    st.caption("✅ Sin seguimientos pendientes esta semana.")
            else:
                st.caption("Sin seguimientos activos.")

        st.markdown("---")

    

        # =====================================================
        # ASISTENTE DE OFERTAS
        # =====================================================

        st.markdown("### 🔎 Asistente de Ofertas")
        st.caption("Buscar precio:")

        busqueda = st.text_input(
            "",
            placeholder="Ej: 500Mbps, 6.10, 60GB",
            key="sidebar_busqueda",
            label_visibility="collapsed"
        )

        if busqueda.strip():

            resultados = []
            termino = busqueda.strip().lower()

            # Planes móviles
            for familia, planes in PLANES_MOVIL.items():
                for plan, precio in planes.items():

                    if (
                        termino in str(plan).lower()
                        or termino in str(familia).lower()
                    ):
                        resultados.append(
                            f"📱 {plan}: **${precio:,}**"
                        )

            # Planes fijos
            for plan, precio in PLANES_FIJO.items():

                if termino in str(plan).lower():

                    resultados.append(
                        f"🌐 {plan}: **${precio:,}**"
                    )

            if resultados:
                for r in resultados[:5]:
                    st.markdown(r)
            else:
                st.caption("Sin coincidencias.")

        st.markdown("---")

        # =====================================================
        # BOTÓN CERRAR SESIÓN
        # =====================================================

        if st.button(
            "⚫ Cerrar Sesión",
            key="btn_logout",
            use_container_width=True
        ):
            st.session_state.clear()
            st.rerun()

        st.markdown("---")

        # =====================================================
        # RESUMEN
        # =====================================================
        
        st.markdown("### 📊 Resumen")
        
        if not df.empty:
        
            # KPIs
            total = len(df)
            instalados = len(df[df["ESTADO"] == "Instalado"])
            activados = len(df[df["ESTADO"] == "Activado"])
            anulados = len(df[df["ESTADO"] == "Anulado"])
        
            # Mini gráfico
            resumen = pd.DataFrame({
                "Estado": ["Instalado", "Activado", "Anulado"],
                "Cantidad": [instalados, activados, anulados]
            })
        
            fig = px.bar(
                resumen,
                x="Estado",
                y="Cantidad",
                text="Cantidad",
                color="Estado",
                color_discrete_map={
                    "Instalado": "#00a0e3",
                    "Activado": "#0288d1",
                    "Anulado": "#231f20"
                },
                template="plotly_white"
            )
        
            fig.update_layout(
                height=220,
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False,
                xaxis_title="",
                yaxis_title="",
                plot_bgcolor="white",
                paper_bgcolor="white",
                font=dict(size=11)
            )
        
            fig.update_traces(
                textposition="outside",
                marker_line_width=0
            )
        
            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )
        
            # Indicadores rápidos
            st.caption(
                f"📋 Total: **{total}** | "
                f"🟢 Instalados: **{instalados}** | "
                f"⚡ Activados: **{activados}** | "
                f"❌ Anulados: **{anulados}**"
            )
        
            st.markdown("---")
        
            csv_export = df.to_csv(index=False).encode("utf-8")
        
            st.download_button(
                "📤 Exportar CRM",
                data=csv_export,
                file_name=f"crm_somostelser_{datetime.now(TZ).strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="btn_export_sidebar",
                use_container_width=True
            )
# ════════════════════════════════════════════════════════════
# LIMPIAR FORMULARIO
# ════════════════════════════════════════════════════════════

def limpiar_formulario():

    keys = [
        "reg_division",
        "reg_tipo_doc",
        "reg_num_doc",
        "reg_razon",
        "reg_dir",
        "reg_barrio",
        "reg_depto",
        "reg_municipio",
        "reg_email_contacto",
        "reg_nombre_contacto",
        "reg_movil_contacto",
        "reg_nombre_rep",
        "reg_cedula_rep",
        "reg_email_rep",
        "reg_movil_rep",
        "reg_estado",
        "reg_notas",
        "reg_fecha_seg",
        "reg_tipo_seg",
        "reg_familia",
        "reg_plan",
        "reg_plan_fijo",
        "reg_lineas",
        "reg_docs",
        "tipo_linea_pop",
        "op_linea_pop",
        "cant_linea_pop",
        "num_linea_pop",
    ]

    for key in keys:
        st.session_state.pop(key, None)

    st.session_state["lista_lineas"] = []

# ════════════════════════════════════════════════════════════
# TAB 1 — REGISTRAR VENTA (COLUMNA DERECHA AJUSTADA)
# ════════════════════════════════════════════════════════════

def tab_registrar_venta():
    if "lista_lineas" not in st.session_state:
        st.session_state.lista_lineas = []

    st.markdown("### Seleccione División:")
    division = st.radio("", ["Móvil", "Fijo"], horizontal=True, key="reg_division", label_visibility="collapsed")
    st.markdown("---")

    col_izq, col_der = st.columns(2)
    
# --- COLUMNA IZQUIERDA: DATOS CLIENTE + GESTIÓN TÉCNICA ---
    with col_izq:
        st.markdown("### 📱 Datos del Cliente")
        tipo_doc = st.selectbox("Tipo Doc:", TIPOS_DOC, key="reg_tipo_doc")
        num_doc   = st.text_input("Número de Documento:", key="reg_num_doc")
        razon     = st.text_input("Razón Social o Nombre:", key="reg_razon")
        direccion = st.text_input("Dirección:", key="reg_dir")
        barrio    = st.text_input("Barrio:", key="reg_barrio")

        deptos = [""] + sorted(DEPARTAMENTOS_MUNICIPIOS.keys())
        depto  = st.selectbox("Departamento:", deptos, key="reg_depto")
        municipios = [""] + DEPARTAMENTOS_MUNICIPIOS.get(depto, []) if depto else [""]
        municipio = st.selectbox("Municipio:", municipios, key="reg_municipio", disabled=(not depto))

        email_contacto  = st.text_input("Email contacto:", key="reg_email_contacto")
        nombre_contacto = st.text_input("Nombre contacto autorizado:", key="reg_nombre_contacto")
        movil_contacto  = st.text_input("Móvil contacto autorizado:", key="reg_movil_contacto")

        st.markdown("---")
        # Gestión Técnica movida a la izquierda
        st.subheader("⚙️ Gestión Técnica")
        with st.popover("📱 Configurar Líneas Móviles / Full Tigo"):
            tipo_linea = st.radio("Tipo de gestión:", ["Portabilidad", "Línea Nueva", "Línea Existente"], key="tipo_linea_pop")
            
            op_linea = "N/A"
            if tipo_linea == "Portabilidad":
                op_linea = st.selectbox("Operador Origen:", ["Claro", "Movistar", "Móvil Éxito", "Wom"], key="op_linea_pop")
            
            cant_linea = st.number_input("Cantidad:", min_value=1, value=1, key="cant_linea_pop")
            num_linea  = st.text_input("Número de línea:", key="num_linea_pop")

            if st.button("➕ Agregar línea", key="btn_add_linea"):
                st.session_state.lista_lineas.append({
                    "cantidad": cant_linea, "tipo": tipo_linea,
                    "operador": op_linea, "numero": num_linea
                })
                st.success(f"✅ Línea {num_linea} agregada.")
                st.rerun()

            if st.session_state.get("lista_lineas"):
                st.markdown("**Líneas acumuladas:**")
                for i, ln in enumerate(st.session_state.lista_lineas, start=1):
                    st.write(f"{i}. {ln['tipo']} | {ln['numero']} (x{ln['cantidad']})")
                
                if st.button("🗑️ Limpiar líneas", key="btn_clear_lineas"):
                    st.session_state.lista_lineas = []
                    st.rerun()
            else:
                st.info("La gestión móvil aplica también para Full Tigo.")

    # --- COLUMNA DERECHA: REPRESENTANTE LEGAL ---
    with col_der:
        st.markdown("### 👤 Representante Legal")
        nombre_rep  = st.text_input("Nombre Rep. Legal:", key="reg_nombre_rep")
        cedula_rep  = st.text_input("Cédula Rep. Legal:", key="reg_cedula_rep")
        email_rep   = st.text_input("Correo Rep. Legal:", key="reg_email_rep")
        movil_rep   = st.text_input("Móvil Rep. Legal:", key="reg_movil_rep")

        st.markdown("### 📊 Estado y Plan")
        estado_ini = st.selectbox("Estado inicial:", ESTADOS, key="reg_estado")
        notas      = st.text_area("📝 Notas / Bitácora:", key="reg_notas", height=80)
        fecha_seg  = st.date_input("📅 Fecha de seguimiento:", value=date.today(), key="reg_fecha_seg")
        tipo_seg   = st.selectbox("Tipo de seguimiento:", TIPOS_SEGUIMIENTO, key="reg_tipo_seg")

        st.markdown("**Familia de plan:**")
        if division == "Móvil":
            familia = st.radio("", list(PLANES_MOVIL.keys()), horizontal=True, key="reg_familia", label_visibility="collapsed")
            planes_lista = list(PLANES_MOVIL[familia].keys())
            plan_sel = st.selectbox("Servicio:", planes_lista, key="reg_plan")
            lineas = st.number_input("Líneas:", min_value=1, max_value=200, value=1, key="reg_lineas",
                                      help="Use + / - para ajustar")

            precio_total = calcular_precio_movil(familia, plan_sel, lineas)
            if familia == "Negocios 5.0":
                desc_info = "Descuentos 5.0: 2L=10% · 3-5L=20% · 6-8L=25% · 9+L=30% · Portación=50% 1er mes"
            else:
                desc_info = "Descuentos 6.0: 3-5L=13% · 6-9L=25% · 10+L=30% · Portación=50% 1er mes"
            st.caption(desc_info)
            # Definir la lista al inicio del archivo, fuera de las funciones
            FRASES_MOTIVACION = [
                "🚀 ¡Vamos por ese cierre, hoy es un gran día!",
                "💎 La calidad de tu servicio es nuestra mayor ventaja.",
                "📈 ¡A superar la meta de ventas de este mes!",
                "🤝 Cada cliente cuenta, ¡haz que esta venta sea memorable!",
                "🎯 ¡Enfocados en el objetivo, excelente gestión!",
                "⚡ ¡Tu energía determina tu éxito, mantén el ritmo!",
                "🌟 Un cliente feliz es la mejor estrategia de crecimiento.",
                "📊 Buenos datos y gran estrategia siempre cierran ventas.",
                "🔥 La persistencia vence a la resistencia, ¡tú puedes!",
                "🏆 Los grandes logros nacen de la constancia diaria.",
                "💼 Profesionalismo y visión: así se construyen relaciones duraderas.",
                "🧠 Conecta con el cliente, entiende su necesidad y el cierre será natural.",
                "💡 Cada gestión bien hecha es una semilla para el éxito de mañana.",
                "🥇 ¡No hay límites cuando hay buena planeación y actitud!"
            ]
            st.markdown(f"""
            <div style="background:#e0f2fe; border-left:4px solid #00aaff; border-radius:6px;
                        padding:12px 16px; margin:8px 0;">
             <span style="font-size:16px; font-weight:700; color:#0369a1;">
                💰 Total Estimado: ${precio_total:,} COP
              </span><br>
              <span style="font-size:12px; color:#0ea5e9; font-style:italic;">
                • {random.choice(FRASES_MOTIVACION)}
              </span>
            </div>
            """, unsafe_allow_html=True)
            portafolio_val = "MOVIL"
            servicio_val   = "AVANZADO" if "Empresarial" in familia else "BASICO"
        else:
            plan_sel = st.selectbox("Servicio Fijo:", list(PLANES_FIJO.keys()), key="reg_plan_fijo")
            precio_total = PLANES_FIJO.get(plan_sel, 0)
            lineas = 1
            familia = "FIJO"
            st.markdown(f"""
            <div style="background:#e0f2fe; border-left:4px solid #00aaff; border-radius:6px;
                        padding:12px 16px; margin:8px 0;">
              <span style="font-size:16px; font-weight:700; color:#0369a1;">
                💰 Total Estimado: ${precio_total:,} COP
              </span>
            </div>
            """, unsafe_allow_html=True)
            portafolio_val = "FIJO"
            servicio_val   = "AVANZADO" if "Avanzado" in plan_sel or "Empresarial" in plan_sel else "BASICO"

        # Documentos
        st.markdown("### 📎 Documentos del Cliente")
        st.caption("Adjuntar documentos")
        docs = st.file_uploader("", accept_multiple_files=True,
                                 type=["pdf","png","jpg","docx","xlsx"],
                                 key="reg_docs", label_visibility="collapsed")
        if docs:
            for d in docs:
                st.success(f"✅ {d.name}")

    st.markdown("---")
    guardar_col = st.columns([1])[0]
    if st.button("💾 Guardar Venta", type="primary", use_container_width=True, key="btn_guardar_venta"):
          
        # Validaciones
        errores = []
        
        if not num_doc.strip():
            errores.append("Número de Documento es obligatorio.")
        
        if not razon.strip():
            errores.append("Razón Social o Nombre es obligatorio.")
        
        if not depto:
            errores.append("Departamento es obligatorio.")
        
        if not municipio:
            errores.append("Municipio es obligatorio.")
        
        # Gestión Técnica obligatoria para Móvil y Full Tigo
        requiere_gestion = (
            division == "Móvil"
            or "Full Tigo" in plan_sel
        )
        
        if requiere_gestion and not st.session_state.get("lista_lineas"):
            errores.append(
                "Debe registrar al menos una Gestión Técnica (Portabilidad, Línea Nueva o Línea Existente)."
            )
        
        # Si existen errores no continúa
        if errores:
            for e in errores:
                st.error(f"❌ {e}")
            st.stop()
           

        registro = {
            "ESTADO":           estado_ini,
            "PORTAFOLIO":       portafolio_val,
            "SERVICIO":         servicio_val,
            "ASESOR":           st.session_state.get("usuario", ""),
            "NIT":              num_doc.strip(),
            "CLIENTE":          razon.strip(),
            "TEL_CONTACTO":     movil_contacto.strip(),
            "EMAIL_CLIENTE":    email_rep.strip(),
            "TIPO_DOC":         tipo_doc,
            "RAZON_SOCIAL":     razon.strip(),
            "DIRECCION":        direccion.strip(),
            "BARRIO":           barrio.strip(),
            "DEPARTAMENTO":     depto,
            "MUNICIPIO":        municipio,
            "EMAIL_CONTACTO":   email_contacto.strip(),
            "NOMBRE_CONTACTO":  nombre_contacto.strip(),
            "MOVIL_CONTACTO":   movil_contacto.strip(),
            "NOMBRE_REP":       nombre_rep.strip(),
            "CEDULA_REP":       cedula_rep.strip(),
            "EMAIL_REP":        email_rep.strip(),
            "MOVIL_REP":        movil_rep.strip(),
            "DIVISION":         division,
            "FAMILIA_PLAN":     familia,
            "PLAN":             plan_sel,
            "LINEAS":           str(lineas),
            "VALOR_TOTAL":      str(precio_total),
            "NOTAS":            notas.strip(),
            "FECHA_SEGUIMIENTO": str(fecha_seg),
            "TIPO_SEGUIMIENTO": tipo_seg,
        }

        ok, resultado = crear_venta(registro)
    
        if ok:
            st.success(f"✅ Venta registrada exitosamente. **ID_VENTA: {resultado}**")
    
            msg = (
                f"🆕 <b>Nueva Venta — Somos Telser</b>\n"
                f"📋 ID: {resultado} | {razon.strip()}\n"
                f"📦 {portafolio_val} | {plan_sel}\n"
                f"💰 ${precio_total:,} COP\n"
                f"📍 {estado_ini} | {depto}, {municipio}\n"
                f"🧑 {st.session_state.get('usuario','')}\n"
                f"📅 {datetime.now(TZ).strftime('%d/%m/%Y %H:%M')}"
            )
    
            enviar_telegram(msg)
            st.cache_data.clear()
            limpiar_formulario()
            st.rerun()
    
        else:
            st.error(f"❌ Error al registrar: {resultado}")

      
# ═══════════=================================================
# TAB 2 — ACTUALIZAR ESTADO + EDICIÓN COMPLETA DE LA VENTA
# ════════════════════════════════════════════════════════════
 
def tab_actualizar_estado(df: pd.DataFrame):
 
    # ── Helper: limpia nan/None/"" → fallback ──────────────
    def val(v, fallback=""):
        if v is None:
            return fallback
        s = str(v).strip()
        return fallback if s.lower() in ("nan", "none", "") else s
 
    st.markdown("### 🔄 Actualizar Seguimiento de Venta")
 
    if df.empty:
        st.info("📭 No hay ventas registradas.")
        return
 
    # Filtro por rol
    df_filtrado = (
        df[df["ASESOR"] == st.session_state.get("usuario", "")]
        if st.session_state.get("rol") == "asesor"
        else df
    )
 
    if df_filtrado.empty:
        st.info("Sin ventas asignadas.")
        return
 
    # ── Selector de venta ──────────────────────────────────
    lista_ops = opciones_ventas(df_filtrado)
    seleccion = st.selectbox("Selecciona la venta:", lista_ops, key="act_select")
    id_venta  = extraer_id_opcion(seleccion)
 
    if id_venta is None:
        st.error("No se pudo identificar la venta.")
        return
 
    venta = buscar_venta(id_venta)
    if venta is None:
        st.error(f"Venta ID {id_venta} no encontrada.")
        return
 
    estado_anterior = val(venta.get("ESTADO"), "Sin estado")
 
    st.markdown("---")
 
    # ══════════════════════════════════════════════════════
    # BLOQUE 1 — ESTADO (siempre visible arriba, destacado)
    # ══════════════════════════════════════════════════════
    st.markdown(f"""
    <div style="background:#e0f2fe; border-left:5px solid #00a0e3;
                border-radius:8px; padding:12px 18px; margin-bottom:16px;">
      <span style="font-size:14px; font-weight:700; color:#0369a1;">
        📍 Estado actual: <u>{estado_anterior}</u>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        🆔 ID Venta: <b>{id_venta}</b>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        👤 {val(venta.get('CLIENTE'), 'Sin nombre')}
      </span>
    </div>
    """, unsafe_allow_html=True)
 
    idx_actual = ESTADOS.index(estado_anterior) if estado_anterior in ESTADOS else 0
    nuevo_estado = st.selectbox(
        "🔁 Cambiar estado a:",
        ESTADOS,
        index=idx_actual,
        key="act_nuevo_estado"
    )
 
    st.markdown("---")
 
    # ══════════════════════════════════════════════════════
    # BLOQUE 2 — EDICIÓN COMPLETA DE TODOS LOS CAMPOS
    # ══════════════════════════════════════════════════════
    st.markdown("#### ✏️ Revisar y corregir datos de la venta")
 
    col_izq, col_der = st.columns(2)
 
    # ── COLUMNA IZQUIERDA: Datos del Cliente ──────────────
    with col_izq:
        st.markdown("##### 📋 Datos del Cliente")
 
        tipo_doc_actual = val(venta.get("TIPO_DOC"), "NIT")
        tipo_doc_idx = TIPOS_DOC.index(tipo_doc_actual) if tipo_doc_actual in TIPOS_DOC else 0
        e_tipo_doc = st.selectbox("Tipo Doc:", TIPOS_DOC, index=tipo_doc_idx, key="act_tipo_doc")
 
        e_nit      = st.text_input("Número de Documento:", value=val(venta.get("NIT")),      key="act_nit")
        e_razon    = st.text_input("Razón Social / Cliente:", value=val(venta.get("CLIENTE")), key="act_razon")
        e_tel      = st.text_input("Teléfono Contacto:", value=val(venta.get("TEL_CONTACTO")), key="act_tel")
        e_email    = st.text_input("Email Cliente:", value=val(venta.get("EMAIL_CLIENTE")),   key="act_email")
        e_dir      = st.text_input("Dirección:", value=val(venta.get("DIRECCION")),           key="act_dir")
        e_barrio   = st.text_input("Barrio:", value=val(venta.get("BARRIO")),                 key="act_barrio")
 
        # Departamento / Municipio
        deptos_lista = [""] + sorted(DEPARTAMENTOS_MUNICIPIOS.keys())
        depto_actual = val(venta.get("DEPARTAMENTO"))
        depto_idx    = deptos_lista.index(depto_actual) if depto_actual in deptos_lista else 0
        e_depto = st.selectbox("Departamento:", deptos_lista, index=depto_idx, key="act_depto")
 
        muni_lista   = [""] + DEPARTAMENTOS_MUNICIPIOS.get(e_depto, []) if e_depto else [""]
        muni_actual  = val(venta.get("MUNICIPIO"))
        muni_idx     = muni_lista.index(muni_actual) if muni_actual in muni_lista else 0
        e_municipio  = st.selectbox("Municipio:", muni_lista, index=muni_idx,
                                    key="act_municipio", disabled=(not e_depto))
 
        e_email_c  = st.text_input("Email Contacto:", value=val(venta.get("EMAIL_CONTACTO")),   key="act_email_c")
        e_nom_c    = st.text_input("Nombre Contacto:", value=val(venta.get("NOMBRE_CONTACTO")), key="act_nom_c")
        e_mov_c    = st.text_input("Móvil Contacto:", value=val(venta.get("MOVIL_CONTACTO")),   key="act_mov_c")
 
    # ── COLUMNA DERECHA: Rep. Legal + Plan + Seguimiento ──
    with col_der:
        st.markdown("##### 👤 Representante Legal")
        e_nom_rep  = st.text_input("Nombre Rep. Legal:", value=val(venta.get("NOMBRE_REP")), key="act_nom_rep")
        e_ced_rep  = st.text_input("Cédula Rep. Legal:", value=val(venta.get("CEDULA_REP")), key="act_ced_rep")
        e_email_rep= st.text_input("Correo Rep. Legal:", value=val(venta.get("EMAIL_REP")),  key="act_email_rep")
        e_mov_rep  = st.text_input("Móvil Rep. Legal:", value=val(venta.get("MOVIL_REP")),   key="act_mov_rep")
 
        st.markdown("##### 📦 Portafolio y Plan")
 
        # División
        div_actual = val(venta.get("DIVISION"), "Fijo")
        div_opts   = ["Móvil", "Fijo"]
        div_idx    = div_opts.index(div_actual) if div_actual in div_opts else 1
        e_division = st.radio("División:", div_opts, index=div_idx,
                              horizontal=True, key="act_division")
 
        # Portafolio derivado de la división
        portafolio_val = "MOVIL" if e_division == "Móvil" else "FIJO"
 
        if e_division == "Móvil":
            familias   = list(PLANES_MOVIL.keys())
            fam_actual = val(venta.get("FAMILIA_PLAN"), familias[0])
            fam_idx    = familias.index(fam_actual) if fam_actual in familias else 0
            e_familia  = st.radio("Familia:", familias, index=fam_idx,
                                  horizontal=True, key="act_familia")
 
            planes_lista = list(PLANES_MOVIL[e_familia].keys())
            plan_actual  = val(venta.get("PLAN"), planes_lista[0])
            plan_idx     = planes_lista.index(plan_actual) if plan_actual in planes_lista else 0
            e_plan       = st.selectbox("Plan:", planes_lista, index=plan_idx, key="act_plan")
 
            e_lineas = st.number_input("Líneas:", min_value=1, max_value=200,
                                       value=max(1, int(val(venta.get("LINEAS"), "1") or "1")),
                                       key="act_lineas")
            precio_total = calcular_precio_movil(e_familia, e_plan, e_lineas)
            servicio_val = "AVANZADO" if "Empresarial" in e_familia else "BASICO"
        else:
            e_familia    = "FIJO"
            planes_fijo  = list(PLANES_FIJO.keys())
            plan_actual  = val(venta.get("PLAN"), planes_fijo[0])
            plan_idx     = planes_fijo.index(plan_actual) if plan_actual in planes_fijo else 0
            e_plan       = st.selectbox("Plan Fijo:", planes_fijo, index=plan_idx, key="act_plan_fijo")
            e_lineas     = 1
            precio_total = PLANES_FIJO.get(e_plan, 0)
            servicio_val = "AVANZADO" if "Avanzado" in e_plan or "Empresarial" in e_plan else "BASICO"
 
        st.markdown(f"""
        <div style="background:#e0f2fe; border-left:4px solid #00a0e3;
                    border-radius:6px; padding:10px 14px; margin:8px 0;">
          <span style="font-size:15px; font-weight:700; color:#0369a1;">
            💰 Total: ${precio_total:,} COP
          </span>
        </div>
        """, unsafe_allow_html=True)
 
        st.markdown("##### 📅 Seguimiento")
        # Fecha de seguimiento
        fecha_raw = val(venta.get("FECHA_SEGUIMIENTO"))
        try:
            fecha_val = datetime.strptime(fecha_raw, "%Y-%m-%d").date() if fecha_raw else date.today()
        except ValueError:
            fecha_val = date.today()
        e_fecha_seg = st.date_input("Fecha seguimiento:", value=fecha_val, key="act_fecha_seg")
 
        tipo_seg_actual = val(venta.get("TIPO_SEGUIMIENTO"), TIPOS_SEGUIMIENTO[0])
        tipo_seg_idx    = TIPOS_SEGUIMIENTO.index(tipo_seg_actual) if tipo_seg_actual in TIPOS_SEGUIMIENTO else 0
        e_tipo_seg = st.selectbox("Tipo seguimiento:", TIPOS_SEGUIMIENTO,
                                  index=tipo_seg_idx, key="act_tipo_seg")
 
        e_notas = st.text_area("📝 Notas / Bitácora:", value=val(venta.get("NOTAS")),
                               key="act_notas", height=90)
 
        nota_nueva = st.text_area("💬 Agregar nota al historial (opcional):",
                                  key="act_nota_nueva", height=70,
                                  placeholder="Esta nota se agregará con fecha y hora...")

    # ════════════════════════════════════════════════════════════
# MÓDULO DE REGISTRO DE GESTIÓN — va dentro de tab_actualizar_estado
# Insértalo DESPUÉS del bloque de edición de campos y ANTES del botón
# "💾 Guardar y Notificar"
# ════════════════════════════════════════════════════════════

    st.markdown("---")
    st.markdown("#### 📋 Registrar Gestión de Seguimiento")
    st.caption("Registra cada contacto con el cliente. Queda guardado en el historial.")

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        tipo_gestion = st.selectbox(
            "Tipo de gestión realizada:",
            [
                "📞 Llamada — Contestó",
                "📞 Llamada — No contestó",
                "📞 Llamada — Buzón de voz",
                "💬 WhatsApp — Respondió",
                "💬 WhatsApp — No respondió",
                "💬 WhatsApp — Visto sin respuesta",
                "📧 Correo — Enviado",
                "📧 Correo — Respondió",
                "🤝 Visita — Realizada",
                "🤝 Visita — No estaba / reprogramar",
                "🖥️ Reunión virtual — Realizada",
                "🖥️ Reunión virtual — No se conectó",
            ],
            key="act_tipo_gestion"
        )

        resultado_gestion = st.selectbox(
            "Resultado:",
            [
                "✅ Interesado — avanza",
                "🔄 Pendiente — requiere seguimiento",
                "📅 Cita agendada",
                "❌ No interesado",
                "⏳ Solicita más tiempo",
                "📄 Solicitó propuesta formal",
                "✍️ En proceso de firma",
                "🚫 No disponible / cambiar fecha",
            ],
            key="act_resultado_gestion"
        )

    with col_g2:
        # Próxima fecha de seguimiento
        fecha_prox = st.date_input(
            "📅 Próxima fecha de seguimiento:",
            value=date.today(),
            key="act_fecha_prox"
        )

        tipo_prox = st.selectbox(
            "Tipo de próximo contacto:",
            TIPOS_SEGUIMIENTO,
            key="act_tipo_prox"
        )

        detalle_gestion = st.text_area(
            "📝 Detalle / observación:",
            placeholder="Ej: El cliente solicitó revisar la propuesta con su socio...",
            key="act_detalle_gestion",
            height=90
        )

    # ── Vista previa del registro que se va a guardar ──────
    if detalle_gestion.strip() or tipo_gestion:
        ts_prev = datetime.now(TZ).strftime("%d/%m/%Y %H:%M")
        st.markdown(
            f"<div style='background:#f8fafc; border:1px solid #e2e8f0; "
            f"border-radius:8px; padding:10px 14px; margin:8px 0; font-size:12px;'>"
            f"<b>Vista previa del registro:</b><br>"
            f"📅 {ts_prev} · {tipo_gestion}<br>"
            f"📌 {resultado_gestion}<br>"
            f"🗓️ Próximo contacto: {fecha_prox.strftime('%d/%m/%Y')} · {tipo_prox}<br>"
            f"💬 {detalle_gestion.strip() or '(sin detalle)'}"
            f"</div>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ════════════════════════════════════════════════════════
    # HISTORIAL DE GESTIONES ANTERIORES
    # ════════════════════════════════════════════════════════
    notas_existentes = val(venta.get("NOTAS"), "")
    if notas_existentes:
        with st.expander("📂 Ver historial de gestiones anteriores", expanded=False):
            # Mostrar cada línea del historial con estilo
            for linea in notas_existentes.split("\n"):
                linea = linea.strip()
                if not linea:
                    continue
                # Color según tipo de gestión registrada
                if "Contestó" in linea or "Respondió" in linea or "Interesado" in linea:
                    color = "#f0fdf4"; borde = "#22c55e"
                elif "No contestó" in linea or "No respondió" in linea or "No interesado" in linea:
                    color = "#fef2f2"; borde = "#ef4444"
                elif "Cita" in linea or "firma" in linea or "propuesta" in linea:
                    color = "#eff6ff"; borde = "#3b82f6"
                else:
                    color = "#f8fafc"; borde = "#cbd5e1"

                st.markdown(
                    f"<div style='background:{color}; border-left:3px solid {borde}; "
                    f"border-radius:5px; padding:6px 10px; margin:3px 0; font-size:11px;'>"
                    f"{linea}"
                    f"</div>",
                    unsafe_allow_html=True
                )

    # ════════════════════════════════════════════════════════
    # BOTÓN GUARDAR — reemplaza el que ya tenías
    # ════════════════════════════════════════════════════════
    if st.button("💾 Guardar y Notificar", type="primary",
                 use_container_width=True, key="btn_act_guardar"):

        errores = []
        if not e_nit.strip():   errores.append("Número de Documento es obligatorio.")
        if not e_razon.strip(): errores.append("Razón Social / Cliente es obligatorio.")
        if errores:
            for err in errores:
                st.error(f"❌ {err}")
            return

        # ── Construir entrada del historial ────────────────
        ts = datetime.now(TZ).strftime("%d/%m/%Y %H:%M")
        entrada_historial = (
            f"\n[{ts}] {tipo_gestion} | {resultado_gestion}"
            f" | Próx: {fecha_prox.strftime('%d/%m/%Y')} {tipo_prox}"
        )
        if detalle_gestion.strip():
            entrada_historial += f"\n    💬 {detalle_gestion.strip()}"

        # Acumular sobre notas previas
        notas_acumuladas = val(venta.get("NOTAS"), "") + entrada_historial

        # Si el usuario también escribió nota libre adicional
        nota_libre = st.session_state.get("act_nota_nueva", "").strip()
        if nota_libre:
            notas_acumuladas += f"\n[{ts}] 📝 {nota_libre}"

        campos_actualizar = {
            # Estado
            "ESTADO":            nuevo_estado,
            # Datos cliente
            "TIPO_DOC":          e_tipo_doc,
            "NIT":               e_nit.strip(),
            "CLIENTE":           e_razon.strip(),
            "TEL_CONTACTO":      e_tel.strip(),
            "EMAIL_CLIENTE":     e_email.strip(),
            "RAZON_SOCIAL":      e_razon.strip(),
            "DIRECCION":         e_dir.strip(),
            "BARRIO":            e_barrio.strip(),
            "DEPARTAMENTO":      e_depto,
            "MUNICIPIO":         e_municipio,
            "EMAIL_CONTACTO":    e_email_c.strip(),
            "NOMBRE_CONTACTO":   e_nom_c.strip(),
            "MOVIL_CONTACTO":    e_mov_c.strip(),
            # Representante legal
            "NOMBRE_REP":        e_nom_rep.strip(),
            "CEDULA_REP":        e_ced_rep.strip(),
            "EMAIL_REP":         e_email_rep.strip(),
            "MOVIL_REP":         e_mov_rep.strip(),
            # Plan
            "DIVISION":          e_division,
            "PORTAFOLIO":        portafolio_val,
            "SERVICIO":          servicio_val,
            "FAMILIA_PLAN":      e_familia,
            "PLAN":              e_plan,
            "LINEAS":            str(e_lineas),
            "VALOR_TOTAL":       str(precio_total),
            # Seguimiento actualizado con próxima gestión
            "FECHA_SEGUIMIENTO": str(fecha_prox),
            "TIPO_SEGUIMIENTO":  tipo_prox,
            # Historial completo
            "NOTAS":             notas_acumuladas,
        }

        ok = actualizar_venta(id_venta, campos_actualizar)

        if ok:
            st.cache_data.clear()

            # ── Notificación Telegram ──────────────────────
            msg_tg = (
                f"🔄 <b>Cambio de Estado — Somos Telser</b>\n"
                f"📋 ID: {id_venta} | {e_razon.strip()}\n"
                f"📍 {estado_anterior} → {nuevo_estado}\n"
                f"📞 {tipo_gestion}\n"
                f"📌 {resultado_gestion}\n"
                f"🗓️ Próx: {fecha_prox.strftime('%d/%m/%Y')} · {tipo_prox}\n"
                f"💬 {detalle_gestion.strip() or 'Sin detalle'}\n"
                f"📅 {ts}"
            )
            enviar_telegram(msg_tg)

            st.success(
                f"✅ Venta **{id_venta}** guardada. "
                f"Estado: **{estado_anterior} → {nuevo_estado}**"
            )
            st.info("🔔 Notificación enviada a Telegram.")
            st.rerun()

        else:
            st.error("❌ No se pudo guardar. Intenta nuevamente.")
 
    # ══════════════════════════════════════════════════════
    # BOTÓN GUARDAR
    # ══════════════════════════════════════════════════════
    st.markdown("---")
    if st.button("💾 Guardar y Notificar", type="primary",
                 use_container_width=True, key="btn_act_guardar"):
 
        # Validaciones mínimas
        errores = []
        if not e_nit.strip():   errores.append("Número de Documento es obligatorio.")
        if not e_razon.strip(): errores.append("Razón Social / Cliente es obligatorio.")
 
        if errores:
            for err in errores:
                st.error(f"❌ {err}")
            return
 
        # Construir historial de notas
        notas_acumuladas = val(venta.get("NOTAS"), "")
        if nota_nueva.strip():
            ts = datetime.now().strftime("%d/%m/%Y %H:%M")
            notas_acumuladas += f"\n[{ts}] {nota_nueva.strip()}"
 
        campos_actualizar = {
            # Estado
            "ESTADO":           nuevo_estado,
            # Datos cliente
            "TIPO_DOC":         e_tipo_doc,
            "NIT":              e_nit.strip(),
            "CLIENTE":          e_razon.strip(),
            "TEL_CONTACTO":     e_tel.strip(),
            "EMAIL_CLIENTE":    e_email.strip(),
            "RAZON_SOCIAL":     e_razon.strip(),
            "DIRECCION":        e_dir.strip(),
            "BARRIO":           e_barrio.strip(),
            "DEPARTAMENTO":     e_depto,
            "MUNICIPIO":        e_municipio,
            "EMAIL_CONTACTO":   e_email_c.strip(),
            "NOMBRE_CONTACTO":  e_nom_c.strip(),
            "MOVIL_CONTACTO":   e_mov_c.strip(),
            # Representante legal
            "NOMBRE_REP":       e_nom_rep.strip(),
            "CEDULA_REP":       e_ced_rep.strip(),
            "EMAIL_REP":        e_email_rep.strip(),
            "MOVIL_REP":        e_mov_rep.strip(),
            # Plan
            "DIVISION":         e_division,
            "PORTAFOLIO":       portafolio_val,
            "SERVICIO":         servicio_val,
            "FAMILIA_PLAN":     e_familia,
            "PLAN":             e_plan,
            "LINEAS":           str(e_lineas),
            "VALOR_TOTAL":      str(precio_total),
            # Seguimiento
            "FECHA_SEGUIMIENTO": str(e_fecha_seg),
            "TIPO_SEGUIMIENTO":  e_tipo_seg,
            "NOTAS":             notas_acumuladas,
        }
 
        ok = actualizar_venta(id_venta, campos_actualizar)
 
        if ok:
            # Notificación Telegram
            ts_fmt = datetime.now().strftime("%d/%m/%Y %H:%M")
            msg_tg = (
                f"🔄 <b>Cambio de Estado — Somos Telser</b>\n"
                f"📋 ID: {id_venta} | {e_razon.strip()}\n"
                f"📍 {estado_anterior} → {nuevo_estado}\n"
                f"💬 {nota_nueva.strip() or 'Sin nota'}\n"
                f"📅 {ts_fmt}"
            )
            enviar_telegram(msg_tg)
 
            st.success(
                f"✅ Venta **{id_venta}** actualizada correctamente. "
                f"Estado: **{estado_anterior} → {nuevo_estado}**"
            )
            st.info("🔔 Notificación enviada a Telegram.")
 
            # Limpiar panel → fuerza recarga limpia
            st.rerun()
        else:
            st.error("❌ No se pudo guardar. Verifica los datos e intenta nuevamente.")
 
# ════════════════════════════════════════════════════════════
# TAB 3 — BASE DE DATOS / DASHBOARD
# ════════════════════════════════════════════════════════════
 
def tab_base_datos(df: pd.DataFrame):
    # Paleta corporativa Somos Telser
    COLOR_AZUL      = "#00a0e3"   # Instaladas / Activadas
    COLOR_GRIS_OSC  = "#231f20"   # Anuladas
    COLOR_FONDO     = "#f4f4f4"   # Fondos y detalles
    COLOR_AZUL_SEC  = "#0288d1"   # Botones / secundario
 
    rol = st.session_state.get("rol", "asesor")
    nombre_rol = "Administrador" if rol == "admin" else "Asesor"
    st.markdown(f"### 📊 Dashboard y Base de Datos — Vista {nombre_rol}")
 
    if df.empty:
        st.info("📭 Sin datos aún.")
        return
 
    # ── KPIs — calculados directo desde el DataFrame ──────
    total      = len(df)
    instalados = len(df[df["ESTADO"] == "Instalado"])
    activados  = len(df[df["ESTADO"] == "Activado"])
    anulados   = len(df[df["ESTADO"] == "Anulado"])
    fijo_c     = len(df[df["PORTAFOLIO"] == "FIJO"])
    movil_c    = len(df[df["PORTAFOLIO"] == "MOVIL"])
 
    # Instalados/Anulados/Activados por portafolio — fuente única: df
    fijo_instalado  = len(df[(df["PORTAFOLIO"] == "FIJO")  & (df["ESTADO"] == "Instalado")])
    fijo_anulado    = len(df[(df["PORTAFOLIO"] == "FIJO")  & (df["ESTADO"] == "Anulado")])
    movil_activado  = len(df[(df["PORTAFOLIO"] == "MOVIL") & (df["ESTADO"] == "Activado")])
    movil_anulado   = len(df[(df["PORTAFOLIO"] == "MOVIL") & (df["ESTADO"] == "Anulado")])
 
    try:
        ingresos = df["VALOR_TOTAL"].apply(
            lambda x: float(str(x).replace(",","")) if str(x).replace(".","").replace(",","").isdigit() else 0
        ).sum()
        ingresos_fmt = f"${ingresos:,.0f}"
    except Exception:
        ingresos_fmt = "$0"
 
    # ── Tarjetas KPI con paleta corporativa ──────────────
    def kpi_card(label, valor, color_borde, color_num="#1e293b"):
        return f"""
        <div style="background:{COLOR_FONDO}; border-left:5px solid {color_borde};
                    border-radius:8px; padding:14px 16px; text-align:center;
                    box-shadow:0 1px 4px rgba(0,0,0,0.07);">
          <div style="font-size:11px; color:#64748b; font-weight:600;
                      text-transform:uppercase; letter-spacing:0.5px;">{label}</div>
          <div style="font-size:30px; font-weight:800; color:{color_num}; margin-top:4px;">{valor}</div>
        </div>"""
 
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(kpi_card("📋 Registros", total, COLOR_AZUL_SEC), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("✅ Instalados", instalados, COLOR_AZUL), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("⚡ Activados", activados, COLOR_AZUL), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("❌ Anulados", anulados, COLOR_GRIS_OSC, COLOR_GRIS_OSC), unsafe_allow_html=True)
    with c5: st.markdown(kpi_card("🌐 Fijo / 📱 Móvil", f"{fijo_c} / {movil_c}", COLOR_AZUL_SEC), unsafe_allow_html=True)
 
    st.markdown("<br>", unsafe_allow_html=True)
 
    # ── Gráfica 1: Ventas por Estado ─────────────────────
    st.markdown("#### 📈 Ventas por Estado")
    conteo_estado = df["ESTADO"].value_counts().reset_index()
    conteo_estado.columns = ["Estado", "Cantidad"]
    # Colores corporativos por estado
    def color_estado(e):
        if e in ("Instalado", "Activado"):  return COLOR_AZUL
        if e == "Anulado":                  return COLOR_GRIS_OSC
        return COLOR_AZUL_SEC
 
    conteo_estado["Color"] = conteo_estado["Estado"].apply(color_estado)
    fig_estado = px.bar(
        conteo_estado, x="Estado", y="Cantidad",
        color="Estado",
        color_discrete_map={row["Estado"]: row["Color"] for _, row in conteo_estado.iterrows()},
        template="plotly_white",
        text="Cantidad",
    )
    fig_estado.update_traces(textposition="outside", textfont_size=11)
    fig_estado.update_layout(
        height=340, showlegend=False,
        xaxis_title="", yaxis_title="Cantidad",
        margin=dict(l=0, r=0, t=20, b=10),
        font=dict(family="Arial", size=12),
        plot_bgcolor="white",
    )
    # Etiquetas horizontales — sin tickangle
    fig_estado.update_xaxes(tickangle=0, tickfont=dict(size=11))
    st.plotly_chart(fig_estado, use_container_width=True)
 
    st.markdown("---")
 
    # ── Gráfica 2: Ventas por Asesor ─────────────────────
    st.markdown("#### 👤 Ventas por Asesor")
    try:
        df_asesor = df.copy()
        # Contar ventas (no valor, ya que VALOR_TOTAL puede estar vacío en registros migrados)
        por_asesor = df_asesor.groupby("ASESOR")["ID_VENTA"].count().reset_index()
        por_asesor.columns = ["Asesor", "Ventas"]
        # Abreviar correos para eje X legible
        por_asesor["Asesor_corto"] = por_asesor["Asesor"].apply(
            lambda x: str(x).split("@")[0].replace(".", " ").replace("distribuidor","dist.").title()
            if "@" in str(x) else str(x)
        )
        fig_asesor = px.bar(
            por_asesor, x="Asesor_corto", y="Ventas",
            color_discrete_sequence=[COLOR_AZUL],
            template="plotly_white",
            text="Ventas",
        )
        fig_asesor.update_traces(textposition="outside", textfont_size=11)
        fig_asesor.update_layout(
            height=300, showlegend=False,
            xaxis_title="", yaxis_title="Nº Ventas",
            margin=dict(l=0, r=0, t=20, b=10),
            font=dict(family="Arial", size=12),
        )
        fig_asesor.update_xaxes(tickangle=0, tickfont=dict(size=11))
        st.plotly_chart(fig_asesor, use_container_width=True)
    except Exception as e:
        st.warning(f"No se pudo generar gráfica de asesor: {e}")
 
    st.markdown("---")
 
    # ── Gráfica 3: Instalados / Activados / Anulados por Portafolio ──
    st.markdown("#### 📊 Instalados, Activados y Anulados por Portafolio")
 
    # Construcción del DataFrame desde el cruce real de datos
    datos_portafolio = []
    for portafolio in ["FIJO", "MOVIL"]:
        for estado in ["Instalado", "Activado", "Anulado"]:
            cnt = len(df[(df["PORTAFOLIO"] == portafolio) & (df["ESTADO"] == estado)])
            if cnt > 0:
                datos_portafolio.append({
                    "Portafolio": portafolio,
                    "Estado": estado,
                    "Cantidad": cnt,
                })
 
    if datos_portafolio:
        df_port = pd.DataFrame(datos_portafolio)
        fig_port = px.bar(
            df_port,
            x="Portafolio", y="Cantidad", color="Estado",
            barmode="group",
            color_discrete_map={
                "Instalado": COLOR_AZUL,
                "Activado":  COLOR_AZUL_SEC,
                "Anulado":   COLOR_GRIS_OSC,
            },
            template="plotly_white",
            text="Cantidad",
        )
        fig_port.update_traces(textposition="outside", textfont_size=12)
        fig_port.update_layout(
            height=340,
            xaxis_title="", yaxis_title="Cantidad",
            margin=dict(l=0, r=0, t=20, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            font=dict(family="Arial", size=12),
            plot_bgcolor="white",
        )
        fig_port.update_xaxes(tickangle=0, tickfont=dict(size=13, color="#1e293b"))
        st.plotly_chart(fig_port, use_container_width=True)
 
        # Resumen textual de los indicadores clave
        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
        with col_r1:
            st.markdown(kpi_card("FIJO — Instalado", fijo_instalado, COLOR_AZUL), unsafe_allow_html=True)
        with col_r2:
            st.markdown(kpi_card("FIJO — Anulado", fijo_anulado, COLOR_GRIS_OSC, COLOR_GRIS_OSC), unsafe_allow_html=True)
        with col_r3:
            st.markdown(kpi_card("MÓVIL — Activado", movil_activado, COLOR_AZUL), unsafe_allow_html=True)
        with col_r4:
            st.markdown(kpi_card("MÓVIL — Anulado", movil_anulado, COLOR_GRIS_OSC, COLOR_GRIS_OSC), unsafe_allow_html=True)
    else:
        st.info("Sin datos de Instalados/Activados/Anulados.")
 
    st.markdown("---")
 
    # ── Análisis y Recomendaciones ────────────────────────
    st.markdown("#### 💡 Análisis y Recomendaciones")
    col_obs, col_oport = st.columns(2)
    tasa_anulacion = (anulados / total * 100) if total > 0 else 0
    with col_obs:
        st.markdown("**Observación:**")
        if tasa_anulacion > 25:
            st.warning(f"⚠️ Tasa de anulación alta: {tasa_anulacion:.1f}%. Revisar proceso de validación.")
        elif tasa_anulacion > 15:
            st.info(f"ℹ️ Tasa de anulación moderada: {tasa_anulacion:.1f}%. Monitorear.")
        else:
            st.success(f"✅ Tasa de anulación normal: {tasa_anulacion:.1f}%.")
    with col_oport:
        st.markdown("**Oportunidad:**")
        if fijo_c > movil_c:
            st.markdown("• Portafolio **Fijo** lidera. Potenciar cross-selling hacia clientes **Móviles**.")
        else:
            st.markdown("• Portafolio **Móvil** lidera. Potenciar cross-selling hacia clientes **Fijos**.")
 
    st.markdown("---")
 
    # ── Base de Datos Completa ────────────────────────────
    st.markdown("#### 🗃️ Base de Datos Completa")
 
    # Filtros solo para admin
    if rol == "admin":
        asesores_lista = ["Todos"] + sorted(df["ASESOR"].dropna().unique().tolist())
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            f_asesor = st.selectbox("Filtrar por asesor:", asesores_lista, key="db_asesor")
        with col_f2:
            estados_lista = list(df["ESTADO"].dropna().unique())
            f_estados = st.multiselect("Filtrar por estado:", estados_lista,
                                        default=estados_lista, key="db_estados")
        df_vista = df.copy()
        if f_asesor != "Todos":
            df_vista = df_vista[df_vista["ASESOR"] == f_asesor]
        if f_estados:
            df_vista = df_vista[df_vista["ESTADO"].isin(f_estados)]
    else:
        df_vista = df[df["ASESOR"] == st.session_state.get("usuario", "")]
 
    cols_visibles = ["ID_VENTA","ESTADO","PORTAFOLIO","SERVICIO","ASESOR",
                     "FECHA_REGISTRO","NIT","CLIENTE","TEL_CONTACTO","EMAIL_CLIENTE"]
    cols_show = [c for c in cols_visibles if c in df_vista.columns]
 
    st.dataframe(
        df_vista[cols_show].sort_values("ID_VENTA", ascending=True),
        use_container_width=True,
        hide_index=False,
    )
 
    # Exportar vista
    csv_vista = df_vista[cols_show].to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Descargar Vista Actual",
        data=csv_vista,
        file_name=f"crm_vista_{datetime.now(TZ).strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        key="btn_dl_vista"
    )
 
# ════════════════════════════════════════════════════════════
# MAIN (SEGURIDAD DE ROLES SIN AFECTAR CACHÉ)
# ════════════════════════════════════════════════════════════
 
def main():
    if "auth" not in st.session_state:
        st.session_state["auth"] = False
 
    check_auth()
    
    if not st.session_state.get("auth"):
        return

    # Cargar datos una sola vez (la caché de @st.cache_data protegerá esto)
    df = cargar_datos()
 
    # Sidebar
    sidebar_render(df)
 
    # Encabezado principal
    st.markdown("""
    <h1 style="font-size:28px; font-weight:700; color:#1e293b; margin-bottom:2px;">
      📡 Portal de Ventas Somos Telser
    </h1>
    <p style="font-size:14px; color:#64748b; margin-top:0; margin-bottom:16px;">
      Gestión Inteligente de Contratos B2B
    </p>
    """, unsafe_allow_html=True)
 
    # Definir roles
    es_admin = st.session_state.get("rol") == "admin"
 
    # Crear pestañas condicionales
    if es_admin:
        tab1, tab2, tab3 = st.tabs(["📋 Registrar Venta", "🔄 Actualizar Estado", "📊 Base de Datos"])
    else:
        tab1, tab2 = st.tabs(["📋 Registrar Venta", "🔄 Actualizar Estado"])
 
    # Renderizar contenido
    with tab1:
        tab_registrar_venta()
 
    with tab2:
        tab_actualizar_estado(df)
            
    if es_admin:
        with tab3:
            tab_base_datos(df)
 
if __name__ == "__main__":
    main()
