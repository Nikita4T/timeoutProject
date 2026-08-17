from pathlib import Path
import shutil
import os


resultDir = Path(os.environ["RESULT_DIR"])

sourceDir = resultDir / "result_by_timeout"
destDir = resultDir / "result"

destDir.mkdir(parents=True, exist_ok=True)

count = 0

for folder in sourceDir.glob("timeout_*"):
    for file in folder.glob("*.csv"):
        shutil.move(file, destDir / file.name)
        count += 1

print(f"{count} CSV-Dateien verschoben.")
