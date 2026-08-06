#!/usr/bin/env bash
# Genera un certificado SSL autofirmado para probar HTTPS localmente
# (requerido para probar el Service Worker / PWA desde un teléfono).
# Uso: ./generar_ssl.sh [dominio|IP]
# Ejemplo: ./generar_ssl.sh 192.168.1.10
set -e

DOMAIN="${1:-localhost}"

openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout cert_key.pem -out cert.pem -days 365 \
  -subj "/CN=${DOMAIN}" \
  -addext "subjectAltName=DNS:${DOMAIN},DNS:localhost,IP:127.0.0.1"

echo
echo "Certificado autofirmado generado (cert.pem / cert_key.pem)."
echo "Para arrancar Django con HTTPS local:"
echo "  python manage.py runserver 0.0.0.0:8000 --cert cert.pem --key cert_key.pem"
echo
echo "En producción usa el certificado HTTPS que provee tu hosting (ej. Render automático)."
