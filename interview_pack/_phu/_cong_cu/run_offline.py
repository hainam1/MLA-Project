"""Run the existing two scripts without network or repository data access."""
from pathlib import Path
import runpy,sys,time,os
sys.stdout.reconfigure(encoding='utf-8');sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[2]
def guard(event,args):
 if event.startswith(('socket.','urllib.','http.client.')):raise RuntimeError('NETWORK_BLOCKED')
 if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
  path=Path(os.fsdecode(args[0])).resolve()
  if path.is_relative_to(P.parent) and not path.is_relative_to(P):raise RuntimeError('REPO_READ_OUTSIDE_PACK_BLOCKED')
sys.addaudithook(guard)
start=time.perf_counter()
print('OFFLINE GUARD ACTIVE: network denied; reads outside pack in repository denied.')
for name in ['check_d_88_of_386.py','check_synthetic_ranking.py']:
 script=P/'_phu/07_kiem_tra_offline'/name;sys.argv=[str(script)]
 runpy.run_path(str(script),run_name='__main__')
print('Ky vong lam tron: 77,36')
print(f'Both checks completed in {time.perf_counter()-start:.4f} seconds.')
