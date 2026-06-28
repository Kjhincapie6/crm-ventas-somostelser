import streamlit as st
import pandas as pd
import os
import random
import requests
import altair as alt
from datetime import date, timedelta

# ==========================================
# CONFIGURACIÓN DE PÁGINA (siempre primero)
# ==========================================
st.set_page_config(page_title="Portal de Ventas Somos Telser", layout="wide")

# ==========================================
# FUNCIÓN TELEGRAM
# ==========================================
def enviar_telegram(mensaje):
    TOKEN   = "8942591199:AAFi8vkAvNyL4LLkUPO9TXKhC2bjukEDmcg"
    CHAT_ID = "1415966548"
    url     = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        r = requests.get(url, params={"chat_id": CHAT_ID, "text": mensaje})
        if r.status_code != 200:
            st.error(f"❌ Telegram error {r.status_code}")
    except Exception as e:
        st.error(f"❌ Error Telegram: {e}")

# ==========================================
# HELPER: RESETEAR FORMULARIO TAB1
# ==========================================
KEYS_FORM = [
    "t_doc","n_doc","nombre","dir_cli","barrio","depto","muni_activo","muni_disabled",
    "email_cli","contacto_cli","tel_contacto","nom_rep","cc_rep","mail_rep","tel_rep",
    "estado_venta","bitacora","fecha_seg","tipo_seg","servicio","lineas","incluye_movil",
    "file_uploader","div_radio","tipo_linea_pop","op_linea_pop","cant_linea_pop","num_linea_pop",
]

def limpiar_formulario():
    for k in KEYS_FORM:
        if k in st.session_state:
            del st.session_state[k]
    st.session_state.lista_lineas = []
    st.session_state.venta_guardada = True

# ==========================================
# PORTAFOLIO COMPLETO (según ayudaventa)
# ==========================================

# --- MÓVIL 5.0 ---
# Descuentos: 1 línea=0%, 2=10%, 3-5=20%, 6-8=25%, 9+=30%
PLANES_MOVIL_50 = {
    "Pospago Negocios 4.9 Plus+ 60GB [5.0]":      44900.0,
    "Pospago Negocios 5.4 Plus+ 100GB [5.0]":     53900.0,
    "Pospago 5.3 Empresarial Ilim GB [5.0]":     113900.0,
}

# --- MÓVIL 6.0 ---
# Descuentos: 1 línea=0%, 3-5=13%, 6-9=25%, 10+=30%
PLANES_MOVIL_60 = {
    "Plan Datos Empresarial 6.9 — 30GB [6.0]":    38300.0,
    "Plan Datos Empresarial 6.10 — 60GB [6.0]":   47900.0,
    "Plan Datos Empresarial 6.11 — 110GB [6.0]":  57900.0,
    "Plan Datos Empresarial 6.12 — Ilim GB [6.0]":113900.0,
    "Plan Datos Empresarial 6.8 FULL TIGO Ilim [6.0]": 54900.0,
}

# Todos los móviles juntos (para el asistente sidebar)
PLANES_MOVIL = {**PLANES_MOVIL_50, **PLANES_MOVIL_60}

# --- FIJO ---
PLANES_FIJO = {
    # Internet Business individual
    "Internet Business 300 Mbps (HFC/FTTx)":         88880.0,
    "Internet Business 500 Mbps (HFC/FTTx)":        115000.0,
    "Internet Business 700 Mbps (HFC/FTTx)":        180001.0,
    # Internet Business Seguro con Ciberseguridad
    "Internet Business Seguro 300 Mbps":             117880.0,
    "Internet Business Seguro 500 Mbps":             144000.0,
    "Internet Business Seguro 700 Mbps":             209000.0,
    # Full Tigo Business (fijo + móvil 6.8)
    "Full Tigo Business 500 Mbps + Móvil 6.8":      169900.0,
    "Full Tigo Business 700 Mbps + Móvil 6.8":      199900.0,
    "Full Tigo Business 1000 Mbps + Móvil 6.8":     299900.0,
    # Full Tigo Business Seguro
    "Full Tigo Business Seguro 500 Mbps + Móvil 6.8": 198900.0,
    "Full Tigo Business Seguro 700 Mbps + Móvil 6.8": 228900.0,
    "Full Tigo Business Seguro 1000 Mbps + Móvil 6.8": 328900.0,
    # Telefonía IP
    "Telefonía IP Voz sin Fronteras Plus (nominal)":  64528.0,
    "Telefonía IP Voz sin Fronteras Plus (empaquetado)": 59276.0,
    # Internet Avanzado GPON 30% dcto
    "Internet Avanzado 50 Mbps GPON":               248740.0,
    "Internet Avanzado 100 Mbps GPON":              298438.0,
    "Internet Avanzado 200 Mbps GPON":              425049.0,
    "Internet Avanzado 300 Mbps GPON":              457638.0,
    "Internet Avanzado 500 Mbps GPON":              518174.0,
}

# ==========================================
# LÓGICA DE DESCUENTOS POR PLAN
# ==========================================
def calcular_descuento(plan_nombre: str, num_lineas: int) -> int:
    """Devuelve el % de descuento según la familia del plan y cantidad de líneas."""
    if "[6.0]" in plan_nombre:
        # Escala Empresarial 6.0
        if num_lineas >= 10: return 30
        if num_lineas >= 6:  return 25
        if num_lineas >= 3:  return 13
        return 0
    elif "[5.0]" in plan_nombre:
        # Escala Negocios 5.0
        if num_lineas >= 9:  return 30
        if num_lineas >= 6:  return 25
        if num_lineas >= 3:  return 20
        if num_lineas == 2:  return 10
        return 0
    else:
        # Fijo: sin descuento por volumen estándar
        return 0

