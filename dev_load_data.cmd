@echo off
setlocal

echo Carregando dados iniciais de data/ (country)...
docker exec ecommerce_django python manage.py loaddata data/init_data_address_CountryModel.json
echo _________________________________________________________________________________

echo Carregando dados iniciais de data/ (state)...
docker exec ecommerce_django python manage.py loaddata data/init_data_address_StateModel.json
echo _________________________________________________________________________________

echo Carregando dados iniciais de data/ (city)...
docker exec ecommerce_django python manage.py loaddata data/init_data_address_CityModel.json
echo _________________________________________________________________________________

echo TEST ONLY
echo _________________________________________________________________________________

echo Carregando dados iniciais de data/ (product category)...
docker exec ecommerce_django python manage.py loaddata data/init_data_product_ProductCategoryModel.json
echo _________________________________________________________________________________

echo Carregando dados iniciais de data/ (product)...
@REM  docker compose exec backend python manage.py dumpdata product.ProductModel --indent 2 > data/init_data_product_ProductModel.json
docker exec ecommerce_django python manage.py loaddata data/init_data_product_ProductModel.json
echo _________________________________________________________________________________

echo Carregando dados iniciais de data/ (product images)...
@REM  docker compose exec backend python manage.py dumpdata product.ProductImageModel --indent 2 > data/init_data_product_ProductImageModel.json
docker exec ecommerce_django python manage.py loaddata data/init_data_product_ProductImageModel.json
echo _________________________________________________________________________________






if errorlevel 1 (
    echo.
    echo Falha ao carregar os dados. Confira se o container "ecommerce_django" esta rodando ^(docker compose up^).
    exit /b 1
)

echo.
echo Dados carregados com sucesso.
