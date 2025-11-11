
# 🥖 Sistema de Gestión Baneton

**Proyecto Integrador 1 - Ingeniería de Sistemas**  
*Universidad EAFIT*

## 📋 Descripción del Proyecto

**Baneton** es un sistema integral de gestión diseñado específicamente para panaderías y establecimientos de repostería. El sistema permite gestionar de manera eficiente el inventario, las ventas, los productos y generar reportes detallados para la toma de decisiones empresariales.

### 🎯 ¿Por qué Baneton?

Las panaderías tradicionales enfrentan desafíos únicos:
- **Gestión compleja de inventario** con materias primas perecederas
- **Control de stock** en tiempo real para productos frescos
- **Seguimiento de ventas** para optimizar la producción diaria
- **Reportes precisos** para analizar el rendimiento del negocio

Baneton soluciona estos problemas mediante una plataforma web intuitiva y completa.

## ✨ Características Principales

### 🏪 **Punto de Venta (POS)**
- Interfaz intuitiva para procesar ventas
- Soporte para múltiples métodos de pago (Efectivo, Transferencia)
- Cálculo automático de totales
- Registro detallado de cada transacción

### 📦 **Gestión de Inventario**
- Control de materias primas con fechas de vencimiento
- Seguimiento de stock de productos terminados
- Alertas automáticas para stock bajo
- Relación productos-materias primas

### 📊 **Reportes y Analytics**
- **Reporte diario de ventas** con métricas clave:
  - Revenue total del día
  - Número de órdenes procesadas
  - Productos más vendidos
  - Análisis por métodos de pago
- Exportación e impresión de reportes

### 🛍️ **Catálogo de Productos**
- Visualización de productos disponibles para clientes
- Gestión de precios y descripciones
- Carga de imágenes de productos
- Control de disponibilidad

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 5.2.4** - Framework web de Python
- **SQLite3** - Base de datos
- **Python 3.13** - Lenguaje de programación

### Frontend
- **HTML5/CSS3** - Estructura y estilos
- **Bootstrap** - Framework CSS responsivo
- **JavaScript** - Interactividad del cliente

### Herramientas de Desarrollo
- **Git** - Control de versiones
- **Django Admin** - Panel de administración
- **Django ORM** - Mapeo objeto-relacional

## 🏗️ Arquitectura del Sistema

El proyecto sigue el patrón **MVT (Model-View-Template)** de Django:

```
Baneton/
├── Bakery_proyect/          # Configuración principal del proyecto
├── core/                    # Funcionalidades centrales
├── inventory/               # Gestión de inventario y materias primas
├── pos/                     # Punto de venta y reportes
├── products/                # Catálogo de productos
├── static/                  # Archivos estáticos (CSS, JS, imágenes)
├── media/                   # Archivos subidos por usuarios
└── templates/               # Plantillas HTML
```

### 📊 Modelo de Datos Clave

- **Product**: Productos de la panadería
- **RawMaterial**: Materias primas
- **Order**: Órdenes de venta
- **OrderItem**: Detalles de productos en cada orden
- **ProductRawMaterial**: Relación productos-materias primas

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.13 o superior
- Git

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/ssabogall/Trabajo_P1.git
   cd Trabajo_P1
   ```

2. **Crear entorno virtual**
   - Para crear un entorno virtual y aislar las dependencias de tu proyecto, ejecuta los siguientes comandos:
   ```bash
   python -m venv venv

   # En Windows:
   .\venv\Scripts\Activate.ps1

   # En Linux/Mac:
   source venv/bin/activate
   ```
   - Luego de de activar la primera vez con el comando anterior  ya puedes o volver a activar con el siguiente comando

   ```bash
   # En windows:
   # (Activador)
   venv\Scripipts\activate 

   # (Desactivador)
   deactivate

   # En linux/Mac:
   # (Desactivardor)
   deactivate
   
   # O tambien puede utilizar
   user@machine:/path/to/project$


   ```
3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```


