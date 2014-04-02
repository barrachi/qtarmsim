#!/usr/bin/make -f

UISRCS:=$(wildcard ui/*.ui)
UIOBJS:=$(UISRCS:%.ui=%.py)

QRSRCS:=$(wildcard resources/*.qrc)
QROBJS:=$(QRSRCS:%.qrc=%_rc.py)

all: ${UIOBJS} ${QROBJS}

%.py : %.ui
	pyuic4 -o $@ $<

%_rc.py : %.qrc
	pyrcc4 -py3 -o $@ $<
