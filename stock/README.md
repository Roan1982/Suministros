# Sistema de Gestión de Inventario y Servicios

Un sistema completo de gestión de inventario desarrollado con Django que permite administrar bienes, órdenes de compra, entregas, remitos y servicios con renovaciones periódicas.

## Características Principales

### Gestión de Inventario
- **Bienes**: Administración completa de productos con categorías (rubros)
- **Órdenes de Compra**: Creación y gestión de órdenes de compra con múltiples ítems
- **Entregas**: Registro de entregas con control de stock automático
- **Remitos**: Generación de remitos en PDF para entregas
- **Control de Stock**: Seguimiento automático del stock disponible por producto

### Gestión de Servicios
- **Servicios Recurrentes**: Administración de servicios con frecuencias variables (semanal, quincenal, mensual)
- **Estados de Servicio**: Control de estados (Activo, Por Vencer, Vencido, Cancelado)
- **Renovaciones Automáticas**: Cálculo automático de próximas fechas de renovación
- **Alertas de Vencimiento**: Notificaciones en el dashboard para servicios próximos a vencer

### Sistema de Auditoría
- **Registro Automático**: Todas las operaciones quedan registradas con usuario y timestamp
- **Historial Completo**: Seguimiento de cambios en todos los modelos
- **Filtros Avanzados**: Búsqueda y filtrado por usuario, modelo, acción y fechas

### Seguridad y Usuarios
- **Grupos de Usuarios**: Asignación automática de permisos por categorías de productos
- **Autenticación**: Sistema completo de login/logout
- **Permisos**: Control granular de acceso a funcionalidades

### Dashboard Interactivo
- **Alertas de Stock**: Productos con stock bajo
- **Órdenes por Vencer**: Órdenes de compra próximas a su fecha límite
- **Servicios por Renovar**: Servicios que requieren renovación próximamente
- **Vista General**: Resumen ejecutivo del estado del inventario

### Reportes y Exportación
- **Reportes de Stock**: Por rubro, por bien, con exportación a Excel/PDF
- **Reportes de Entregas**: Por año, por área/persona, con exportación
- **Ranking de Bienes**: Productos más entregados
- **Ranking de Proveedores**: Proveedores con mayor volumen

## Tecnologías Utilizadas

- **Backend**: Django 5.2.4
- **Base de Datos**: PostgreSQL 16
- **Frontend**: Bootstrap 5, JavaScript
- **PDF Generation**: xhtml2pdf
- **Charts**: Bootstrap components
- **Deployment**: Docker, Docker Compose

## Instalación y Despliegue

### Desarrollo Local

1. **Clonar el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd almacenes/stock
   ```

2. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar base de datos**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Ejecutar servidor**:
   ```bash
   python manage.py runserver
   ```

### Despliegue con Docker

1. **Construir y ejecutar**:
   ```bash
   docker-compose up --build
   ```

2. **Aplicar migraciones**:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Crear superusuario**:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

Para instrucciones detalladas de despliegue en PythonAnywhere, consulta `README_DEPLOY.md`.

## Estructura del Proyecto

```
stock/
├── inventario/              # App principal
│   ├── models.py           # Modelos de datos
│   ├── views.py            # Lógica de vistas
│   ├── admin.py            # Configuración del admin
│   ├── urls.py             # URLs de la app
│   ├── forms.py            # Formularios
│   ├── templates/          # Plantillas HTML
│   ├── static/             # Archivos estáticos
│   └── migrations/         # Migraciones de BD
├── stockapp/               # Configuración del proyecto
├── static/                 # Archivos estáticos globales
├── requirements.txt        # Dependencias Python
├── Dockerfile             # Configuración Docker
├── docker-compose.yml     # Servicios Docker
└── manage.py              # Script de gestión Django
```

## Funcionalidades de Servicios

### Tipos de Frecuencia
- **Semanal**: Renovación cada 7 días
- **Quincenal**: Renovación cada 15 días
- **Mensual**: Renovación cada mes

### Estados de Servicio
- **ACTIVO**: Servicio activo y al día
- **POR_VENCER**: Próxima renovación en menos de 30 días
- **VENCIDO**: Servicio vencido, requiere renovación inmediata
- **CANCELADO**: Servicio cancelado

### Cálculo de Renovaciones
El sistema calcula automáticamente la próxima fecha de renovación basada en:
- Fecha de inicio del servicio
- Frecuencia seleccionada
- Fecha de la última renovación (si aplica)

### Dashboard de Servicios
- Alertas visuales para servicios próximos a vencer
- Indicadores de estado con colores
- Enlaces directos a gestión de servicios

## API Endpoints

### Bienes
- `GET /bienes/` - Lista de bienes
- `POST /agregar_bien/` - Crear bien
- `GET/POST /editar_bien/<id>/` - Editar bien

### Órdenes de Compra
- `GET /ordenes/` - Lista de órdenes
- `POST /agregar_orden/` - Crear orden
- `GET/POST /ordenes/<id>/editar/` - Editar orden

### Entregas
- `GET /remitos/` - Lista de remitos
- `POST /crear_entrega/` - Crear entrega
- `GET /remitos/<id>/print/` - Imprimir remito

### Servicios
- `GET /servicios/` - Lista de servicios
- `POST /agregar_servicio/` - Crear servicio
- `GET/POST /servicios/<id>/editar/` - Editar servicio
- `GET /servicios/<id>/` - Detalle de servicio

### Reportes
- `GET /reportes/` - Dashboard de reportes
- `GET /reportes/stock_rubro/` - Stock por rubro
- `GET /reportes/stock_bien/` - Stock por bien
- `GET /reportes/entregas_anio/` - Entregas por año
- `GET /reportes/entregas_area/` - Entregas por área

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.</content>
<parameter name="filePath">c:\Users\angel.steklein\Documents\desarrollo\almacenes\stock\README.md