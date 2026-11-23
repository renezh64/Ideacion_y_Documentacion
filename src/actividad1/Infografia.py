import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Infografía Inmobiliaria Colombia 2026",
    page_icon="🏠",
    layout="wide"
)

# Título principal
st.title("🏠 Infografía Interactiva: Casas vs Apartamentos en Colombia 2026")
st.markdown("Análisis de precios de oferta por m² | Dataset Aptología")

# Cargar datos (ajusta la ruta según donde guardaste el CSV enriquecido)
@st.cache_data
def cargar_datos():
    ruta = Path("datos/vivienda_colombia_enriquecido.csv")  # o la ruta relativa correcta
    if not ruta.exists():
        ruta = Path("src/actividad1/datos/vivienda_colombia_enriquecido.csv")
    df = pd.read_csv(ruta)
    return df

df = cargar_datos()

# ========== MÉTRICAS PRINCIPALES (KPIs) ==========
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Ciudades analizadas", len(df))

with col2:
    promedio_descuento = df["diferencia_pct"].mean()
    st.metric("Descuento promedio casas", f"{promedio_descuento:.1f}%")

with col3:
    ciudades_prima = (df["diferencia_pct"] > 0).sum()
    st.metric("Ciudades con prima en casas", ciudades_prima)

with col4:
    total_oferta = df["total_registros"].sum()
    st.metric("Total anuncios analizados", f"{total_oferta:,.0f}")

st.divider()

# ========== FILTROS ==========
st.sidebar.header("Filtros")
categoria = st.sidebar.multiselect(
    "Categoría de brecha",
    options=df["categoria_brecha_precio"].unique(),
    default=df["categoria_brecha_precio"].unique()
)

tipo_mercado = st.sidebar.multiselect(
    "Tipo de mercado dominante",
    options=df["tipo_mercado_dominante"].unique(),
    default=df["tipo_mercado_dominante"].unique()
)

df_filtrado = df[
    (df["categoria_brecha_precio"].isin(categoria)) &
    (df["tipo_mercado_dominante"].isin(tipo_mercado))
]

# ========== GRÁFICOS ==========
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Top 10 ciudades con mayor descuento en casas")
    top_descuento = df_filtrado.nsmallest(10, "diferencia_pct")
    fig1 = px.bar(
        top_descuento,
        x="diferencia_pct",
        y="city",
        orientation="h",
        color="diferencia_pct",
        color_continuous_scale="RdYlGn_r",
        labels={"diferencia_pct": "Diferencia %", "city": "Ciudad"}
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.subheader("Distribución de categorías de brecha")
    fig2 = px.pie(
        df_filtrado,
        names="categoria_brecha_precio",
        title="Proporción de categorías"
    )
    st.plotly_chart(fig2, use_container_width=True)

# Mapa de dispersión volumen vs precio
st.subheader("Relación entre volumen de oferta y precio por m²")
fig3 = px.scatter(
    df_filtrado,
    x="total_registros",
    y="casa_cop_m2",
    size="n_si",
    color="categoria_brecha_precio",
    hover_name="city",
    log_x=True,
    labels={
        "total_registros": "Total de registros (escala log)",
        "casa_cop_m2": "Precio m² Casa (COP)"
    }
)
st.plotly_chart(fig3, use_container_width=True)

# Tabla interactiva
st.subheader("Datos detallados")
st.dataframe(
    df_filtrado.sort_values("diferencia_pct"),
    use_container_width=True,
    hide_index=True
)

st.caption("Fuente: Dataset Aptología – Casa vs Apartamento precio m² ciudades Colombia 2026")