clear
@REM ./dev_reset.cmd
docker compose down --rmi local -v
docker builder prune -f
docker image prune -f
docker container prune -f
docker volume prune -f
setlocal
set "BUILDX_BAKE_ENTITLEMENTS_FS=0"


echo Gerando certificado autoassinado para o Nginx...
docker run --rm -v ecommerce_letsencrypt:/etc/letsencrypt alpine sh -c "apk add --no-cache openssl >/dev/null 2>&1 && mkdir -p /etc/letsencrypt/live/177.222.210.50 && openssl req -x509 -nodes -newkey rsa:2048 -days 365 -keyout /etc/letsencrypt/live/177.222.210.50/privkey.pem -out /etc/letsencrypt/live/177.222.210.50/fullchain.pem -subj '/CN=177.222.210.50'"

docker compose up --build