4. **Cargar datos automáticamente (opcional)**
   - Si deseas evitar ejecutar manualmente los comandos de migración y carga de datos, puedes usar el script `load_data.sh` que contiene todos los pasos necesarios para poblar la base de datos con datos iniciales.

   Para ejecutar el script de carga de datos automáticamente, simplemente ejecuta el siguiente comando en la terminal:

   ```bash
   bash load_data.sh
   ```

   Este script ejecutará:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
   - `python manage.py ad_products_db`
   - `python manage.py ad_materials_db`
   - `python manage.py ad_materialsProducts_db`

   También puedes ejecutar cada uno de esos comandos manualmente si prefieres hacerlo de forma individual.

5. **Crear superusuario (opcional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Ejecutar servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

7. **Acceder al sistema**
   - Aplicación principal: `http://127.0.0.1:8000/`
   - Panel de administración: `http://127.0.0.1:8000/adminbaneton/`

## 📚 Guía de Uso

### 🏪 **Cómo usar el Punto de Venta**

1. Navega a `/pos/` desde la página principal
2. Selecciona los productos haciendo clic en ellos
3. Elige el método de pago
4. Confirma la venta
5. La orden se registra automáticamente

### 📊 **Cómo generar Reportes Diarios**

1. Ve a "Ventas" (`/pos/orders`)
2. Haz clic en "📊 Reporte Diario"
3. Selecciona la fecha deseada
4. Visualiza las métricas:
   - Revenue total
   - Número de órdenes
   - Productos más vendidos
   - Métodos de pago utilizados

### 📦 **Gestión de Inventario**

1. Accede a `/inventory/`
2. Revisa los niveles de stock
3. Las alertas se muestran automáticamente para productos con stock bajo
4. Actualiza cantidades según sea necesario

## 🌟 Funcionalidades Destacadas

### PB-02: Reportes Diarios Automáticos ✅
- **Generación automática** de reportes al final de cada día
- **Métricas completas**: Revenue, órdenes, productos más vendidos
- **Interfaz intuitiva** con gráficos y tablas
- **Exportación e impresión** de reportes

### Sistema de Alertas de Inventario
- Notificaciones automáticas para stock bajo
- Configuración personalizable de umbrales mínimos
- Vista centralizada de alertas críticas

## 🤝 Contribuir al Proyecto

### Estructura de Ramas
- `main`: Rama principal estable
- `simon`: Rama de desarrollo con características avanzadas
- `santiago2`: Ramas para nuevas funcionalidades

### Flujo de Desarrollo
1. Crear rama desde `main`
2. Desarrollar la funcionalidad
3. Hacer commit con mensajes descriptivos
4. Crear Pull Request hacia `main`

## 📝 Próximas Funcionalidades

- [ ] Sistema de usuarios y roles
- [ ] Reportes semanales y mensuales
- [ ] Integración con sistemas de pago
- [ ] API REST para integración externa
- [ ] Dashboard ejecutivo con métricas avanzadas
- [ ] Sistema de notificaciones push
- [ ] Gestión de proveedores

## 🐛 Solución de Problemas Comunes

### Error de Migración
```bash
python manage.py makemigrations
python manage.py migrate
```

### Problemas con Archivos Estáticos
```bash
python manage.py collectstatic
```

### Resetear Base de Datos
```bash
rm db.sqlite3
python manage.py migrate
```

## 📞 Contacto y Soporte

**Equipo de Desarrollo:**
- Universidad EAFIT - Ingeniería de Sistemas
- Proyecto Integrador 1

**Recursos Adicionales:**
- Documentación Django: https://docs.djangoproject.com/
- Bootstrap: https://getbootstrap.com/docs/

---

## 🏆 Logros del Proyecto

✅ **Arquitectura sólida** con patrón MVT  
✅ **Funcionalidades core** completamente implementadas  
✅ **Reportes automáticos** (PB-02) funcionando  
✅ **Interfaz responsiva** con Bootstrap  
✅ **Base de datos optimizada** con relaciones apropiadas  
✅ **Gestión de inventario** con alertas automáticas  

---

*"Baneton - Simplificando la gestión de tu panadería, un producto a la vez."* 🥖✨
