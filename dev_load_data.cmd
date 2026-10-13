@echo off
setlocal

echo Carregando dados iniciais de data/ (country)...
docker exec ecommerce_django python manage.py loaddata data/init_data_CountryModel.json
echo _________________________________________________________________________________

echo Carregando dados iniciais de data/ (state)...
docker exec ecommerce_django python manage.py loaddata data/init_data_StateModel.json
echo _________________________________________________________________________________

echo Carregando dados iniciais de data/ (city)...
docker exec ecommerce_django python manage.py loaddata data/init_data_CityModel.json
echo _________________________________________________________________________________

if errorlevel 1 (
    echo.
    echo Falha ao carregar os dados. Confira se o container "ecommerce_django" esta rodando ^(docker compose up^).
    exit /b 1
)

echo.
echo Dados carregados com sucesso.
