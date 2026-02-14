obj_bas = boot.mpy bas.mpy myconn.mpy mydisp.mpy
obj_eno = espn.mpy  encli.mpy  enserv.mpy 
obj_pel = myBH1750.mpy  myMCP4725.mpy myKR.mpy myINA219.mpy myCONF.mpy pelt.mpy



P ?= COM5
.PHONY: bas eno pel up clean
define upload 
	@echo "Neue Dateien: $?"
	@for %%f in ($?) do ( \
	    echo Up: %%f  & \
	    putmak %%f 55 || (echo Fehler beim Upload von %%f & exit 1) \
	)
endef

define upampy
	@for %%f in ($(obj)) do ( \
	    echo Up: %%f  & \
	    ampy --port $(P) put %%f %%f || (echo Fehler beim Upload von %%f & exit 1) \
	)
endef

bas: $(obj_bas)
	$(upload)

eno: $(obj_eno)	
	$(upload)
	
pel: $(obj_pel)
	$(upload)
	
%.mpy: %.py
	mpy-cross $<

clean :
	del *.mpy 		

up : $(obj)
	@for %%f in ($(obj)) do ( \
	    echo Up: %%f  & \
	    ampy --port $(P) put %%f %%f || (echo Fehler beim Upload von %%f & exit 1) \
	)
