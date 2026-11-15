#!/usr/bin/env python3
"""Check the prepared Android payload and optionally the assembled APK (no device required)."""
import argparse
import binascii
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile
from prepare_upstream import ROOT, OVERLAY, validate

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apk", type=Path)
args = parser.parse_args()
project, runtime = ROOT / "app/src/main/assets/project", ROOT / "runtime"
validate(project, runtime)
interface = json.loads((project / "interface.json").read_text())
for resource in interface["resource"]:
    nodes = set()
    for directory in resource["path"]:
        for pipeline in (project / directory / "pipeline").rglob("*.json"):
            nodes.update(json.loads(pipeline.read_text(encoding="utf-8-sig")))
    for task in interface["task"]:
        if not task.get("resource") or resource["name"] in task["resource"]:
            assert task["entry"] in nodes, f'Missing entry {task["entry"]} for {resource["name"]}'
binaries = [p for p in runtime.rglob("*") if p.is_file() and (".so" in p.name or p.name == "python3")]
provided = {p.name for p in binaries}
system = {"libm.so", "libdl.so", "libc.so", "liblog.so", "libmediandk.so", "libz.so", "libandroid.so"}
symbols = set()
for binary in binaries:
    header = subprocess.check_output(["readelf", "-h", str(binary)], text=True)
    assert "AArch64" in header, f"Wrong ABI: {binary}"
    dynamic = subprocess.check_output(["readelf", "-d", str(binary)], text=True)
    for library in re.findall(r"\(NEEDED\).*?\[(.*?)\]", dynamic):
        assert library in provided | system, f"Unresolved dependency {library}: {binary}"
    if binary.parent.name == "maafw":
        exported = subprocess.check_output(["nm", "-D", "--defined-only", str(binary)], text=True)
        symbols.update(re.findall(r"\b(Maa\w+)$", exported, re.MULTILINE))
bridge = (ROOT / "MaaFramework-Android/framework/src/main/java/com/maaframework/android/maa/MaaFrameworkBridge.java").read_text()
calls = set(re.findall(r"(?:library|agentClientLibrary)\.(Maa\w+)\(", bridge))
assert not calls - symbols, f"Missing Maa ABI symbols: {calls - symbols}"
for source in (project / "agent").rglob("*.py"):
    compile(source.read_bytes(), str(source.relative_to(project)), "exec")

if args.apk:
    subprocess.run([sys.executable, str(ROOT / "MaaFramework-Android/tools/verify_android_elf.py"),
                    "--apk", str(args.apk)], check=True)
    # Android ZIP entries use UTF-8 even when the language-encoding flag is unset.
    with zipfile.ZipFile(args.apk, metadata_encoding="utf-8") as apk:
        assert apk.testzip() is None
        assert apk.read("assets/maa_project_manifest.json") == (ROOT / "app/src/main/assets/maa_project_manifest.json").read_bytes()
        for library in (runtime / "maafw").glob("*.so"):
            # AGP strips debug sections in jniLibs, so compare dynamic ABI, not file bytes.
            assert apk.read("assets/bundled_runtime/maafw/" + library.name) == library.read_bytes(), library.name
            with tempfile.NamedTemporaryFile(suffix=".so") as extracted:
                extracted.write(apk.read("lib/arm64-v8a/" + library.name))
                extracted.flush()
                def exported(path):
                    output = subprocess.check_output(["nm", "-D", "--defined-only", str(path)], text=True)
                    return {line.split()[-1] for line in output.splitlines() if line.strip()}
                assert exported(extracted.name) == exported(library), library.name
        for root, prefix in ((project, "assets/project/"), (runtime, "assets/bundled_runtime/"), (OVERLAY, "assets/project_overlay/")):
            # Check the complete payload, including underscore-prefixed Python packages.
            # AAPT silently omits those directories with its default asset filters.
            for path in root.rglob("*"):
                relative = path.relative_to(root)
                if not path.is_file() or any(part.startswith(".") for part in relative.parts):
                    continue
                info = apk.getinfo(prefix + relative.as_posix())
                assert info.file_size == path.stat().st_size, relative
                assert info.CRC == binascii.crc32(path.read_bytes()), relative
        assert not any(name.startswith("lib/") and not name.startswith("lib/arm64-v8a/") for name in apk.namelist())
print(f"Verified {len(binaries)} ARM64 binaries, {len(calls)} Maa symbols, agent syntax" + (" and APK payload" if args.apk else ""))
