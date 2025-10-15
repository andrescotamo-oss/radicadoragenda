
import streamlit as st
import pandas as pd
import io, requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

def to_direct_download(url: str) -> str:
    try:
        u = url.strip()
        low = u.lower()
        if "onedrive.live.com" in low:
            if "redir" in low:
                u = u.replace("redir", "download")
            if "download=" not in low and "?" in u:
                u = u + "&download=1"
            elif "download=" not in low and "?" not in u:
                u = u + "?download=1"
            return u
        if "sharepoint.com" in low:
            if "download=1" not in low:
                if "?" in u:
                    u = u + "&download=1"
                else:
                    u = u + "?download=1"
            return u
        if "1drv.ms" in low:
            return u
        return url
    except Exception:
        return url

st.set_page_config(page_title="Agenda ↔ Radicador (Streamlit)", layout="wide")
st.title("AGENDA VIRTUAL ↔ LIBRO RADICADOR — J14 Penal")

st.markdown("""Esta app cruza **AGENDA VIRTUAL** (columna **C = R. INTERNO**) con el **LIBRO RADICADOR** (*PROCESOS 1 INSTANCIA PENAL*, **RADICADO INTERNO**).
- Tooltip en **R. INTERNO**: **Procesado + Delito + Etapa**.
- Selecciona una fila para ver el panel con **todos** los campos del radicador.
""")

def fetch_bytes_from_url(url: str) -> bytes:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.content

@st.cache_data(show_spinner=False)
def load_excel(content: bytes, sheet_name: str | None = None) -> pd.DataFrame:
    bio = io.BytesIO(content)
    return pd.read_excel(bio, sheet_name=sheet_name, dtype=str)

def normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df

st.sidebar.header("Entrada de datos")
mode = st.sidebar.radio("¿Cómo cargar archivos?", ["Subir archivos", "URLs de OneDrive/HTTP"], horizontal=True)

agenda_df = None
rad_df = None

if mode == "Subir archivos":
    up_agenda = st.sidebar.file_uploader("AGENDA VIRTUAL (.xlsx)", type=["xlsx"])
    up_radic = st.sidebar.file_uploader("LIBRO RADICADOR (.xlsx)", type=["xlsx"])
    if up_agenda and up_radic:
        sheet_agenda = st.sidebar.text_input("Hoja AGENDA", value="AGENDA AUDIENCIAS 2025")
        sheet_radic  = st.sidebar.text_input("Hoja RADICADOR", value="PROCESOS 1 INSTANCIA PENAL")
        try:
            agenda_df = load_excel(up_agenda.read(), sheet_agenda)
            rad_df    = load_excel(up_radic.read(), sheet_radic)
        except Exception as e:
            st.error(f"Error al leer Excel: {e}")
elif mode == "URLs de OneDrive/HTTP":
    url_agenda = st.sidebar.text_input("URL AGENDA (.xlsx)", value="", placeholder="Pega el enlace de OneDrive o HTTP directo")
    url_radic  = st.sidebar.text_input("URL RADICADOR (.xlsx)", value="", placeholder="Pega el enlace de OneDrive o HTTP directo")
    sheet_agenda = st.sidebar.text_input("Hoja AGENDA", value="AGENDA AUDIENCIAS 2025")
    sheet_radic  = st.sidebar.text_input("Hoja RADICADOR", value="PROCESOS 1 INSTANCIA PENAL")
    if url_agenda and url_radic:
        try:
            ag_url = to_direct_download(url_agenda)
            rd_url = to_direct_download(url_radic)
            st.caption(f"URL AGENDA resuelta: {ag_url}")
            st.caption(f"URL RADICADOR resuelta: {rd_url}")
            ag_bytes = fetch_bytes_from_url(ag_url)
            rd_bytes = fetch_bytes_from_url(rd_url)
            agenda_df = load_excel(ag_bytes, sheet_agenda)
            rad_df    = load_excel(rd_bytes, sheet_radic)
        except Exception as e:
            st.error(f"Error al descargar/leer Excel: {e}")

if agenda_df is None or rad_df is None:
    st.info("Sube ambos archivos o proporciona ambas URLs para continuar.")
    st.stop()

