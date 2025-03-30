#!/bin/sh

# Caminho completo para o diretório alvo
TARGET_DIR=$1

# Copiar o script para o diretório correto
cp ../custom-scripts/S41network-config $TARGET_DIR/etc/init.d/
chmod +x $TARGET_DIR/etc/init.d/S41network-config