# ==========================================
# UBICACIONES COLOMBIA — COMPLETO
# ==========================================
UBICACIONES_COL = {
    "Amazonas": ["Leticia","Puerto Nariño","El Encanto","La Chorrera","La Pedrera","Tarapacá"],
    "Antioquia": [
        "Medellín","Envigado","Itagüí","Bello","Rionegro","Sabaneta","La Estrella","Caldas","Retiro",
        "Copacabana","Girardota","Barbosa","La Ceja","La Unión","El Retiro","El Carmen de Viboral",
        "El Santuario","Marinilla","Guarne","Caucasia","Turbo","Apartadó","Carepa","Chigorodó",
        "Andes","Jericó","Santa Fe de Antioquia","Yarumal","Amaga","Fredonia","Concordia",
        "Sonsón","Abejorral","Ciudad Bolívar","Urrao","Quibdó","Montebello","Amagá",
        "El Bagre","Zaragoza","Segovia","Remedios","Puerto Berrío","Puerto Nare","Yolombó",
        "Gómez Plata","Angostura","Valdivia","Tarazá","Cáceres","Nechí","San Roque","Maceo",
    ],
    "Arauca": ["Arauca","Tame","Saravena","Fortul","Arauquita","Cravo Norte","Puerto Rondón"],
    "Atlántico": [
        "Barranquilla","Soledad","Malambo","Puerto Colombia","Galapa","Baranoa","Sabanagrande",
        "Santo Tomás","Palmar de Varela","Ponedera","Sabanalarga","Luruaco","Repelón","Suan",
        "Campo de la Cruz","Candelaria","Juan de Acosta","Piojó","Tubará","Usiacurí",
    ],
    "Bolívar": [
        "Cartagena","Magangué","Turbaco","El Carmen de Bolívar","Mompox","San Juan Nepomuceno",
        "Arjona","Villanueva","Córdoba","Zambrano","Barranco de Loba","Calamar","Cicuco",
        "Clemencia","El Guamo","Hatillo de Loba","Mahates","Margarita","Montecristo",
        "Morales","Norosí","Pinillos","Regidor","Río Viejo","San Cristóbal","San Estanislao",
        "San Jacinto","San Jacinto del Cauca","San Martín de Loba","San Pablo",
        "Santa Catalina","Santa Rosa","Santa Rosa del Sur","Simití","Soplaviento",
        "Talaigua Nuevo","Tiquisio","Turbaco","Turbaná","Villanueva",
    ],
    "Boyacá": [
        "Tunja","Duitama","Sogamoso","Chiquinquirá","Paipa","Villa de Leyva","Nobsa",
        "Moniquirá","Soatá","Barbosa","Belén","Boavita","Briceño","Buenavista",
        "Caldas","Campohermoso","Cerinza","Chinavita","Chivor","Ciénega","Cómbita",
        "Coper","Corrales","Covarachía","Cubará","Cucaita","Cuítiva","Chíquiza",
        "El Cocuy","El Espino","Floresta","Gachantivá","Gámeza","Garagoa","Guacamayas",
        "Guateque","Guayatá","Güicán","Iza","Jericó","Labranzagrande","La Capilla",
        "La Uvita","La Victoria","Macanal","Maripí","Miraflores","Mongua","Monguí",
        "Motavita","Muzo","Otanche","Pachavita","Páez","Panqueba","Pauna","Paya",
        "Paz de Río","Pesca","Pisba","Puerto Boyacá","Quípama","Ramiriquí","Ráquira",
        "Rondón","Saboyá","Sáchica","Samacá","San Eduardo","San José de Pare",
        "San Luis de Gaceno","San Mateo","San Miguel de Sema","San Pablo de Borbur",
        "Santana","Santa María","Santa Rosa de Viterbo","Santa Sofía","Sativanorte",
        "Sativasur","Siachoque","Socha","Socotá","Sotaquirá","Susacón","Sutamarchán",
        "Sutatenza","Tasco","Tenza","Tibaná","Tibasosa","Tinjacá","Tipacoque","Toca",
        "Togüí","Tota","Turmequé","Tuta","Tutazá","Úmbita","Ventaquemada","Viracachá",
        "Zetaquira",
    ],
    "Caldas": [
        "Manizales","La Dorada","Chinchiná","Riosucio","Salamina","Anserma","Viterbo",
        "Aguadas","Aranzazu","Belalcázar","Filadelfia","La Merced","Manzanares","Marmato",
        "Marquetalia","Marulanda","Neira","Norcasia","Pácora","Palestina","Pensilvania",
        "Riosucio","San José","Samaná","Supía","Victoria","Villamaría","Viterbo",
    ],
    "Caquetá": [
        "Florencia","San Vicente del Caguán","Puerto Rico","El Doncello","La Montañita",
        "Belén de los Andaquíes","Cartagena del Chairá","Curillo","El Paujil","Milán",
        "Morelia","San José del Fragua","Solano","Solita","Valparaíso",
    ],
    "Casanare": [
        "Yopal","Aguazul","Villanueva","Tauramena","Paz de Ariporo","Monterrey","Orocué",
        "Chameza","Hato Corozal","La Salina","Maní","Nunchía","Pore","Recetor",
        "Sabanalarga","Sácama","San Luis de Palenque","Trinidad",
    ],
    "Cauca": [
        "Popayán","Santander de Quilichao","Puerto Tejada","Corinto","Caloto","Miranda",
        "Piendamó","Cajibío","Timbío","El Tambo","Patía","Mercaderes","La Sierra",
        "Almaguer","Bolívar","Buenos Aires","Caldono","Florencia","Guachené",
        "Guapi","Inzá","Jambaló","La Vega","López","Morales","Páez","Piamonte",
        "Rosas","San Sebastián","Silvia","Sotara","Suárez","Sucre","Timbiquí",
        "Toribío","Totoró","Villa Rica",
    ],
    "Cesar": [
        "Valledupar","Aguachica","Codazzi","Bosconia","La Jagua de Ibirico","Chiriguaná",
        "Curumaní","El Copey","El Paso","Gamarra","González","La Gloria","La Paz",
        "Manaure Balcón del Cesar","Pailitas","Pelaya","Pueblo Bello","Río de Oro",
        "San Alberto","San Diego","San Martín","Tamalameque",
    ],
    "Chocó": [
        "Quibdó","Istmina","Tumaco","Condoto","Tadó","Riosucio","Acandí","Alto Baudó",
        "Atrato","Bagadó","Bahía Solano","Bajo Baudó","Bojayá","Carmen del Darién",
        "Cértegui","El Cantón del San Pablo","El Carmen de Atrato","Juradó","Litoral del San Juan",
        "Lloró","Medio Atrato","Medio Baudó","Medio San Juan","Nóvita","Nuquí",
        "Río Iró","Río Quito","Sipí","Unguía","Unión Panamericana",
    ],
    "Córdoba": [
        "Montería","Lorica","Cereté","Sahagún","Tierralta","Montelíbano","San Pelayo",
        "Ayapel","Buenavista","Canalete","Chinú","Ciénaga de Oro","Cotorra",
        "La Apartada","Moñitos","Planeta Rica","Puerto Escondido","Puerto Libertador",
        "Purísima","Ráspalco","San Andrés de Sotavento","San Antero","San Bernardo del Viento",
        "San Carlos","San José de Uré","San Marcos","San Rafael","Tuchin","Valencia",
    ],
    "Cundinamarca": [
        "Bogotá D.C.","Soacha","Chía","Cajicá","Zipaquirá","Fusagasugá","Facatativá",
        "Mosquera","Madrid","Funza","Girardot","Tocancipá","La Mesa","Sibaté",
        "Sopó","Cota","Tabio","Tenjo","Subachoque","El Rosal","Bojacá","Zipacón",
        "Anolaima","Albán","La Vega","Sasaima","Villeta","Guaduas","Puerto Salgar",
        "Gachalá","Gachetá","Gama","Guasca","Ubaté","Carmen de Carupa","Simijaca",
        "Susa","Sutatausa","Tausa","Fúquene","Cucunubá","Lenguazaque","Guachetá",
        "Nemocón","Cogua","Nemocon","Pacho","La Palma","Yacopí","Villagómez",
        "Bituima","Chaguaní","Guayabal de Síquima","San Juan de Río Seco","Beltrán",
        "Nariño","Ricaurte","Agua de Dios","Tocaima","Apulo","Tena","Anapoima",
        "Viotá","Quipile","Pulí","Jerusalén","Pandi","San Bernardo","Arbeláez",
        "Pasca","Tibacuy","Cabrera","Venecia","Silvania","Granada","Gutierrez",
        "Medina","Paratebueno","Villavicencio","Cáqueza","Chipaque","Choachí",
        "Fómeque","Quetame","Ubaque","Une","Fosca","Gutiérrez","Junín","Gachalá",
        "Ubalá","Medina","Restrepo","El Peñón","Vergara","La Peña","Útica",
        "Quebradanegra","Nimaima","Nocaima","Supatá","San Francisco","Tobia",
    ],
    "Guainía": ["Inírida","Barranco Minas","Cacahual","La Guadalupe","Mapiripana","Morichal","Pana Pana","Puerto Colombia","San Felipe"],
    "Guaviare": ["San José del Guaviare","Calamar","El Retorno","Miraflores"],
    "Huila": [
        "Neiva","Pitalito","Garzón","La Plata","Campoalegre","Palermo","Isnos","Gigante",
        "Acevedo","Agrado","Aipe","Algeciras","Altamira","Baraya","Colombia","El Pital",
        "Elías","Guadalupe","Hobo","Iquira","Isnos","La Argentina","Nátaga",
        "Oporapa","Paicol","Palermo","Palestina","Rivera","Saladoblanco","San Agustín",
        "Santa María","Suaza","Tarqui","Tello","Teruel","Tesalia","Timaná",
        "Villavieja","Yaguará",
    ],
    "La Guajira": [
        "Riohacha","Maicao","Uribia","Manaure","San Juan del Cesar","Barrancas","Albania",
        "Dibulla","Distracción","El Molino","Fonseca","Hatonuevo","La Jagua del Pilar",
        "Urumita","Villanueva",
    ],
    "Magdalena": [
        "Santa Marta","Ciénaga","Fundación","El Banco","Plato","Aracataca","Pivijay",
        "Salamina","Algarrobo","Ariguaní","Cerro San Antonio","Chibolo","Concordia",
        "El Piñón","El Retén","Guamal","Nueva Granada","Pedraza","Pijiño del Carmen",
        "Remolino","Sabanas de San Ángel","San Sebastián de Buenavista","San Zenón",
        "Santa Ana","Santa Bárbara de Pinto","Sitionuevo","Tenerife","Zapayán","Zona Bananera",
    ],
    "Meta": [
        "Villavicencio","Acacías","Granada","Puerto López","San Martín","Cumaral",
        "Restrepo","El Dorado","Barranca de Upía","Cabuyaro","Castilla la Nueva",
        "El Calvario","Fuente de Oro","La Macarena","Lejanías","Mapiripán","Mesetas",
        "Puerto Concordia","Puerto Gaitán","Puerto Lleras","Puerto Rico","San Carlos de Guaroa",
        "San Juan de Arama","San Juanito","Uribe","Vista Hermosa",
    ],
    "Nariño": [
        "Pasto","Ipiales","Tumaco","Túquerres","La Unión","Samaniego","Sandoná",
        "El Charco","Barbacoas","La Llanada","Albán","Aldana","Ancuyá","Arboleda",
        "Belén","Buesaco","Colón","Consacá","Contadero","Córdoba","Cuaspud","Cumbal",
        "Cumbitara","El Peñol","El Rosario","El Tablón de Gómez","El Tambo","Funes",
        "Guachucal","Guaitarilla","Gualmatán","Iles","Imués","La Cruz","La Florida",
        "Leiva","Linares","Los Andes","Magüí","Mallama","Mosquera","Nariño","Olaya Herrera",
        "Ospina","Policarpa","Potosí","Providencia","Puerres","Pupiales","Ricaurte",
        "Roberto Payán","San Bernardo","San Lorenzo","San Pablo","San Pedro de Cartago",
        "Santa Bárbara","Sapuyes","Taminango","Tangua","Teorama","Tola","Túquerres","Yacuanquer",
    ],
    "Norte de Santander": [
        "Cúcuta","Ocaña","Villa del Rosario","Los Patios","El Zulia","Pamplona",
        "Tibú","Ábrego","Arboledas","Bochalema","Bucarasica","Cáchira","Cácota",
        "Chinácota","Chitagá","Convención","Cucutilla","Durania","El Carmen",
        "El Tarra","Gramalote","Hacarí","Herrán","La Esperanza","La Playa",
        "Labateca","Lourdes","Mutiscua","Nortésantander","Puerto Santander","Ragonvalia",
        "Salazar","San Calixto","San Cayetano","Santiago","Sardinata","Silos",
        "Teorama","Toledo","Villa Caro","Villacaro",
    ],
    "Putumayo": [
        "Mocoa","Puerto Asís","Orito","Puerto Caicedo","Puerto Guzmán","Villagarzón",
        "Colón","Sibundoy","San Francisco","San Miguel","Valle del Guamuez",
    ],
    "Quindío": [
        "Armenia","Calarcá","Montenegro","Quimbaya","La Tebaida","Circasia","Salento",
        "Buenavista","Córdoba","Filandia","Génova","Pijao",
    ],
    "Risaralda": [
        "Pereira","Dosquebradas","Santa Rosa de Cabal","La Virginia","Quinchía",
        "Belén de Umbría","Apía","Balboa","Guática","La Celia","Marsella","Mistrató",
        "Pueblo Rico","Santuario",
    ],
    "San Andrés y Providencia": ["San Andrés","Providencia","Santa Catalina"],
    "Santander": [
        "Bucaramanga","Floridablanca","Girón","Piedecuesta","Barrancabermeja",
        "San Gil","Socorro","Málaga","Barbosa","Vélez","Zapatoca","Lebrija",
        "El Playón","Sabana de Torres","Puerto Wilches","Betulia","Bolívar",
        "Cabrera","California","Carcasí","Cepitá","Cerrito","Charalá","Charta",
        "Chimá","Chipatá","Cimitarra","Concepción","Confines","Contratación",
        "Coromoro","Curití","El Carmen de Chucurí","El Guacamayo","El Peñón",
        "Encino","Enciso","Florián","Galán","Gambita","Guacamayas","Guapotá",
        "Guavatá","Güepsa","Hato","Jesús María","Jordán","La Belleza","La Paz",
        "Landázuri","Macaravita","Matanza","Mogotes","Molagavita","Ocamonte","Oiba",
        "Onzaga","Palmar","Palmas del Socorro","Páramo","Pinchote","Puerto Parra",
        "Rionegro","San Andrés","San Benito","San Joaquín","San José de Miranda",
        "San Miguel","San Vicente de Chucurí","Santa Bárbara","Santa Helena del Opón",
        "Simacota","Suaita","Sucre","Suratá","Tona","Valle de San José","Vélez",
        "Vetas","Villanueva","Enciso",
    ],
    "Sucre": [
        "Sincelejo","Corozal","Sampués","San Marcos","Tolú","Magangué","Montería",
        "Buenavista","Caimito","Chalán","Coloso","Coveñas","El Roble","Galeras",
        "Guaranda","La Unión","Los Palmitos","Majagual","Morroa","Ovejas","Palmito",
        "Sincé","San Benito Abad","San Juan de Betulia","San Onofre","San Pedro",
        "Sucre","Tolú Viejo",
    ],
    "Tolima": [
        "Ibagué","Espinal","Melgar","Honda","Mariquita","Chaparral","Líbano","Ambalema",
        "Alpujarra","Alvarado","Anzoátegui","Ataco","Cajamarca","Carmen de Apicalá",
        "Casabianca","Coello","Coyaima","Cunday","Dolores","Falán","Flandes",
        "Fresno","Guamo","Herveo","Icononzo","Lérida","Murillo","Natagaima",
        "Ortega","Palocabildo","Piedras","Planadas","Prado","Purificación","Rioblanco",
        "Roncesvalles","Rovira","Saldaña","San Antonio","San Luis","Santa Isabel",
        "Suárez","Valle de San Juan","Venadillo","Villahermosa","Villarrica",
    ],
    "Valle del Cauca": [
        "Cali","Palmira","Buga","Buenaventura","Cartago","Jamundí","Tuluá","Yumbo",
        "Dagua","La Cumbre","Vijes","El Cerrito","Ginebra","Guacarí","San Pedro",
        "Andalucía","Bugalagrande","Zarzal","La Victoria","Obando","Ulloa","Alcalá",
        "Ansermanuevo","El Águila","El Cairo","Versalles","El Dovio","Roldanillo",
        "La Unión","Bolívar","Toro","Trujillo","Riofrio","Florida","Pradera",
        "Candelaria","El Darién","Restrepo","Calima","Caicedonia","Sevilla",
        "Argelia","El Águila",
    ],
    "Vaupés": ["Mitú","Carurú","Taraira","Papunahua","Yavaraté"],
    "Vichada": ["Puerto Carreño","La Primavera","Santa Rosalía","Cumaribo"],
}

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
    "🥇 ¡No hay límites cuando hay buena planeación y actitud!",
]

