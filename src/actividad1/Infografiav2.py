import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np

# ====================== CONFIGURACIÓN DE PÁGINA ======================
st.set_page_config(
    page_title="Infografía Inmobiliaria Colombia 2026",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS ligero para mejorar la apariencia
st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem !important;
        font-weight: 700;
        color: #1f2a44;
    }
    .kpi-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #0d6efd;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 10px 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

# ====================== CARGA DE DATOS ======================
@st.cache_data
def cargar_datos():
    posibles_rutas = [
        Path("datos/vivienda_colombia_enriquecido.csv"),
        Path("src/actividad1/datos/vivienda_colombia_enriquecido.csv"),
        Path("../datos/vivienda_colombia_enriquecido.csv"),
    ]
    for ruta in posibles_rutas:
        if ruta.exists():
            df = pd.read_csv(ruta)
            return df
    st.error("No se encontró el archivo vivienda_colombia_enriquecido.csv. Ejecuta primero el notebook.")
    st.stop()

df = cargar_datos()

# Coordenadas aproximadas de las principales ciudades (para el mapa)
coords = {
    "Bogotá": (4.7110, -74.0721),
    "Medellín": (6.2476, -75.5658),
    "Cali": (3.4516, -76.5320),
    "Barranquilla": (10.9685, -74.7813),
    "Cartagena": (10.3910, -75.4794),
    "Santa Marta": (11.2404, -74.1990),
    "Bucaramanga": (7.1254, -73.1187),
    "Pereira": (4.8133, -75.6961),
    "Manizales": (5.0700, -75.5200),
    "Ibagué": (4.4447, -75.2424),
    "Villavicencio": (4.1420, -73.6268),
    "Pasto": (1.2136, -77.2811),
    "Cúcuta": (7.8891, -72.4967),
    "Envigado": (6.1699, -75.5852),
    "Sabaneta": (6.1515, -75.6164),
    "Itagüí": (6.1715, -75.6114),
    "Bello": (6.3373, -75.5580),
    "Rionegro": (6.1551, -75.3740),
    "Chía": (4.8616, -74.0580),
    "Cajicá": (4.9173, -74.0260),
    "Zipaquirá": (5.0221, -74.0048),
    "Soacha": (4.5793, -74.2168),
    "La Calera": (4.7190, -73.9670),
    "Tocancipá": (4.9660, -73.9110),
    "Puerto Colombia": (10.9930, -74.9540),
    "Palmira": (3.5394, -76.3036),
    "El Carmen de Viboral": (6.0830, -75.3330),
    "Piedecuesta": (6.9880, -73.0500),
}

df["lat"] = df["city"].map(lambda x: coords.get(x, (None, None))[0])
df["lon"] = df["city"].map(lambda x: coords.get(x, (None, None))[1])

# ====================== SIDEBAR (FILTROS) ======================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/235/235861.png", width=70)
st.sidebar.title("Filtros de la Infografía")

categorias = st.sidebar.multiselect(
    "Categoría de brecha de precio",
    options=sorted(df["categoria_brecha_precio"].unique()),
    default=sorted(df["categoria_brecha_precio"].unique())
)

tipos = st.sidebar.multiselect(
    "Tipo de mercado dominante",
    options=sorted(df["tipo_mercado_dominante"].unique()),
    default=sorted(df["tipo_mercado_dominante"].unique())
)

min_oferta = st.sidebar.slider(
    "Volumen mínimo de oferta",
    min_value=0,
    max_value=int(df["total_registros"].max()),
    value=0,
    step=100
)

df_f = df[
    (df["categoria_brecha_precio"].isin(categorias)) &
    (df["tipo_mercado_dominante"].isin(tipos)) &
    (df["total_registros"] >= min_oferta)
].copy()

# ====================== ENCABEZADO ======================
st.markdown('<p class="main-title">🏠 Infografía Interactiva: Casas vs Apartamentos en Colombia 2026</p>', unsafe_allow_html=True)
st.caption("Precios de oferta por m² | Dataset: Aptología | Análisis enriquecido desde Jupyter")

