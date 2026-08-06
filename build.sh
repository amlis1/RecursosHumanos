#!/usr/bin/env bash
# Script de build para el despliegue (Render / similar).
# Render genera y renueva el certificado SSL HTTPS automáticamente.
set -o errexit
set -o pipefail

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
