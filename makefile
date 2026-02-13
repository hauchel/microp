objects = boot.mpy bas.mpy myconn.mpy mydisp.mpy
P = COM3
.PHONY: all upload clean

all : $(objects)
%.mpy: %.py
	mpy-cross $<

clean :
	del $(objects)

upload: $(objects)
	@for %%f in ($(objects)) do ( \
	    echo Upload: %%f  & \
	    ampy --port $(P) put %%f %%f || (echo Fehler beim Upload von %%f & exit 1) \
	)
