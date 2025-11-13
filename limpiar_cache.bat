@echo off
echo Limpiando cache de Python (.pyc y __pycache__)...

REM Eliminar todos los archivos .pyc
for /r %%i in (*.pyc) do (
    del "%%i"
    echo Eliminado: %%i
)

REM Eliminar todas las carpetas __pycache__
for /d /r %%i in (__pycache__) do (
    if exist "%%i" (
        rmdir /s /q "%%i"
        echo Eliminada carpeta: %%i
    )
)

echo.
echo ¡Cache limpiado exitosamente!
echo Ahora puedes ejecutar: python manage.py runserver
pause
