import os
import shutil


def clean_caches():
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"))
            print(f"Removed: {os.path.join(root, '__pycache__')}")
        if ".pytest_cache" in dirs:
            shutil.rmtree(os.path.join(root, ".pytest_cache"))
            print(f"Removed: {os.path.join(root, '.pytest_cache')}")

    if os.path.exists("coverage.xml"):
        os.remove("coverage.xml")
        print("Removed: coverage.xml")

if __name__ == "__main__":
    clean_caches()
