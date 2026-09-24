from __future__ import annotations

import datetime as dt
import io
import re
import time
import unicodedata
from pathlib import Path
from typing import Iterable

import pandas as pd
import streamlit as st
from pydataxm.pydataxm import ReadDB

APP_DIR = Path(__file__).resolve().parent
CATALOG_PATH = APP_DIR / "Consulta_API_XM.xlsm"
LOGO_PATH = APP_DIR / "logo.png"

st.set_page_config(
    page_title="VisorXM | Descarga de datos XM",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Estilo
# -----------------------------
st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1450px;}
    [data-testid="stSidebar"] {border-right: 1px solid rgba(120,120,120,.15);}
    .vx-title {font-size: 2.15rem; font-weight: 750; margin: 0; letter-spacing: -.03em;}
    .vx-subtitle {opacity: .76; margin-top: .15rem; margin-bottom: 1rem;}
    .vx-card {border: 1px solid rgba(120,120,120,.20); border-radius: 14px; padding: 1rem 1.1rem; margin: .4rem 0 1rem 0;}
    .vx-step {font-size: .78rem; text-transform: uppercase; letter-spacing: .08em; opacity: .60; font-weight: 700;}
    .vx-variable {font-size: 1.15rem; font-weight: 700; margin-top: .2rem;}
    .vx-meta {font-size: .88rem; opacity: .72;}
    .stDownloadButton button {font-weight: 700;}
    div[data-testid="stMetric"] {border: 1px solid rgba(120,120,120,.18); padding: .8rem; border-radius: 12px;}
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Utilidades
# -----------------------------
def normalize_text(value: object) -> str:
    text = str(value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", text)


def slugify(value: object) -> str:
    text = normalize_text(value)
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text[:90] or "datos_xm"


def category_for(name: str) -> str:
    s = normalize_text(name)
    rules = [
        ("Demanda", ["demanda", "dema"]),
        ("Generación", ["generacion", "gene", "cogener", "autogener"]),
        ("Precios y mercado", ["precio", "bolsa", "cargo", "cere", "cee", "contrato", "oferta"]),
        ("Hidrología y embalses", ["aporte", "embalse", "volumen", "vertimiento", "caudal", "hidro"]),
        ("Disponibilidad y capacidad", ["disponibilidad", "capacidad", "mantenimiento", "indispon"]),
        ("Restricciones y seguridad", ["restric", "seguridad", "desviacion", "redespacho"]),
        ("Intercambios y red", ["intercambio", "export", "import", "frontera", "perdida", "stn", "str"]),
    ]
    for category, keys in rules:
        if any(key in s for key in keys):
            return category
    return "Otros"


def display_name(row: pd.Series) -> str:
    name = str(row.get("Nombre Variable", "")).strip()
    entity = str(row.get("Granularidad", "")).strip()
    return f"{name}  ·  {entity}" if entity else name


def max_days(row: pd.Series) -> int:
    raw = row.get("Máximo Días", 31)
    try:
        value = int(float(raw))
        return max(1, value)
    except Exception:
        return 31


@st.cache_data(show_spinner=False)
def load_catalog() -> pd.DataFrame:
    df = pd.read_excel(CATALOG_PATH, sheet_name="Parametros")
    df = df.dropna(how="all").copy()
    required = ["Nombre Variable", "Código API", "Granularidad"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"El catálogo XM no contiene las columnas esperadas: {missing}")
    df["Categoría"] = df["Nombre Variable"].map(category_for)
    df["_search"] = (
        df.fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
        .map(normalize_text)
    )
    return df


def date_chunks(start: dt.date, end: dt.date, days: int) -> Iterable[tuple[dt.date, dt.date]]:
    current = start
    while current <= end:
        chunk_end = min(end, current + dt.timedelta(days=days - 1))
        yield current, chunk_end
        current = chunk_end + dt.timedelta(days=1)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_xm_cached(
    metric_id: str,
    entity: str,
    start_iso: str,
    end_iso: str,
    limit_days: int,
) -> pd.DataFrame:
    start = dt.date.fromisoformat(start_iso)
    end = dt.date.fromisoformat(end_iso)
    client = ReadDB()
    frames: list[pd.DataFrame] = []

    # Para listas, ReadDB ignora las fechas; basta una llamada.
    if normalize_text(entity).startswith("lists"):
        return client.request_data(metric_id, entity, start, end)

    for chunk_start, chunk_end in date_chunks(start, end, limit_days):
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                frame = client.request_data(metric_id, entity, chunk_start, chunk_end)
                if frame is not None and not frame.empty:
                    frames.append(frame)
                last_error = None
                break
            except Exception as exc:  # reintentos ante fallos temporales
                last_error = exc
                time.sleep(0.7 * (attempt + 1))
        if last_error is not None:
            raise RuntimeError(
                f"XM no respondió correctamente para {chunk_start} a {chunk_end}: {last_error}"
            ) from last_error

    if not frames:
        return pd.DataFrame()

    result = pd.concat(frames, ignore_index=True)
    return result.drop_duplicates().reset_index(drop=True)


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Filtros simples post-consulta para columnas útiles y de cardinalidad razonable."""
    out = df.copy()
    candidate_cols = []
    for col in out.columns:
        nunique = out[col].nunique(dropna=True)
        if 1 < nunique <= 150 and not pd.api.types.is_float_dtype(out[col]):
            candidate_cols.append(col)

    if not candidate_cols:
        return out

    with st.expander("Filtrar resultados antes de descargar", expanded=False):
        selected_cols = st.multiselect(
            "Columnas para filtrar",
            candidate_cols,
            placeholder="Ej. Name, Code, agente, recurso...",
        )
        for col in selected_cols:
            values = sorted(out[col].dropna().astype(str).unique().tolist())
            selected = st.multiselect(f"{col}", values, key=f"flt_{slugify(col)}")
            if selected:
                out = out[out[col].astype(str).isin(selected)]
    return out


def find_date_column(df: pd.DataFrame) -> str | None:
    for col in df.columns:
        if normalize_text(col) in {"date", "fecha", "datetime"}:
            return col
    for col in df.columns:
        if "date" in normalize_text(col) or "fecha" in normalize_text(col):
            return col
    return None


def excel_bytes(df: pd.DataFrame, metadata: dict[str, object]) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Datos", index=False)
        pd.DataFrame(
            [{"Campo": key, "Valor": str(value)} for key, value in metadata.items()]
        ).to_excel(writer, sheet_name="Metadatos", index=False)
    return output.getvalue()


def csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def quick_variables(catalog: pd.DataFrame) -> list[str]:
    preferred = [
        "Demanda Energia SIN por Sistema",
        "Demanda Real por Sistema",
        "Generación por Sistema",
        "Generación por Recurso",
        "Precio Bolsa Nacional por Sistema",
        "Precio Bolsa Nacional Ponderado por Sistema",
        "Volumen Útil  diario % por Embalse",
        "Aportes  Energía por Sistema",
        "Disponibilidad Real por Recurso",
    ]
    existing = set(catalog["Nombre Variable"].astype(str))
    return [name for name in preferred if name in existing]


# -----------------------------
# Header / navegación
# -----------------------------
header_a, header_b = st.columns([1, 8], vertical_alignment="center")
with header_a:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=74)
with header_b:
    st.markdown('<div class="vx-title">VisorXM</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="vx-subtitle">Encuentra, consulta y descarga datos públicos de XM sin trabajar directamente con la API.</div>',
        unsafe_allow_html=True,
    )

try:
    catalog = load_catalog()
except Exception as exc:
    st.error(f"No fue posible cargar el catálogo de variables: {exc}")
    st.stop()

with st.sidebar:
    st.markdown("### VisorXM")
    page = st.radio("Navegación", ["Descargar datos", "Catálogo XM", "Ayuda"], label_visibility="collapsed")
    st.divider()
    st.caption(f"{len(catalog):,} variables disponibles en el catálogo local.")
    st.caption("Fuente: API pública XM / Sinergox.")


# -----------------------------
# Página principal
# -----------------------------
if page == "Descargar datos":
    st.markdown('<div class="vx-step">Paso 1 · Elige la información</div>', unsafe_allow_html=True)

    col_search, col_category = st.columns([2.2, 1])
    with col_search:
        query = st.text_input(
            "¿Qué dato necesitas?",
            placeholder="Ej. demanda, precio de bolsa, generación, embalses, recurso...",
        )
    with col_category:
        categories = ["Todas"] + sorted(catalog["Categoría"].unique().tolist())
        category = st.selectbox("Categoría", categories)

    filtered_catalog = catalog.copy()
    if category != "Todas":
        filtered_catalog = filtered_catalog[filtered_catalog["Categoría"] == category]
    if query.strip():
        terms = [normalize_text(t) for t in query.split() if t.strip()]
        if terms:
            mask = pd.Series(True, index=filtered_catalog.index)
            for term in terms:
                mask &= filtered_catalog["_search"].str.contains(re.escape(term), na=False)
            filtered_catalog = filtered_catalog[mask]

    quick = quick_variables(catalog)
    if not query and category == "Todas" and quick:
        quick_choice = st.selectbox(
            "Accesos rápidos",
            ["— Elegir desde todo el catálogo —"] + quick,
            help="Variables de consulta frecuente. También puedes buscar cualquier otra de XM.",
        )
        if quick_choice != "— Elegir desde todo el catálogo —":
            filtered_catalog = catalog[catalog["Nombre Variable"] == quick_choice]

    if filtered_catalog.empty:
        st.warning("No encontré variables con esos términos. Prueba una búsqueda más general.")
        st.stop()

    options = filtered_catalog.index.tolist()
    selected_index = st.selectbox(
        "Variable XM",
        options,
        format_func=lambda i: display_name(filtered_catalog.loc[i]),
        help=f"Coincidencias encontradas: {len(filtered_catalog)}",
    )
    row = catalog.loc[selected_index]

    metric_id = str(row["Código API"]).strip()
    entity = str(row["Granularidad"]).strip()
    variable_name = str(row["Nombre Variable"]).strip()
    desaggregation = str(row.get("Desagregación", "")).strip()
    limit_days = max_days(row)

    st.markdown(
        f"""
        <div class="vx-card">
          <div class="vx-variable">{variable_name}</div>
          <div class="vx-meta">Nivel: {desaggregation or 'No especificado'} · Frecuencia/entidad: {entity}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Ver detalles técnicos de XM"):
        c1, c2, c3 = st.columns(3)
        c1.code(metric_id, language=None)
        c1.caption("Código API")
        c2.code(entity, language=None)
        c2.caption("Entidad")
        c3.code(str(limit_days), language=None)
        c3.caption("Máximo días por llamada")

    st.markdown('<div class="vx-step">Paso 2 · Selecciona el período</div>', unsafe_allow_html=True)
    today = dt.date.today()
    default_end = today
    default_start = today - dt.timedelta(days=30)

    d1, d2 = st.columns(2)
    with d1:
        start_date = st.date_input("Desde", value=default_start, format="YYYY-MM-DD")
    with d2:
        end_date = st.date_input("Hasta", value=default_end, format="YYYY-MM-DD")

    if start_date > end_date:
        st.error("La fecha inicial debe ser anterior o igual a la fecha final.")
        st.stop()

    requested_days = (end_date - start_date).days + 1
    if requested_days > limit_days:
        calls = (requested_days + limit_days - 1) // limit_days
        st.caption(
            f"VisorXM dividirá automáticamente este período en aproximadamente {calls} consultas a XM y unirá el resultado."
        )

    st.markdown('<div class="vx-step">Paso 3 · Consulta</div>', unsafe_allow_html=True)
    run = st.button("Consultar datos XM", type="primary", use_container_width=True)

    if run:
        try:
            with st.spinner("Consultando XM y consolidando la información..."):
                result = fetch_xm_cached(
                    metric_id,
                    entity,
                    start_date.isoformat(),
                    end_date.isoformat(),
                    limit_days,
                )
            st.session_state["vx_result"] = result
            st.session_state["vx_meta"] = {
                "Variable": variable_name,
                "Código API": metric_id,
                "Entidad": entity,
                "Desagregación": desaggregation,
                "Fecha inicial": start_date,
                "Fecha final": end_date,
                "Fecha de descarga": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Fuente": "API pública XM / Sinergox",
            }
        except Exception as exc:
            st.error(f"No fue posible completar la consulta: {exc}")

    result = st.session_state.get("vx_result")
    metadata = st.session_state.get("vx_meta")

    if isinstance(result, pd.DataFrame):
        if result.empty:
            st.warning("XM no devolvió registros para la variable y el período seleccionados.")
        else:
            st.divider()
            st.markdown('<div class="vx-step">Paso 4 · Revisa y descarga</div>', unsafe_allow_html=True)

            filtered_result = filter_dataframe(result)
            date_col = find_date_column(filtered_result)

            m1, m2, m3 = st.columns(3)
            m1.metric("Registros", f"{len(filtered_result):,}")
            m2.metric("Columnas", f"{filtered_result.shape[1]:,}")
            if date_col and not filtered_result.empty:
                dates = pd.to_datetime(filtered_result[date_col], errors="coerce").dropna()
                if not dates.empty:
                    m3.metric("Cobertura", f"{dates.min().date()} → {dates.max().date()}")
                else:
                    m3.metric("Cobertura", "Según consulta")
            else:
                m3.metric("Cobertura", "Según consulta")

            tab_preview, tab_chart = st.tabs(["Vista previa", "Gráfica rápida"])
            with tab_preview:
                st.dataframe(filtered_result.head(3000), use_container_width=True, height=480)
                if len(filtered_result) > 3000:
                    st.caption("La vista previa muestra 3.000 filas; la descarga incluye todos los registros filtrados.")

            with tab_chart:
                numeric = filtered_result.select_dtypes(include="number").columns.tolist()
                if date_col and numeric:
                    y = st.selectbox("Serie", numeric)
                    plot_df = filtered_result[[date_col, y]].copy()
                    plot_df[date_col] = pd.to_datetime(plot_df[date_col], errors="coerce")
                    plot_df = plot_df.dropna(subset=[date_col]).set_index(date_col)
                    st.line_chart(plot_df[y])
                else:
                    st.info("Esta consulta no tiene una combinación fecha + columna numérica adecuada para una vista rápida.")

            safe_meta = metadata or {}
            file_base = f"XM_{slugify(safe_meta.get('Variable', variable_name))}_{safe_meta.get('Fecha inicial', start_date)}_{safe_meta.get('Fecha final', end_date)}"
            download_a, download_b = st.columns(2)
            with download_a:
                st.download_button(
                    "⬇ Descargar Excel",
                    data=excel_bytes(filtered_result, safe_meta),
                    file_name=f"{file_base}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True,
                )
            with download_b:
                st.download_button(
                    "⬇ Descargar CSV",
                    data=csv_bytes(filtered_result),
                    file_name=f"{file_base}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            st.caption("El Excel incluye una hoja **Metadatos** con la variable, código XM, período y fuente de la consulta.")

elif page == "Catálogo XM":
    st.subheader("Catálogo de variables XM")
    st.write("Explora las variables disponibles sin necesidad de conocer sus códigos de API.")
    q = st.text_input("Buscar en el catálogo", placeholder="Escribe nombre, código, entidad o palabra clave...")
    view = catalog.copy()
    if q.strip():
        terms = [normalize_text(t) for t in q.split() if t.strip()]
        for term in terms:
            view = view[view["_search"].str.contains(re.escape(term), na=False)]
    shown = [c for c in ["Categoría", "Nombre Variable", "Código API", "Granularidad", "Desagregación", "Máximo Días"] if c in view.columns]
    st.caption(f"{len(view)} resultados")
    st.dataframe(view[shown].reset_index(drop=True), use_container_width=True, height=650)

else:
    st.subheader("Cómo usar VisorXM")
    st.markdown(
        """
        **VisorXM está pensado para que la consulta sea simple:**

        1. Busca el dato en lenguaje normal, por ejemplo **demanda**, **precio de bolsa**, **generación** o **embalses**.
        2. Selecciona la variable XM que necesitas.
        3. Define el período. Si XM limita el número de días por consulta, VisorXM divide y consolida el rango automáticamente.
        4. Consulta, revisa una vista previa, aplica filtros opcionales y descarga en **Excel** o **CSV**.

        Los códigos internos de la API quedan disponibles en un panel técnico, pero no necesitas conocerlos para usar la herramienta.
        """
    )
    st.info("VisorXM es una herramienta independiente basada en datos públicos de XM. No es un producto oficial de XM S.A. E.S.P.")
