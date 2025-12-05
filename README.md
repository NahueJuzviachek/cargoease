# CargoEase – Sistema de Gestión Logística

CargoEase es un sistema web diseñado para gestionar **vehículos, viajes, conductores, clientes, neumáticos, gastos y reportes** dentro de una empresa de transporte.  
Está desarrollado con **Python (Django)** siguiendo una arquitectura modular, escalable y fácil de mantener.


## Características principales

- Gestión completa de **vehículos**
  - Control de aceite
  - Neumáticos
  - Viajes y gastos extras
- Administración de **clientes** y **conductores**
- Módulo de **reportes** con filtros avanzados y exportación
- Dashboard con métricas y gráficos
- Sistema multi-idioma (i18n)
- APIs internas para carga dinámica de datos
- Autenticación con Django Auth
- Interfaz responsive y moderna

# Instalación

## 1)Clonar el repositorio

git clone https://github.com/NahueJuzviachek/cargoease.git 
cd cargoease

## 2) Crear y activar un entorno virtual 

python -m venv venv
venv/Scripts/activate

## 3) Instalar dependencias

pip install -r requirements.txt

## 4) Migrar la base de datos

python manage.py makemigrations
python manage.py migrate

## 5) Cargar la base datos
Cargar la base de datos con todas las aplicaciones que contengan un archivo fixture en este orden 

Py manage.py loaddata neumaticos/fixtures/neumaticos_estados.json
Py manage.py loaddata neumaticos/fixtures/neumaticos_tipos.json
Py manage.py loaddata ubicaciones/fixtures/fixture_paises.json
Py manage.py loaddata ubicaciones/fixtures/fixture_provincias.json
Py manage.py loaddata ubicaciones/fixtures/fixture_localidades.json
Py manage.py loaddata viajes/fixtures/divisas.json

## 6) Acceder al shell y crear un usuario con autenticacion para que utilice el sistema 

py manage.py shell
from django.contrib.auth.models import User
User.objects.create_user(
    username="nuevo_usuario",
    email="usuario@example.com",
    password="Password123"
)

## 7) Ejecutar en servidor local 

py manage.py runserver 


# Estructura del proyecto 
cargoease/
│── cargoease/            # Configuración del proyecto Django
│── home/                 # Dashboard, inicio, reportes
│── clientes/             # Módulo de clientes
│── conductores/          # Módulo de conductores
│── vehiculos/            # Vehículos, aceite, viajes, gastos extras
│── neumaticos/           # Gestión de neumáticos
│── static/               # CSS, JS, imágenes
│── templates/            # HTML global
│── locale/               # Traducciones (es/en)
│── requirements.txt
│── manage.py


# CargoEase fue desarrollado por 

Juzviachek Nahuel, Giraudo Leonel
