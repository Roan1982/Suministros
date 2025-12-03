# Despliegue en PythonAnywhere

Este proyecto Django está configurado para desplegarse en PythonAnywhere.

## Pasos para el despliegue:

1. **Crear cuenta en PythonAnywhere**: Ve a https://www.pythonanywhere.com y crea una cuenta gratuita.

2. **Subir el código**:
   - Crea un repositorio en GitHub con este código.
   - En PythonAnywhere, ve a la pestaña "Files" y clona el repositorio: `git clone https://github.com/Roan1982/almacenes.git`

3. **Crear entorno virtual**:
   - Ve a la pestaña "Consoles" y crea una nueva Bash console.
   - Ejecuta: `mkvirtualenv --python=python3.10 almacenes` (elige la versión de Python compatible).
   - Activa el entorno: `workon almacenes`

4. **Instalar dependencias**:
   - Navega al directorio del proyecto: `cd almacenes/stock`
   - Instala: `pip install -r requirements.txt`

5. **Configurar la base de datos**:
   - En PythonAnywhere, ve a "Databases" y crea una base de datos MySQL.
   - Anota el nombre de la base de datos, usuario y contraseña.

6. **Configurar variables de entorno**:
   - Ve a "Web" > "Variables" y agrega:
     - `DJANGO_SECRET_KEY`: Una clave secreta segura (genera una nueva, por ejemplo usando `python -c "import secrets; print(secrets.token_urlsafe(50))"`).
     - `DJANGO_ALLOWED_HOSTS`: `<tu_dominio>`
     - `DATABASE_NAME`: `<tu_base_de_datos>`
     - `DATABASE_USER`: `<tu_usuario>`
     - `DATABASE_PASSWORD`: `<tu_contraseña>`
     - `DATABASE_HOST`: `<tu_host>`
     - `DATABASE_PORT`: `<tu_puerto>`

7. **Ejecutar migraciones**:
   - En la consola: `python manage.py migrate`

8. **Recopilar archivos estáticos**:
   - `python manage.py collectstatic`

9. **Configurar la aplicación web**:
   - Ve a "Web" > "Add a new web app".
   - Selecciona "Manual configuration" y Python 3.10.
   - En "WSGI configuration file", apunta a `/home/<tu_usuario>/almacenes/stock/wsgi_production.py`
   - En "Static files", agrega:
     - URL: `/static/`
     - Directory: `/home/<tu_usuario>/almacenes/stock/staticfiles`

10. **Reiniciar la aplicación**:
    - Haz clic en "Reload" en la pestaña "Web".

Tu aplicación debería estar corriendo en `https://<tu_usuario>.pythonanywhere.com`.

## Notas:
- Asegúrate de que el SECRET_KEY sea único y secreto.
- Si usas PostgreSQL en lugar de MySQL, cambia las configuraciones de base de datos en `settings_production.py`.