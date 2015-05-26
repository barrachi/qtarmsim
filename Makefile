#!/usr/bin/make -f

ifdef SYSTEMROOT
   RM = del /Q
   FixPath = $(subst /,\,$1)
   PYSIDEUIC4 = pyside-uic.bat
else
   ifeq ($(shell uname), Linux)
      RM = rm -f
      FixPath = $1
      PYSIDEUIC4 = pyside-uic
   endif
endif


UISRCS:=$(wildcard ./qtarmsim/ui/*.ui)
UIOBJS:=$(UISRCS:%.ui=%.py)

QRSRCS:=$(wildcard ./qtarmsim/res/*.qrc)
QROBJS:=$(QRSRCS:%.qrc=%_rc.py)

TSSRCS:=$(wildcard ./qtarmsim/lang/*.ts)
TSOBJS:=$(TSSRCS:%.ts=%.qm)

all: ${UIOBJS} ${QROBJS} ${TSOBJS}

%.py : %.ui
	$(PYSIDEUIC4) -o $@ $<
	./qtarmsim/res/bin/add_file_icons.py $@ > $@.tmp
	mv $@.tmp $@

%_rc.py : %.qrc
	pyside-rcc -py3 -o $@ $<

%.qm : %.ts
	lrelease ./qtarmsim/qtarmsim.pro

clean:
	find ./qtarmsim/ -type f -name "*.pyc" -exec rm -f {} \; 2>/dev/null
	find ./qtarmsim/ -type d -name "__pycache__" -exec rm -rf {} \; 2>/dev/null
	cd ./examples; $(RM) *.o *.err *.lst

linguist:
	@ \
	pyside-lupdate4 ./qtarmsim/qtarmsim.pro; \
	echo "Now you can run 'linguist ./qtarmsim/lang/qtarmsim_es.ts'"