CSV_PATH = "crm_sistema_maestro.csv"

# ==========================================
# SISTEMA DE LOGIN
# ==========================================
if "correo_asesor" not in st.session_state:
    st.session_state.correo_asesor = None

if st.session_state.correo_asesor is None:
    st.title("🔐 Acceso al CRM Somos Telser")
    st.write("Selecciona tu perfil e ingresa la contraseña:")
    usuario_sel = st.selectbox("Usuario:", [
        "", "ADMIN@SOMOSTELSER.COM",
        "ASESOR1@SOMOSTELSER.COM","ASESOR2@SOMOSTELSER.COM",
        "ASESOR3@SOMOSTELSER.COM","ASESOR4@SOMOSTELSER.COM",
    ], key="select_usuario")
    password = st.text_input("Contraseña:", type="password", key="pass_input")
    if st.button("Ingresar al Portal", key="btn_login"):
        if usuario_sel == "":
            st.warning("Por favor selecciona un usuario.")
        elif password == "Telser2026":
            st.session_state.correo_asesor = usuario_sel
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")
    st.stop()

# ==========================================
# ROL
# ==========================================
es_admin = st.session_state.correo_asesor == "ADMIN@SOMOSTELSER.COM"

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    if os.path.exists("logo_somostelser.png"):
        st.image("logo_somostelser.png", use_column_width=True)
    rol_label = "👑 Admin" if es_admin else "👤 Asesor"
    st.markdown(f"**{rol_label}:** `{st.session_state.correo_asesor}`")

    # Tareas pendientes
    st.markdown("---")
    st.subheader("🔔 Tareas Pendientes")
    if os.path.exists(CSV_PATH):
        try:
            df_tasks = pd.read_csv(CSV_PATH)
            if "FECHA_SEGUIMIENTO" in df_tasks.columns:
                df_tasks["FECHA_SEGUIMIENTO"] = pd.to_datetime(df_tasks["FECHA_SEGUIMIENTO"], errors="coerce")
                hoy_ts = pd.Timestamp(date.today())
                pendientes = df_tasks[
                    (df_tasks["FECHA_SEGUIMIENTO"] <= hoy_ts) &
                    (df_tasks["ESTADO"].isin(["Cotizado","En proceso de firma"]))
                ]
                if not es_admin:
                    pendientes = pendientes[pendientes["ASESOR"] == st.session_state.correo_asesor]
                if not pendientes.empty:
                    for _, row in pendientes.iterrows():
                        st.warning(f"📞 {row['CLIENTE']} | {row.get('TIPO_SEGUIMIENTO','Seguimiento')}")
                else:
                    st.success("¡Todo al día!")
        except Exception:
            st.caption("No se pudo leer el CRM.")

    if st.button("🚪 Cerrar Sesión", key="btn_logout"):
        st.session_state.correo_asesor = None
        st.rerun()

    # Asistente de ofertas
    st.markdown("---")
    st.subheader("🤖 Asistente de Ofertas")
    consulta = st.text_input("Buscar precio:", placeholder="Ej: 500Mbps, 6.10, 60GB", key="consulta_oferta")
    if consulta:
        portafolio_total = {**PLANES_MOVIL, **PLANES_FIJO}
        resultados = {k: v for k, v in portafolio_total.items() if consulta.lower() in k.lower()}
        if resultados:
            sel_oferta = st.selectbox("Resultados:", list(resultados.keys()), key="sel_oferta")
            st.metric("Precio base (1 línea)", f"${resultados[sel_oferta]:,.0f} COP")
        else:
            st.warning("Sin resultados.")

    # Mini resumen
    st.markdown("---")
    st.subheader("📊 Resumen")
    if os.path.exists(CSV_PATH):
        try:
            df_sb = pd.read_csv(CSV_PATH)
            if not es_admin and "ASESOR" in df_sb.columns:
                df_sb = df_sb[df_sb["ASESOR"] == st.session_state.correo_asesor]
            if "VALOR_TOTAL" in df_sb.columns and not df_sb.empty:
                df_sb["VALOR_TOTAL"] = pd.to_numeric(df_sb["VALOR_TOTAL"], errors="coerce").fillna(0)
                st.metric("💰 Ingresos Totales", f"${df_sb['VALOR_TOTAL'].sum():,.0f} COP")
            if "DIVISION" in df_sb.columns and not df_sb.empty:
                st.bar_chart(df_sb["DIVISION"].value_counts())
            if es_admin and not df_sb.empty:
                st.download_button("📥 Exportar CRM",
                    data=df_sb.to_csv(index=False).encode("utf-8"),
                    file_name="CRM_Ventas_SomosTelser.csv", mime="text/csv", key="dl_sidebar")
        except Exception:
            st.caption("Cargando...")

