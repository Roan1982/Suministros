# Sistema de Inventario - Stock de Almacenes

[![Django](https://img.shields.io/badge/Django-5.2.4-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

Un sistema completo de gestión de inventario para almacenes desarrollado con Django, PostgreSQL y Docker. Incluye control de stock, órdenes de compra, auditoría completa y gestión de permisos por rubros.

## 📋 Características Principales

### 🔍 Sistema de Auditoría Completo
- **Registro automático** de todas las operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
- **Captura de usuario** que realiza cada acción
- **Historial detallado** con cambios específicos en JSON
- **Vista administrativa** con filtros avanzados (usuario, acción, modelo, fechas)
- **Interfaz responsive** con paginación y búsqueda

### 👥 Control de Acceso por Rubros
- **Grupos automáticos** basados en rubros existentes
- **9 grupos pre-configurados** (INSUMOS AIRES, PLOMERIA, ELECTRICIDAD, etc.)
- **Permisos granulares** para cada tipo de rubro
- **Command personalizado** para crear grupos: `python manage.py create_rubro_groups`

### 📸 Gestión de Imágenes
- **Subida de imágenes** para productos/bienes
- **Almacenamiento en base de datos** (BinaryField)
- **Visualización integrada** en formularios y listados

### 📊 Dashboard Interactivo
- **Vista general** del estado del inventario
- **Órdenes vencidas** destacadas en rojo con días negativos
- **Estadísticas rápidas** de productos y órdenes

### 🐳 Despliegue con Docker
- **Contenedorizado** con Docker Compose
- **PostgreSQL 16** como base de datos
- **Configuración de producción** lista
- **Volúmenes persistentes** para datos

## 🚀 Instalación y Configuración

### Prerrequisitos
- Docker y Docker Compose
- Git

### Clonación del Repositorio
```bash
git clone https://github.com/Roan1982/Suministros.git
cd Suministros/stock
```

### Configuración con Docker
```bash
# Construir y levantar los contenedores
docker-compose up --build

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear grupos de permisos por rubros
docker-compose exec web python manage.py create_rubro_groups

# Crear superusuario
docker-compose exec web python manage.py createsuperuser
```

### Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:
```env
DJANGO_SECRET_KEY=tu-clave-secreta-aqui
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=stockdb
DATABASE_USER=stockuser
DATABASE_PASSWORD=tu-password
DATABASE_HOST=db
DATABASE_PORT=5432
```

## 📖 Uso del Sistema

### Acceso al Sistema
- **URL principal:** `http://localhost:8000`
- **Panel de administración:** `http://localhost:8000/admin/`
- **Auditoría (solo administradores):** `http://localhost:8000/auditoria/`

### Funcionalidades Disponibles

#### 📋 Gestión de Rubros
- Crear, editar y eliminar rubros
- Clasificación automática de productos

#### 📦 Gestión de Bienes/Productos
- CRUD completo de productos
- Subida de imágenes
- Asociación con rubros
- Búsqueda y filtrado

#### 📋 Órdenes de Compra
- Creación de órdenes de compra
- Seguimiento de proveedores
- Estados de órdenes (pendiente, aprobado, recibido)
- Cálculo automático de totales

#### 👥 Gestión de Usuarios y Permisos
- Sistema de autenticación Django
- Grupos por rubros con permisos específicos
- Control de acceso basado en roles

#### 🔍 Auditoría y Logs
- Historial completo de cambios
- Filtros por usuario, acción, modelo y fecha
- Vista detallada de cambios realizados
- Exportación de datos de auditoría

## 🏗️ Arquitectura del Proyecto

```
stock/
├── inventario/                 # App principal
│   ├── models.py              # Modelos de datos
│   ├── views.py               # Vistas y lógica
│   ├── signals.py             # Señales de auditoría
│   ├── middleware/            # Middleware personalizado
│   │   └── current_user.py    # Captura de usuario actual
│   ├── management/            # Commands personalizados
│   │   └── commands/
│   │       └── create_rubro_groups.py
│   ├── templates/             # Plantillas HTML
│   └── static/                # Archivos estáticos
├── stockapp/                  # Configuración Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── docker-compose.yml         # Configuración Docker
├── Dockerfile                 # Imagen Docker
├── requirements.txt           # Dependencias Python
└── manage.py                  # Script de gestión Django
```

## 🔧 Comandos Útiles

### Gestión de Contenedores
```bash
# Levantar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Ver logs
docker-compose logs -f web

# Acceder al shell del contenedor
docker-compose exec web bash
```

### Gestión de Django
```bash
# Crear migraciones
docker-compose exec web python manage.py makemigrations

# Aplicar migraciones
docker-compose exec web python manage.py migrate

# Crear grupos de rubros
docker-compose exec web python manage.py create_rubro_groups

# Recargar servidor
docker-compose restart web
```

### Gestión de Base de Datos
```bash
# Backup de base de datos
docker-compose exec db pg_dump -U stockuser stockdb > backup.sql

# Restaurar base de datos
docker-compose exec -T db psql -U stockuser stockdb < backup.sql
```

## 🔐 Grupos y Permisos

### Grupos Automáticos por Rubro
El sistema crea automáticamente los siguientes grupos:

- **Rubro: INSUMOS AIRES**
- **Rubro: PLOMERIA**
- **Rubro: ELECTRICIDAD**
- **Rubro: PINTURA**
- **Rubro: LIBRERIA**
- **Rubro: CABLE CANAL**
- **Rubro: VESTIMENTA**
- **Rubro: TERMOFUSION**
- **Rubro: VARIOS**

Cada grupo tiene permisos para:
- Ver bienes (`view_bien`)
- Agregar bienes (`add_bien`)
- Modificar bienes (`change_bien`)
- Eliminar bienes (`delete_bien`)

## 📊 Auditoría del Sistema

### Información Registrada
- **Usuario** que realizó la acción
- **Fecha y hora** exacta
- **Tipo de acción** (CREATE, UPDATE, DELETE)
- **Modelo afectado**
- **Objeto específico**
- **Cambios realizados** (en formato JSON)

### Acceso a Auditoría
- Solo usuarios con permisos de administrador
- Filtros por usuario, acción, modelo y rango de fechas
- Paginación automática
- Vista detallada de cambios

## 🐛 Solución de Problemas

### Error de Conexión a Base de Datos
```bash
# Verificar que PostgreSQL esté ejecutándose
docker-compose ps

# Revisar logs de la base de datos
docker-compose logs db

# Reiniciar servicios
docker-compose restart
```

### Problemas de Migraciones
```bash
# Resetear migraciones (CUIDADO: elimina datos)
docker-compose exec web python manage.py migrate inventario zero
docker-compose exec web python manage.py migrate
```

### Error 500 en Auditoría
```bash
# Verificar que el middleware esté configurado
docker-compose exec web python manage.py check

# Reiniciar el contenedor web
docker-compose restart web
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request