agenda_df = normalize_cols(agenda_df)
rad_df    = normalize_cols(rad_df)

COL_AGENDA_KEY = "R. INTERNO"
COL_RAD_KEY    = "RADICADO INTERNO"

if COL_AGENDA_KEY not in agenda_df.columns:
    st.error(f"No se encontró la columna '{COL_AGENDA_KEY}' en AGENDA. Columnas: {list(agenda_df.columns)}")
    st.stop()
if COL_RAD_KEY not in rad_df.columns:
    st.error(f"No se encontró la columna '{COL_RAD_KEY}' en RADICADOR. Columnas: {list(rad_df.columns)}")
    st.stop()

ALL_FIELDS = [
  "NO.", "RADICADO INTERNO", "ESTADO", "NO. SPOA", "EMPLEADO RESPONSABLE", "ORIGEN",
  "F. REPARTO", "MES INGRESO", "F. IMPUTACIÓN", "F.ACUSACIÓN", "F. PRESCRIPCIÓN",
  "PROCESADO", "DELITO", "FISCAL", "VICTIMA", "PRIVADO DE LA LIBERTAD", "F. DETENCIÓN",
  "ESTABLECIMIENTO RECLUSIÓN", "ETAPA SIGUIENTE", "DECISIÓN", "SALIDA EN TYBA",
  "TIPO DE EXPEDIENTE", "LINK EXPEDIENTE", "OBSERVACIONES", "LINK EXPEDIENTE JUZGADO ORIGEN"
]
for col in list(ALL_FIELDS):
    if col not in rad_df.columns:
        rad_df[col] = ""

compact = rad_df[[COL_RAD_KEY] + [c for c in ALL_FIELDS if c != COL_RAD_KEY]].copy()

def make_tooltip_text(row):
    parts = []
    for label, key in [("Procesado", "PROCESADO"), ("Delito", "DELITO"), ("Etapa", "ETAPA SIGUIENTE")]:
        val = str(row.get(key, "")).strip()
        if val:
            parts.append(f"{label}: {val}")
    return " • ".join(parts) if parts else ""

compact["__TOOLTIP__"] = compact.apply(make_tooltip_text, axis=1)
merged = agenda_df.merge(compact, how="left", left_on=COL_AGENDA_KEY, right_on=COL_RAD_KEY, suffixes=("", "_RAD"))

gb = GridOptionsBuilder.from_dataframe(merged)
gb.configure_grid_options(enableBrowserTooltips=True)
tooltip_js = JsCode("""function(params){
    if (params.colDef && params.colDef.field === 'R. INTERNO'){
        return params.data && params.data['__TOOLTIP__'] ? params.data['__TOOLTIP__'] : '';
    }
    return '';
}""")
gb.configure_column(COL_AGENDA_KEY, header_name=COL_AGENDA_KEY, tooltipValueGetter=tooltip_js)
gb.configure_selection(selection_mode="single", use_checkbox=False)
grid_options = gb.build()

st.subheader("Agenda con tooltip en columna C (R. INTERNO)")
grid_response = AgGrid(merged, gridOptions=grid_options, update_mode=GridUpdateMode.SELECTION_CHANGED,
                       allow_unsafe_jscode=True, theme="alpine", height=520)

sel_rows = grid_response.get("selected_rows", [])
with st.expander("Panel de detalle del RADICADOR (selecciona una fila en la tabla)", expanded=True):
    if not sel_rows:
        st.caption("Selecciona una fila para ver el detalle...")
    else:
        row = sel_rows[0]
        st.markdown(f"**Radicado interno:** `{row.get('RADICADO INTERNO', row.get(COL_AGENDA_KEY, ''))}`")
        left, right = st.columns(2)
        half = (len(ALL_FIELDS) + 1) // 2
        for i, col in enumerate(ALL_FIELDS):
            val = row.get(col, "")
            target_col = left if i < half else right
            with target_col:
                st.markdown(f"**{col}:** {val if str(val).strip() else '-'}")
st.divider()
st.caption("Tip: La app intentará convertir enlaces de OneDrive/SharePoint a descarga directa.")
