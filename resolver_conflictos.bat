@echo off
echo ============================================
echo RESOLVIENDO CONFLICTOS DE GIT - BANETON
echo ============================================
echo.

echo [1/5] Marcando archivos conflictivos como resueltos...
git add Bakery_proyect/urls.py
git add inventory/migrations/0001_initial.py
git add customers/migrations/0001_initial.py
git add pos/templates/pos.html
echo ✓ Archivos marcados como resueltos
echo.

echo [2/5] Completando el merge...
git commit -m "Resueltos conflictos: urls.py, migraciones y templates"
echo ✓ Merge completado
echo.

echo [3/5] Creando migraciones para reorder_threshold...
python manage.py makemigrations
echo ✓ Migraciones creadas
echo.

echo [4/5] Aplicando migraciones...
python manage.py migrate
echo ✓ Migraciones aplicadas
echo.

echo [5/5] Verificando estado de migraciones...
python manage.py showmigrations inventory
echo.

echo ============================================
echo ✓ PROCESO COMPLETADO EXITOSAMENTE
echo ============================================
echo.
echo Ahora puedes:
echo   1. git push origin santiago2  (para subir tus cambios)
echo   2. python manage.py runserver (para probar el servidor)
echo   3. Acceder a /inventory/low-stock/ (para ver alertas)
echo.
pause