# ====================== KPIs PRINCIPALES ======================
st.subheader("Indicadores clave")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Ciudades", len(df_f))

with col2:
    st.metric("Descuento promedio", f"{df_f['diferencia_pct'].mean():.1f}%")

with col3:
    st.metric("Ciudades con prima", int((df_f["diferencia_pct"] > 0).sum()))

with col4:
    st.metric("Oferta total", f"{df_f['total_registros'].sum():,.0f}")

with col5:
    st.metric("Mayor descuento", f"{df_f['diferencia_pct'].min():.1f}%")

st.divider()

# ====================== FILA 1: TOP DESCUENTOS + DISTRIBUCIÓN ======================
col_a, col_b = st.columns([1.3, 1])

with col_a:
    st.subheader("Top 12 ciudades con mayor descuento en casas")
    top = df_f.nsmallest(12, "diferencia_pct")
    fig_bar = px.bar(
        top,
        x="diferencia_pct",
        y="city",
        orientation="h",
        color="diferencia_pct",
        color_continuous_scale="RdYlGn_r",
        text="diferencia_pct",
        labels={"diferencia_pct": "Diferencia %", "city": ""}
    )
    fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_bar.update_layout(height=480, showlegend=False, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_bar, use_container_width=True)

with col_b:
    st.subheader("Distribución de categorías")
    fig_pie = px.pie(
        df_f,
        names="categoria_brecha_precio",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_pie.update_layout(height=480, margin=dict(t=30, b=10))
    st.plotly_chart(fig_pie, use_container_width=True)

# ====================== FILA 2: MAPA + SCATTER ======================
st.subheader("Mapa de ciudades y relación Volumen vs Precio")

col_c, col_d = st.columns(2)

with col_c:
    df_mapa = df_f.dropna(subset=["lat", "lon"])
    if not df_mapa.empty:
        fig_map = px.scatter_mapbox(
            df_mapa,
            lat="lat",
            lon="lon",
            size="total_registros",
            color="diferencia_pct",
            color_continuous_scale="RdYlGn_r",
            hover_name="city",
            hover_data={
                "casa_cop_m2": ":,.0f",
                "apto_cop_m2": ":,.0f",
                "diferencia_pct": ":.1f",
                "total_registros": True,
                "lat": False,
                "lon": False
            },
            size_max=35,
            zoom=4.5,
            mapbox_style="carto-positron",
            title="Ubicación y magnitud del descuento/prima"
        )
        fig_map.update_layout(height=500, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No hay coordenadas disponibles para las ciudades filtradas.")

with col_d:
    fig_scatter = px.scatter(
        df_f,
        x="total_registros",
        y="casa_cop_m2",
        size="n_si",
        color="categoria_brecha_precio",
        hover_name="city",
        log_x=True,
        size_max=40,
        labels={
            "total_registros": "Volumen de oferta (log)",
            "casa_cop_m2": "Precio m² Casa (COP)"
        },
        title="Volumen de oferta vs Precio de casas"
    )
    fig_scatter.update_layout(height=500, margin=dict(t=40, b=10))
    st.plotly_chart(fig_scatter, use_container_width=True)

# ====================== TABLA DETALLADA ======================
st.subheader("Tabla completa de datos filtrados")
st.dataframe(
    df_f.sort_values("diferencia_pct")[[
        "city", "n_si", "n_no", "total_registros",
        "casa_cop_m2", "apto_cop_m2", "diferencia_pct",
        "categoria_brecha_precio", "tipo_mercado_dominante"
    ]],
    use_container_width=True,
    hide_index=True,
    height=400
)

# ====================== PIE DE PÁGINA ======================
st.divider()
st.caption("Fuente: Dataset Aptología – Casa vs Apartamento precio m² ciudades Colombia 2026 | Elaborado a partir del notebook Actividad3.ipynb")
st.caption("Dashboard generado con Streamlit + Plotly | Proyecto de Ideación y Documentación")