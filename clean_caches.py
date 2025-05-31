import os
import shutil


def clean_caches() -> None:
    for root, dirs, _files in os.walk("."):
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"))
        if ".pytest_cache" in dirs:
            shutil.rmtree(os.path.join(root, ".pytest_cache"))

    if os.path.exists("coverage.xml"):
        os.remove("coverage.xml")

if __name__ == "__main__":
    clean_caches()
