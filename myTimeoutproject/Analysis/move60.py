from pathlib import Path
import shutil
import os


result_dir = Path(os.environ["RESULT_DIR"])

source_dir = result_dir / "result"
target_dir = result_dir / "result_by_timeout"


for file in source_dir.glob("*.sca"):
    timeout = int(file.stem.split("_")[0])

    if timeout <= 20:
        folder = "timeout_0-20"
    elif timeout <= 40:
        folder = "timeout_21-40"
    else:
        folder = "timeout_41-60"

    destination = target_dir / folder
    destination.mkdir(parents=True, exist_ok=True)

    shutil.move(file, destination / file.name)


print("Fertig.")
