d:
cd /esp/microp/
set P=COM%1
ampy --port %P% put boot.py boot.py
ampy --port %P% put webrepl_cfg.py webrepl_cfg.py
ampy --port %P% put myconn.py myconn.py
ampy --port %P% put bas.mpy bas.mpy
ampy --port %P% put espn.py espn.py