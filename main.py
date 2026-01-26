import pelt
from myconn import conn
nw=conn()
nw.an()
import gc
gc.collect()
print(f"Alloc {gc.mem_alloc()}  Free {gc.mem_free()}")