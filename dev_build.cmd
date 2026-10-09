@echo off
setlocal

set "BUILDX_BAKE_ENTITLEMENTS_FS=0"

docker compose up --build
