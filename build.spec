# build.spec — PyInstaller
from PyInstaller.utils.hooks import copy_metadata
from PyInstaller.building.build_main import Analysis, PYZ, EXE
from PyInstaller.building.datastruct import TOC
import os
app_name = "AgendaRadicador"
datas = TOC()
datas += [(os.path.abspath("app.py"), "app.py", "DATA")]
if os.path.exists("README.txt"):
    datas += [(os.path.abspath("README.txt"), "README.txt", "DATA")]
datas += copy_metadata("streamlit")
datas += copy_metadata("pandas")
datas += copy_metadata("requests")
a = Analysis(['run_app.py'], pathex=['.'], binaries=[], datas=datas, hiddenimports=[
    'streamlit','streamlit.web.cli','streamlit.runtime','streamlit.web.bootstrap','pkg_resources.py2_warn',
], noarchive=False)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, name=app_name, console=False, icon=None, upx=True)
exe
