from pathlib import Path
import subprocess,sys
script=Path(sys.argv[1])/'app.py'
for data,total in [('1\n2\n3\n',6),('\n -3\n5\n',2),('',0)]:
    p=subprocess.run([sys.executable,str(script)],input=data,text=True,capture_output=True,timeout=5)
    assert p.returncode==0 and p.stdout.strip()==str(total),(p.returncode,p.stdout,p.stderr)
p=subprocess.run([sys.executable,str(script)],input='1\ninvalid\n',text=True,capture_output=True,timeout=5)
assert p.returncode!=0 and p.stderr.strip() and not p.stdout.strip()
