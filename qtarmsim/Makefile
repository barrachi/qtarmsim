#!/usr/bin/make -f

UISRCS:=$(wildcard ui/*.ui)
UIOBJS:=$(UISRCS:%.ui=%.py)

QRSRCS:=$(wildcard res/*.qrc)
QROBJS:=$(QRSRCS:%.qrc=%_rc.py)

TSSRCS:=$(wildcard lang/*.ts)
TSOBJS:=$(TSSRCS:%.ts=%.qm)

all: ${UIOBJS} ${QROBJS} ${TSOBJS}

%.py : %.ui
	pyuic4 -o $@ $<

%_rc.py : %.qrc
	pyrcc4 -py3 -o $@ $<

%.qm : %.ts
	lrelease qtarmsim.pro

clean:
	find ./ -type f -name "*.pyc" -exec rm -f {} \; 2>/dev/null
	find ./ -type d -name "__pycache__" -exec rm -rf {} \; 2>/dev/null

linguist:
	@ \
	pylupdate4 qtarmsim.pro; \
	echo "Now you can run 'linguist lang/qtarmsim_es.ts'"
