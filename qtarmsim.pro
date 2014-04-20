# TEMPLATE = app

# TARGET = 

# DEPENDPATH += src \
#              ui

#INCLUDEPATH += ./ \
#              src

#HEADERS =

# FOMS += ui/breakpo.ui \
#     ui/consola.ui \
#     ui/ejec.ui \
#     ui/help.ui \
#     ui/imprimir.ui \
#     ui/mainwindow.ui \
#     ui/multi.ui \
#     ui/opciones.ui \
#     ui/value.ui

SOURCES = ./qtarmsim.py \
    ui/help.py 
#\
#    ui/mainwindow.py

#RESOURCES += resources/main.qrc \
#             resources/console.qrc

TRANSLATIONS += languages/qtarmsim_es.ts
CODECFORTR      = UTF-8
CODECFORSRC     = UTF-8
