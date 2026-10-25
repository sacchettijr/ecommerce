@echo off
setlocal

set "BUILDX_BAKE_ENTITLEMENTS_FS=0"

clear
docker compose up --build
