import contextlib
import io
import re
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tests.fake_server import FakeServer

for filename in ('README.md', 'SHOW_AND_TELL_DRAFT.md'):
    blocks = re.findall(r'```python\n(.*?)```', Path(filename).read_text(encoding='utf-8'), re.S)
    for index, code in enumerate(blocks, 1):
        with FakeServer() as server:
            code = re.sub(r'http://localhost:\d+/v1', server.base_url, code)
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(code, f'{filename} example {index}', 'exec'), {})
            assert len(server.requests) == 1, (filename, index)
            print(f'{filename} example {index}: passed (one fake-server request)')
