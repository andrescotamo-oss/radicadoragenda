# run_app.py
import os, sys
def resource_path(rel_path: str) -> str:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, rel_path)
def main():
    app_path = resource_path("app.py")
    sys.argv = ["streamlit", "run", app_path, "--server.headless=true"]
    from streamlit.web.cli import main as st_main
    sys.exit(st_main())
if __name__ == "__main__":
    main()
