from pathlib import Path
import subprocess,sys
root=Path(sys.argv[1])
for path in [root/'app.py',root/'callers.py']:
    assert 'legacy_double' not in path.read_text(), path
p=subprocess.run([sys.executable,'-c','from app import double_value; from callers import call; assert double_value(-3)==-6; assert call(7)==14'],cwd=root,capture_output=True,text=True,timeout=5)
assert p.returncode==0,p.stderr
