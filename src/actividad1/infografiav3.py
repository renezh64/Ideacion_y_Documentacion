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

st.markdown("""
<style>
    .main-title {font-size: 2.3rem !important; font-weight: 700; color: #1f2a44;}
    .stMetric {background-color: #ffffff; padding: 12px 15px; border-radius: 8px;
               box-shadow: 0 1px 3px rgba(0,0,0,0.08);}
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
            return pd.read_csv(ruta)
    st.error("No se encontró el archivo vivienda_colombia_enriquecido.csv. Ejecuta primero el notebook.")
    st.stop()

df = cargar_datos()

# Coordenadas aproximadas
coords = {
    "Bogotá": (4.7110, -74.0721), "Medellín": (6.2476, -75.5658), "Cali": (3.4516, -76.5320),
    "Barranquilla": (10.9685, -74.7813), "Cartagena": (10.3910, -75.4794),
    "Santa Marta": (11.2404, -74.1990), "Bucaramanga": (7.1254, -73.1187),
    "Pereira": (4.8133, -75.6961), "Manizales": (5.0700, -75.5200),
    "Ibagué": (4.4447, -75.2424), "Villavicencio": (4.1420, -73.6268),
    "Pasto": (1.2136, -77.2811), "Cúcuta": (7.8891, -72.4967),
    "Envigado": (6.1699, -75.5852), "Sabaneta": (6.1515, -75.6164),
    "Itagüí": (6.1715, -75.6114), "Bello": (6.3373, -75.5580),
    "Rionegro": (6.1551, -75.3740), "Chía": (4.8616, -74.0580),
    "Cajicá": (4.9173, -74.0260), "Zipaquirá": (5.0221, -74.0048),
    "Soacha": (4.5793, -74.2168), "La Calera": (4.7190, -73.9670),
    "Tocancipá": (4.9660, -73.9110), "Puerto Colombia": (10.9930, -74.9540),
    "Palmira": (3.5394, -76.3036), "El Carmen de Viboral": (6.0830, -75.3330),
    "Piedecuesta": (6.9880, -73.0500), "Jamundí": (3.2600, -76.5400),
    "Yumbo": (3.5850, -76.4950), "Guarne": (6.2800, -75.4400),
    "Marinilla": (6.1730, -75.3360), "San Antonio de Pereira": (6.1600, -75.4800),
}

df["lat"] = df["city"].map(lambda x: coords.get(x, (None, None))[0])
df["lon"] = df["city"].map(lambda x: coords.get(x, (None, None))[1])

# ====================== DEFINICIÓN DE REGIONES ======================
regiones = {
    "Valle de Aburrá": ["Medellín", "Envigado", "Sabaneta", "Itagüí", "Bello"],
    "Sabana de Bogotá": ["Bogotá", "Chía", "Cajicá", "Zipaquirá", "Soacha", "La Calera", "Tocancipá"],
    "Valle de San Nicolás": ["Rionegro", "Guarne", "Marinilla", "San Antonio de Pereira", "El Carmen de Viboral"],
    "Área Metropolitana Suroccidente": ["Cali", "Jamundí", "Yumbo", "Palmira"]
}

def asignar_region(ciudad):
    for region, ciudades in regiones.items():
        if ciudad in ciudades:
            return region
    return "Otra"

df["region"] = df["city"].apply(asignar_region)

# ====================== SIDEBAR ======================
st.sidebar.title("Filtros")
categorias = st.sidebar.multiselect(
    "Categoría de brecha",
    options=sorted(df["categoria_brecha_precio"].unique()),
    default=sorted(df["categoria_brecha_precio"].unique())
)
tipos = st.sidebar.multiselect(
    "Tipo de mercado",
    options=sorted(df["tipo_mercado_dominante"].unique()),
    default=sorted(df["tipo_mercado_dominante"].unique())
)
min_oferta = st.sidebar.slider("Volumen mínimo de oferta", 0, int(df["total_registros"].max()), 0, 100)

df_f = df[
    (df["categoria_brecha_precio"].isin(categorias)) &
    (df["tipo_mercado_dominante"].isin(tipos)) &
    (df["total_registros"] >= min_oferta)
].copy()

# ====================== ENCABEZADO ======================
st.markdown('<p class="main-title">🏠 Infografía Interactiva: Casas vs Apartamentos – Colombia 2026</p>', unsafe_allow_html=True)
st.caption("Análisis enriquecido | Comparación de áreas metropolitanas")

# ====================== KPIs GENERALES ======================
st.subheader("Indicadores generales (datos filtrados)")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Ciudades", len(df_f))
c2.metric("Descuento promedio", f"{df_f['diferencia_pct'].mean():.1f}%")
c3.metric("Ciudades con prima", int((df_f["diferencia_pct"] > 0).sum()))
c4.metric("Oferta total", f"{df_f['total_registros'].sum():,.0f}")
c5.metric("Mayor descuento", f"{df_f['diferencia_pct'].min():.1f}%")

st.divider()

# ====================== SECCIÓN: COMPARACIÓN REGIONAL ======================
st.header("Comparación de Áreas Metropolitanas / Regiones")

# Filtrar solo las 4 regiones de interés
df_regiones = df_f[df_f["region"].isin(regiones.keys())].copy()

if df_regiones.empty:
    st.warning("No hay datos disponibles para las regiones seleccionadas con los filtros actuales.")
else:
    # ---- Resumen por región ----
    resumen = df_regiones.groupby("region").agg(
        ciudades=("city", "count"),
        oferta_total=("total_registros", "sum"),
        precio_casa_promedio=("casa_cop_m2", "mean"),
        precio_apto_promedio=("apto_cop_m2", "mean"),
        diferencia_promedio=("diferencia_pct", "mean"),
        ciudades_con_prima=("diferencia_pct", lambda x: (x > 0).sum())
    ).reset_index()

    st.subheader("Resumen comparativo por región")
    st.dataframe(
        resumen.style.format({
            "oferta_total": "{:,.0f}",
            "precio_casa_promedio": "${:,.0f}",
            "precio_apto_promedio": "${:,.0f}",
            "diferencia_promedio": "{:.1f}%"
        }),
        use_container_width=True,
        hide_index=True
    )

    # ---- Gráficos de comparación ----
    col1, col2 = st.columns(2)

    with col1:
        fig_diff = px.bar(
            resumen,
            x="region",
            y="diferencia_promedio",
            color="diferencia_promedio",
            color_continuous_scale="RdYlGn_r",
            text="diferencia_promedio",
            title="Diferencia porcentual promedio (Casa vs Apto)",
            labels={"diferencia_promedio": "Diferencia %", "region": ""}
        )
        fig_diff.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_diff.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig_diff, use_container_width=True)

    with col2:
        fig_oferta = px.bar(
            resumen,
            x="region",
            y="oferta_total",
            color="oferta_total",
            color_continuous_scale="Blues",
            text="oferta_total",
            title="Volumen total de oferta por región",
            labels={"oferta_total": "Total anuncios", "region": ""}
        )
        fig_oferta.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_oferta.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig_oferta, use_container_width=True)

    # Precios promedio lado a lado
    st.subheader("Precio promedio por m² – Casas vs Apartamentos")
    fig_precios = go.Figure()
    fig_precios.add_trace(go.Bar(
        name="Casas",
        x=resumen["region"],
        y=resumen["precio_casa_promedio"],
        text=resumen["precio_casa_promedio"],
        texttemplate="$%{text:,.0f}",
        textposition="outside"
    ))
    fig_precios.add_trace(go.Bar(
        name="Apartamentos",
        x=resumen["region"],
        y=resumen["precio_apto_promedio"],
        text=resumen["precio_apto_promedio"],
        texttemplate="$%{text:,.0f}",
        textposition="outside"
    ))
    fig_precios.update_layout(
        barmode="group",
        height=450,
        yaxis_title="Precio por m² (COP)",
        legend_title=""
    )
    st.plotly_chart(fig_precios, use_container_width=True)

    # Detalle de ciudades por región
    st.subheader("Detalle de ciudades por región")
    region_seleccionada = st.selectbox(
        "Selecciona una región para ver sus ciudades:",
        options=list(regiones.keys())
    )
    detalle = df_regiones[df_regiones["region"] == region_seleccionada].sort_values("diferencia_pct")
    st.dataframe(
        detalle[[
            "city", "n_si", "n_no", "total_registros",
            "casa_cop_m2", "apto_cop_m2", "diferencia_pct",
            "categoria_brecha_precio", "tipo_mercado_dominante"
        ]],
        use_container_width=True,
        hide_index=True
    )   

st.divider()

# ====================== RESTO DE LA INFOGRAFÍA (Top descuentos, mapa, etc.) ======================
st.header("Vista general del mercado")

col_a, col_b = st.columns([1.3, 1])

with col_a:
    st.subheader("Top 12 ciudades con mayor descuento en casas")
    top = df_f.nsmallest(12, "diferencia_pct")
    fig_bar = px.bar(
        top, x="diferencia_pct", y="city", orientation="h",
        color="diferencia_pct", color_continuous_scale="RdYlGn_r",
        text="diferencia_pct", labels={"diferencia_pct": "Diferencia %", "city": ""}
    )
    fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_bar.update_layout(height=480, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_b:
    st.subheader("Distribución de categorías")
    fig_pie = px.pie(df_f, names="categoria_brecha_precio", hole=0.45)
    fig_pie.update_layout(height=480)
    st.plotly_chart(fig_pie, use_container_width=True)

# Mapa
st.subheader("Mapa de ciudades")
df_mapa = df_f.dropna(subset=["lat", "lon"])
if not df_mapa.empty:
    fig_map = px.scatter_mapbox(
        df_mapa, lat="lat", lon="lon", size="total_registros",
        color="diferencia_pct", color_continuous_scale="RdYlGn_r",
        hover_name="city", size_max=35, zoom=5,
        mapbox_style="carto-positron",
        hover_data={"casa_cop_m2": ":,.0f", "apto_cop_m2": ":,.0f", "diferencia_pct": ":.1f", "lat": False, "lon": False}
    )
    fig_map.update_layout(height=520, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

st.divider()
st.caption("Fuente: Dataset Aptología – Casa vs Apartamento precio m² ciudades Colombia 2026")
st.caption("Dashboard: Streamlit + Plotly | Proyecto de Ideación y Documentación")