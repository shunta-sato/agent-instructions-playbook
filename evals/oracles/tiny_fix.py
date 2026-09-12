import importlib.util
from pathlib import Path
import sys
p=Path(sys.argv[1])/'app.py'
s=importlib.util.spec_from_file_location('candidate',p); m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
for value,expected in [(' ABC ','abc'),('\t X-Y\n','x-y'),('A B','a b'),('','')]:
    assert m.slug(value)==expected, (value,expected)
