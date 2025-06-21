import subprocess
import pathlib
import sys
HERE = pathlib.Path(__file__).resolve().parent
PKGS = ["api", "ai_models", "agent_team", "marketing", "monetization", "niche_analysis", "common_utils"]
OUT = HERE / "source" / "api"
OUT.mkdir(parents=True, exist_ok=True)
subprocess.check_call([
    sys.executable,
    "-m", "sphinx.ext.apidoc",
    "-o", str(OUT),
    *PKGS,
    "--force",
    "--no-toc",
])