# ==========================================
# TÍTULO
# ==========================================
st.title("📡 Portal de Ventas Somos Telser")
st.subheader("Gestión Inteligente de Contratos B2B")

# ==========================================
# PESTAÑAS
# ==========================================
nombres_tabs = ["📋 Registrar Venta", "🔄 Actualizar Estado"]
if es_admin:
    nombres_tabs.append("📊 Base de Datos")
tabs  = st.tabs(nombres_tabs)
tab1  = tabs[0]
tab2  = tabs[1]
tab3  = tabs[2] if es_admin else None

# Inicializar session_state
if "lista_lineas"   not in st.session_state: st.session_state.lista_lineas   = []
if "venta_guardada" not in st.session_state: st.session_state.venta_guardada = False

# ==========================================================
# ██  PESTAÑA 1: REGISTRAR VENTA  ██
# ==========================================================
with tab1:

    # Banner de confirmación si se acaba de guardar
    if st.session_state.venta_guardada:
        st.success("✅ Venta registrada correctamente. Puedes ingresar una nueva venta.")
        if st.button("➕ Ingresar nueva venta", key="btn_nueva_venta"):
            st.session_state.venta_guardada = False
            st.rerun()
        st.stop()

    div = st.radio("Seleccione División:", ["Móvil", "Fijo"], key="div_radio", horizontal=True)

    col_izq, col_der = st.columns(2)

    # ── COLUMNA IZQUIERDA ──────────────────────────────────
    with col_izq:
        st.subheader("🏢 Datos del Cliente")
        t_doc        = st.selectbox("Tipo Doc:", ["NIT","CV","CE","PPT"], key="t_doc")
        n_doc        = st.text_input("Número de Documento:", key="n_doc")
        nombre       = st.text_input("Razón Social o Nombre:", key="nombre")
        dir_cli      = st.text_input("Dirección:", key="dir_cli")
        barrio       = st.text_input("Barrio:", key="barrio")

        depto = st.selectbox("Departamento:", options=sorted(UBICACIONES_COL.keys()),
                             index=None, placeholder="Escribe para buscar...", key="depto")
        if depto:
            muni = st.selectbox("Municipio:", options=sorted(UBICACIONES_COL[depto]),
                                index=None, placeholder="Escribe para buscar...", key="muni_activo")
        else:
            muni = st.selectbox("Municipio:", options=[], disabled=True,
                                placeholder="Selecciona primero un departamento", key="muni_disabled")

        email_cli    = st.text_input("Email contacto:", key="email_cli")
        contacto_cli = st.text_input("Nombre contacto autorizado:", key="contacto_cli")
        tel_contacto = st.text_input("Móvil contacto autorizado:", key="tel_contacto")

        st.subheader("⚙️ Gestión Técnica")
        with st.popover("📱 Configurar Líneas Móviles (Click aquí)"):
            tipo_linea = st.radio("Tipo de gestión:",
                ["Portabilidad","Línea Nueva","Línea Existente"], key="tipo_linea_pop")
            op_linea = "N/A"
            if tipo_linea == "Portabilidad":
                op_linea = st.selectbox("Operador Origen:",
                    ["Claro","Movistar","Móvil Éxito","Wom"], key="op_linea_pop")
            cant_linea = st.number_input("Cantidad:", min_value=1, value=1, key="cant_linea_pop")
            num_linea  = st.text_input("Número de línea:", key="num_linea_pop")

            if st.button("➕ Agregar línea", key="btn_add_linea"):
                st.session_state.lista_lineas.append({
                    "cantidad": cant_linea, "tipo": tipo_linea,
                    "operador": op_linea,  "numero": num_linea,
                })
                st.success(f"✅ Línea {num_linea} agregada.")

            if st.session_state.lista_lineas:
                st.markdown("**Líneas acumuladas:**")
                for i, ln in enumerate(st.session_state.lista_lineas, 1):
                    st.write(f"{i}. {ln['tipo']} | {ln['operador']} | {ln['numero']} | x{ln['cantidad']}")
                if st.button("🗑️ Limpiar líneas", key="btn_clear_lineas"):
                    st.session_state.lista_lineas = []
                    st.rerun()
            else:
                st.info("La gestión móvil aplica también para Full Tigo.")

    # ── COLUMNA DERECHA ────────────────────────────────────
    with col_der:
        st.subheader("👤 Representante Legal")
        nom_rep  = st.text_input("Nombre Rep. Legal:", key="nom_rep")
        cc_rep   = st.text_input("Cédula Rep. Legal:", key="cc_rep")
        mail_rep = st.text_input("Correo Rep. Legal:", key="mail_rep")
        tel_rep  = st.text_input("Móvil Rep. Legal:", key="tel_rep")

        st.subheader("📊 Estado y Plan")
        estado = st.selectbox("Estado inicial:",
            ["Cotizado","En proceso de firma","Ingreso de pedido","Activado","Anulado"],
            key="estado_venta")
        bitacora = st.text_area("📝 Notas / Bitácora:", key="bitacora")
        fecha_seg = st.date_input("📅 Fecha de seguimiento:",
            value=date.today() + timedelta(days=3), key="fecha_seg")
        tipo_seg = st.selectbox("Tipo de seguimiento:",
            ["Llamada","Visita","Correo","WhatsApp"], key="tipo_seg")

        # Selección de plan según división
        if div == "Móvil":
            st.markdown("**Familia de plan:**")
            familia = st.radio("", ["Negocios 5.0","Empresarial 6.0"],
                horizontal=True, key="familia_plan")
            tarifas = PLANES_MOVIL_50 if familia == "Negocios 5.0" else PLANES_MOVIL_60
        else:
            tarifas = PLANES_FIJO
            familia = "Fijo"

        servicio = st.selectbox("Servicio:", list(tarifas.keys()), key="servicio")
        lbl_cant = "Líneas:" if div == "Móvil" else "Cantidad:"
        lineas   = st.number_input(lbl_cant, min_value=1, value=1, key="lineas")

        plan_movil_asociado = None
        if div == "Fijo" and "Full Tigo" in servicio:
            if st.checkbox("📱 ¿Incluye línea móvil adicional 6.8?", key="incluye_movil"):
                plan_movil_asociado = "Plan Datos Empresarial 6.8 FULL TIGO Ilim [6.0]"
                st.info(f"✨ Plan móvil asociado: **{plan_movil_asociado}**")

        # Cálculo financiero con escala correcta por familia
        dcto  = calcular_descuento(servicio, lineas)
        valor = tarifas[servicio] * lineas * (1 - dcto / 100)

        # Mostrar tabla de descuentos aplicable
        if div == "Móvil":
            if "[5.0]" in servicio:
                st.caption("ℹ️ Descuentos 5.0: 2L=10% · 3-5L=20% · 6-8L=25% · 9+L=30% · Portación=50% 1er mes")
            else:
                st.caption("ℹ️ Descuentos 6.0: 3-5L=13% · 6-9L=25% · 10+L=30% · Portación=50% 1er mes")

        if valor > 0:
            valor_fmt  = f"${valor:,.0f} COP"
            dcto_txt   = f"&nbsp;&nbsp;🏷️ Descuento: {dcto}%" if dcto > 0 else ""
            frase_html = random.choice(FRASES_MOTIVACION)
            html_card  = (
                '<div style="background:#e1f5fe;padding:12px;border-radius:10px;'
                'border-left:5px solid #0288d1;margin-bottom:15px;">'
                '<p style="margin:0;font-size:1.1em;color:#01579b;">'
                f'💰 <b>Total Estimado:</b> {valor_fmt} {dcto_txt}'
                '</p>'
                f'<p style="margin:5px 0 0;font-size:0.85em;"><i>{frase_html}</i></p>'
                '</div>'
            )
            st.markdown(html_card, unsafe_allow_html=True)

        st.subheader("📎 Documentos del Cliente")
        archivos_subidos = st.file_uploader("Adjuntar documentos",
            type=["pdf","png","jpg","jpeg","docx","xlsx"],
            accept_multiple_files=True, key="file_uploader")
        if archivos_subidos:
            st.success(f"📎 {len(archivos_subidos)} documento(s) seleccionado(s)")

    # ── BOTÓN GUARDAR ──────────────────────────────────────
    st.markdown("---")
    if st.button("💾 Guardar Venta", key="btn_guardar_tab1",
                 use_container_width=True, type="primary"):
        if not n_doc or not nombre:
            st.error("⚠️ Faltan datos obligatorios: Número de Documento y Razón Social.")
        else:
            # Guardar documentos adjuntos
            carpeta_docs = "documentos_clientes"
            os.makedirs(carpeta_docs, exist_ok=True)
            archivos_guardados = []
            if archivos_subidos:
                for doc in archivos_subidos:
                    ruta = os.path.join(carpeta_docs, f"{n_doc}_{doc.name}")
                    with open(ruta, "wb") as f:
                        f.write(doc.getbuffer())
                    archivos_guardados.append(f"{n_doc}_{doc.name}")

            resumen_lineas = " | ".join([
                f"{ln['tipo']}/{ln['operador']}/{ln['numero']}(x{ln['cantidad']})"
                for ln in st.session_state.lista_lineas
            ]) if st.session_state.lista_lineas else ""

            df_ex = pd.read_csv(CSV_PATH) if os.path.exists(CSV_PATH) else pd.DataFrame()

            nueva_fila = pd.DataFrame([{
                "ID_VENTA":          int(len(df_ex) + 1),
                "FECHA_REGISTRO":    str(date.today()),
                "ASESOR":            st.session_state.correo_asesor,
                "ESTADO":            estado,
                "DIVISION":          div,
                "PORTAFOLIO":        "MOVIL" if div == "Móvil" else "FIJO",
                "FAMILIA_PLAN":      familia,
                "TIPO_DOC":          t_doc,
                "NIT":               n_doc,
                "CLIENTE":           nombre,
                "DIRECCION":         dir_cli,
                "BARRIO":            barrio,
                "DEPARTAMENTO":      depto or "",
                "MUNICIPIO":         muni  or "",
                "EMAIL_CLIENTE":     email_cli,
                "CONTACTO":          contacto_cli,
                "TEL_CONTACTO":      tel_contacto,
                "REP_LEGAL":         nom_rep,
                "CC_REP":            cc_rep,
                "CORREO_REP":        mail_rep,
                "TEL_REP":           tel_rep,
                "SERVICIO":          servicio,
                "CANTIDAD_LINEAS":   int(lineas),
                "LINEAS_DETALLE":    resumen_lineas,
                "PLAN_MOVIL_ASOC":   plan_movil_asociado or "",
                "DESCUENTO_PCT":     int(dcto),
                "VALOR_TOTAL":       float(round(valor, 2)),
                "BITACORA":          bitacora,
                "FECHA_SEGUIMIENTO": str(fecha_seg),
                "TIPO_SEGUIMIENTO":  tipo_seg,
                "DOCUMENTOS":        ";".join(archivos_guardados),
                "ESTADO_FINANCIERO": "APROBADO" if valor >= 35000 else "REVISION",
            }])

            pd.concat([df_ex, nueva_fila], ignore_index=True).to_csv(CSV_PATH, index=False)

            # Notificación Telegram
            enviar_telegram(
                f"🆕 Nueva venta registrada\n━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 Asesor: {st.session_state.correo_asesor}\n"
                f"🏢 Cliente: {nombre} | NIT: {n_doc}\n"
                f"📦 Servicio: {servicio}\n"
                f"📊 Líneas: {lineas} | Descuento: {dcto}%\n"
                f"💰 Valor: ${valor:,.0f} COP\n"
                f"📌 Estado: {estado}"
            )
            ESTADOS_SEG = {
                "Cotizado": "📋 SEGUIMIENTO — Cotización enviada\n━━━━━━━━━━━━━━━━━━━━━\nHacer seguimiento para resolver dudas y avanzar al cierre.\n",
                "En proceso de firma": "✍️ SEGUIMIENTO — En proceso de firma\n━━━━━━━━━━━━━━━━━━━━━\nVerificar que no haya obstáculos para la firma.\n",
                "Anulado": "❌ ALERTA — Venta Anulada\n━━━━━━━━━━━━━━━━━━━━━\nContactar al cliente para entender el motivo.\n",
            }
            if estado in ESTADOS_SEG:
                enviar_telegram(
                    f"{ESTADOS_SEG[estado]}"
                    f"🏢 Cliente: {nombre}\n"
                    f"👤 Asesor: {st.session_state.correo_asesor}\n"
                    f"📞 Tipo seguimiento: {tipo_seg}\n"
                    f"📅 Fecha programada: {fecha_seg}"
                )

            limpiar_formulario()
            st.rerun()

