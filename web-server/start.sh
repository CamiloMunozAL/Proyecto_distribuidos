#!/bin/bash
#Script para iniciar el servidor de la aplicacion web

#Crear y activar entorno virtual si no existe
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
#Activar entorno virtual
source venv/bin/activate
#instalar dependencias dentro del entorno virtual
pip install -r requirements.txt
#ejecutar la aplicacion
python3 app.py