# build.spec — PyInstaller (corregido)
from PyInstaller.building.build_main import Analysis, PYZ, EXE
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os

app_name = "AgendaRadicador"

# Recolecta archivos de datos de los paquetes usados
datas = []
datas += collect_data_files("streamlit", include_py_files=True)
datas += collect_data_files("pandas", include_py_files=False)
datas += collect_data_files("requests", include_py_files=False)
datas += collect_data_files("st_aggrid", include_py_files=False)  # paquete es st_aggrid

# Incluye también nuestros propios archivos fuente como "DATA"
datas += [(os.path.abspath("app.py"), "app.py")]
if os.path.exists("README.txt"):
    datas += [(os.path.abspath("README.txt"), "README.txt")]

# Algunos módulos que a veces PyInstaller no detecta automáticamente
hidden = []
hidden += collect_submodules("st_aggrid")
hidden += [
    "streamlit",
    "streamlit.web.cli",
    "streamlit.runtime",
    "streamlit.web.bootstrap",
    "pkg_resources.py2_warn",
]

a = Analysis(
    ["run_app.py"],      # nuestro lanzador
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hidden,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name=app_name,
    console=False,   # sin consola
    icon=None,       # si quieres, pon aquí tu .ico
    upx=False,       # más seguro desactivar UPX en runners CI
)