# ==========================================================
# ██  PESTAÑA 2: ACTUALIZAR ESTADO  ██
# ==========================================================
with tab2:
    st.subheader("🔄 Actualizar Seguimiento de Venta")

    if not os.path.exists(CSV_PATH):
        st.info("Aún no hay base de datos. Registra tu primera venta en la pestaña anterior.")
    else:
        df_upd = pd.read_csv(CSV_PATH)

        # Red de seguridad
        for col in ["ESTADO","ID_VENTA","CLIENTE","ASESOR","SERVICIO","DIVISION","VALOR_TOTAL"]:
            if col not in df_upd.columns:
                df_upd[col] = "Sin dato" if col != "VALOR_TOTAL" else 0
        df_upd["ID_VENTA"]    = pd.to_numeric(df_upd["ID_VENTA"],    errors="coerce").fillna(0).astype(int)
        df_upd["VALOR_TOTAL"] = pd.to_numeric(df_upd["VALOR_TOTAL"], errors="coerce").fillna(0)

        df_vista = df_upd.copy() if es_admin else df_upd[df_upd["ASESOR"] == st.session_state.correo_asesor].copy()

        if df_vista.empty:
            st.warning("No tienes ventas registradas para actualizar.")
        else:
            df_vista["OPCION"] = (
                df_vista["ID_VENTA"].astype(str).str.zfill(4) + " — " +
                df_vista["CLIENTE"].astype(str) + " | " +
                df_vista["ESTADO"].astype(str)
            )
            seleccion = st.selectbox("Selecciona la venta:", df_vista["OPCION"].tolist(), key="sel_venta_tab2")

            if seleccion:
                id_sel = int(seleccion.split(" — ")[0])

                registro = df_upd[df_upd["ID_VENTA"] == id_sel]

                if registro.empty:
                    st.error(f"No se encontró la venta con ID {id_sel}.")
                    st.stop()

                fila = registro.iloc[0]

                st.markdown("---")
                ci1, ci2 = st.columns(2)
                with ci1:
                    st.info(f"📌 Estado actual: **{fila['ESTADO']}**")
                    st.write(f"**Cliente:** {fila.get('CLIENTE','N/A')}")
                    st.write(f"**Servicio:** {fila.get('SERVICIO','N/A')}")
                    st.write(f"**Líneas:** {fila.get('CANTIDAD_LINEAS','N/A')}")
                with ci2:
                    st.write(f"**Asesor:** {fila.get('ASESOR','N/A')}")
                    st.write(f"**División:** {fila.get('DIVISION','N/A')}")
                    st.write(f"**Valor:** ${float(fila.get('VALOR_TOTAL',0)):,.0f} COP")
                    st.write(f"**Seguimiento:** {fila.get('FECHA_SEGUIMIENTO','N/A')} | {fila.get('TIPO_SEGUIMIENTO','N/A')}")

                st.markdown("---")
                nuevo_estado = st.selectbox("Cambiar estado a:",
                    ["Cotizado","En proceso de firma","Ingreso de pedido","Activado","Anulado"],
                    key="sel_nuevo_estado_tab2")
                nota_adicional = st.text_area("📝 Agregar nota a la bitácora (opcional):", key="nota_tab2")

                if st.button("🔄 Guardar y Notificar", key="btn_guardar_tab2",
                             type="primary", use_container_width=True):
                    df_upd.loc[df_upd["ID_VENTA"] == id_sel, "ESTADO"] = nuevo_estado
                    if nota_adicional.strip():
                        texto_actual = str(fila.get("BITACORA",""))
                        df_upd.loc[df_upd["ID_VENTA"] == id_sel, "BITACORA"] = (
                            texto_actual + f"\n[{date.today()}] {nota_adicional.strip()}"
                        )
                    df_upd.to_csv(CSV_PATH, index=False)

                    enviar_telegram(
                        f"🔄 Venta #{str(id_sel).zfill(4)} actualizada\n━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🏢 Cliente: {fila.get('CLIENTE','N/A')}\n"
                        f"📌 Nuevo estado: {nuevo_estado}\n"
                        f"👤 Asesor: {st.session_state.correo_asesor}"
                    )
                    MENSAJES_SEG = {
                        "Cotizado": "📋 SEGUIMIENTO — Cotización enviada\n━━━━━━━━━━━━━━━━━━━━━\nHacer seguimiento para resolver dudas y avanzar al cierre.\n",
                        "En proceso de firma": "✍️ SEGUIMIENTO — En proceso de firma\n━━━━━━━━━━━━━━━━━━━━━\nVerificar que no haya obstáculos para la firma.\n",
                        "Anulado": "❌ ALERTA — Venta Anulada\n━━━━━━━━━━━━━━━━━━━━━\nContactar al cliente para entender el motivo.\n",
                    }
                    if nuevo_estado in MENSAJES_SEG:
                        enviar_telegram(
                            f"{MENSAJES_SEG[nuevo_estado]}"
                            f"🏢 Cliente: {fila.get('CLIENTE','N/A')}\n"
                            f"👤 Asesor: {st.session_state.correo_asesor}\n"
                            f"📞 Tipo seguimiento: {fila.get('TIPO_SEGUIMIENTO','N/A')}\n"
                            f"📅 Fecha programada: {fila.get('FECHA_SEGUIMIENTO','N/A')}"
                        )
                    st.success("✅ Estado actualizado y notificado correctamente.")
                    st.rerun()

