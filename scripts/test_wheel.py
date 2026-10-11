"""Install one release wheel in a clean environment on its native platform."""

import subprocess
import sys
import tempfile
from pathlib import Path


def verify(directory):
    wheels = list(directory.glob("*.whl"))
    if len(wheels) != 1:
        raise ValueError(f"Expected one wheel, found {len(wheels)}")
    with tempfile.TemporaryDirectory(prefix="pyshacl-turbo-wheel-") as temporary:
        environment = Path(temporary) / "venv"
        subprocess.run(["uv", "venv", "--python", sys.executable, str(environment)], check=True)
        python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        subprocess.run(
            ["uv", "pip", "install", "--python", str(python), str(wheels[0].resolve())], check=True
        )
        smoke = Path(__file__).with_name("smoke_wheel.py").resolve()
        subprocess.run([str(python), "-I", str(smoke)], cwd=temporary, check=True)
        subprocess.run(
            [str(python), "-I", "-m", "pyshacl_turbo", "--help"],
            cwd=temporary,
            check=True,
            stdout=subprocess.DEVNULL,
        )


if __name__ == "__main__":
    verify(Path(sys.argv[1]))
