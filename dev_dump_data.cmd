@echo off
setlocal

echo Exportando dados iniciais do model/ (country)...
docker exec ecommerce_django python manage.py dumpdata address.CountryModel --indent 2 > data/init_data_address_CountryModel.json
echo _________________________________________________________________________________

echo Exportando dados iniciais do model/ (state)...
docker exec ecommerce_django python manage.py dumpdata address.StateModel --indent 2 > data/init_data_address_StateModel.json
echo _________________________________________________________________________________

echo Exportando dados iniciais do model/ (city)...
docker exec ecommerce_django python manage.py dumpdata address.CityModel --indent 2 > data/init_data_address_CityModel.json
echo _________________________________________________________________________________

echo TEST ONLY
echo _________________________________________________________________________________

echo Exportando dados iniciais do model/ (product category)...
docker compose exec backend python manage.py dumpdata product.ProductCategoryModel --indent 2 > data/init_data_product_ProductCategoryModel.json
echo _________________________________________________________________________________

echo Exportando dados iniciais do model/ (product)...
docker compose exec backend python manage.py dumpdata product.ProductModel --indent 2 > data/init_data_product_ProductModel.json
echo _________________________________________________________________________________

echo Exportando dados iniciais de data/ (product images)...
docker compose exec backend python manage.py dumpdata product.ProductImageModel --indent 2 > data/init_data_product_ProductImageModel.json
echo _________________________________________________________________________________






if errorlevel 1 (
    echo.
    echo Falha ao exportar os dados. Confira se o container "ecommerce_django" esta rodando ^(docker compose up^).
    exit /b 1
)

echo.
echo Dados exportados com sucesso.