# ==========================================================
# ██  PESTAÑA 3: BASE DE DATOS (solo Admin)  ██
# ==========================================================
if es_admin and tab3 is not None:
    with tab3:
        st.subheader("📊 Dashboard y Base de Datos — Vista Administrador")

        if not os.path.exists(CSV_PATH):
            st.info("Aún no hay datos registrados.")
        else:
            df = pd.read_csv(CSV_PATH)

            COLS_REQ = {
                "ESTADO":"Sin dato","ASESOR":"Sin dato","CLIENTE":"Sin dato",
                "SERVICIO":"Sin dato","VALOR_TOTAL":0,"DIVISION":"Sin dato",
                "PORTAFOLIO":"Sin dato","ID_VENTA":0,"CANTIDAD_LINEAS":0,
            }
            for col, default in COLS_REQ.items():
                if col not in df.columns:
                    df[col] = default
            df["VALOR_TOTAL"]    = pd.to_numeric(df["VALOR_TOTAL"],    errors="coerce").fillna(0)
            df["CANTIDAD_LINEAS"]= pd.to_numeric(df["CANTIDAD_LINEAS"],errors="coerce").fillna(0)
            df["ID_VENTA"]       = pd.to_numeric(df["ID_VENTA"],       errors="coerce").fillna(0).astype(int)

            if df.empty:
                st.info("La base de datos está vacía.")
            else:
                # Métricas
                m1,m2,m3,m4,m5 = st.columns(5)
                m1.metric("📁 Registros",   len(df))
                m2.metric("✅ Activadas",   len(df[df["ESTADO"].isin(["Activado","Instalado"])]))
                m3.metric("💰 Ingresos",    f"${df['VALOR_TOTAL'].sum():,.0f}")
                col_div = "PORTAFOLIO" if df["PORTAFOLIO"].isin(["FIJO","MOVIL"]).any() else "DIVISION"
                val_f   = "FIJO"  if col_div=="PORTAFOLIO" else "Fijo"
                val_m   = "MOVIL" if col_div=="PORTAFOLIO" else "Móvil"
                m4.metric("📡 Fijo",  len(df[df[col_div]==val_f]))
                m5.metric("📱 Móvil", len(df[df[col_div]==val_m]))

                st.divider()

                # Gráfico 1: Por estado
                st.markdown("#### 📈 Ventas por Estado")
                g1 = df["ESTADO"].value_counts().reset_index()
                g1.columns = ["ESTADO","CANTIDAD"]
                st.altair_chart(
                    alt.Chart(g1).mark_bar(color="#00a0e3").encode(
                        x=alt.X("ESTADO:N",sort="-y",title="Estado"),
                        y=alt.Y("CANTIDAD:Q",title="Cantidad"),
                        tooltip=["ESTADO","CANTIDAD"],
                    ).properties(height=260),
                    use_container_width=True
                )

                st.markdown("---")

                # Gráfico 2: Por asesor
                st.markdown("#### 👤 Ventas por Asesor")
                g2 = df.groupby("ASESOR")["VALOR_TOTAL"].sum().reset_index()
                g2.columns = ["ASESOR","VALOR_TOTAL"]
                st.altair_chart(
                    alt.Chart(g2).mark_bar(color="#0288d1").encode(
                        x=alt.X("ASESOR:N",sort="-y",title="Asesor"),
                        y=alt.Y("VALOR_TOTAL:Q",title="Valor Total COP"),
                        tooltip=["ASESOR","VALOR_TOTAL"],
                    ).properties(height=260),
                    use_container_width=True
                )

                st.markdown("---")

                # Análisis
                st.markdown("### 💡 Análisis y Recomendaciones")
                tasa_anul = len(df[df["ESTADO"]=="Anulado"])/len(df)*100
                ca1,ca2 = st.columns(2)
                with ca1:
                    st.markdown("**Observación:**")
                    if tasa_anul > 20:
                        st.warning(f"⚠️ Tasa de anulación alta: {tasa_anul:.1f}%. Revisar proceso de validación.")
                    else:
                        st.success(f"✅ Tasa de anulación: {tasa_anul:.1f}% — dentro del rango aceptable.")
                with ca2:
                    st.markdown("**Oportunidad:**")
                    n_f = len(df[df[col_div]==val_f])
                    n_m = len(df[df[col_div]==val_m])
                    if n_f > n_m:
                        st.write("• Portafolio **Fijo** lidera. Potenciar cross-selling hacia clientes Móviles.")
                    else:
                        st.write("• Portafolio **Móvil** lidera. Impulsar paquetes de fidelización en Fijo.")

                st.divider()

                # Tabla con filtros
                st.markdown("#### 🗃️ Base de Datos Completa")
                asesores_lista = ["Todos"] + sorted([str(a) for a in df["ASESOR"].dropna().unique().tolist()])
                fa = st.selectbox("Filtrar por asesor:", asesores_lista, key="filtro_asesor_tab3")
                df_t = df.copy() if fa=="Todos" else df[df["ASESOR"].astype(str)==fa]
                estados_disp = df["ESTADO"].dropna().unique().tolist()
                fe = st.multiselect("Filtrar por estado:", options=estados_disp,
                                    default=estados_disp, key="filtro_estado_tab3")
                if fe:
                    df_t = df_t[df_t["ESTADO"].isin(fe)]

                st.dataframe(df_t, use_container_width=True, height=400)
                st.download_button(
                    "📥 Descargar Base de Datos",
                    data=df_t.to_csv(index=False).encode("utf-8"),
                    file_name=f"CRM_SomosTelser_{date.today()}.csv",
                    mime="text/csv", key="dl_tab3",
                )
