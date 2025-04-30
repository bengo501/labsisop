#!/bin/sh

# Caminho completo para o diretório alvo
TARGET_DIR=$1

# Copiar o script para o diretório correto
cp ../custom-scripts/S41network-config $TARGET_DIR/target/etc/init.d/
chmod +x $TARGET_DIR/target/etc/init.d/S41network-config

cp ../custom-scripts/S50hello $TARGET_DIR/target/etc/init.d/
chmod +x $TARGET_DIR/target/etc/init.d/S50hello

cp board/labsisop/linuxstatus.py output/target/usr/bin/
chmod +x output/target/usr/bin/linuxstatus.py

chmod +x output/target/etc/init.d/S50linuxstatus

