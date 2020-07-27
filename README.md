# Auth server

## Descripción
Este servidor será el encargado de brindar servicios de uso común como autenticación y login, tanto para el [App server](https://github.com/chotuve-grupo10/chotuve-application-server)
 como para otros que servicios que lo requieran. El objetivo de la administración de application servers es el de conocer el estado y el uso de estos. Para esto el Auth Server deberá consultar a los application servers, registrados previamente, para conocer datos acerca del uso del mismo.


## Set up para correr el auth server localmente

Para poder correr el server localmente usaremos **Docker**. A continuación detallamos los comandos a ejecutar:

1. Buildear la imagen ejecutando en el directorio raiz del repo
```docker build . -t auth-server```

2. Corremos el container ejecutando
```docker run -e GUNICORN_CMD_ARGS="--bind=0.0.0.0:8000" -p 8000:8000 auth-server```

3. Si queremos eliminar el container creado
```docker rm -f auth-server```

## Tests y linter

Tanto para ejecutar los tests y el linter, usaremos un **venv** para hacerlo. Debemos ejecutar los siguientes comandos:
1. En el directorio del repo, creamos el virtual env (solo esta vez por ser la primera):
```python3 -m venv my-venv```

2. Activamos el venv:
```source my-venv/bin/activate```

3. Instalamos las dependencias de todo el proyecto:
```pip install -e .```

## Ejecutar tests

1. Hacemos export de las variables:
 - ```export DATABASE_URL="postgres://mnigwkzorbukjg:f8d628d71867b3206dfcfa0bfd889844a5bacaf871dcafc5c72a4bd43ff16786@ec2-3-91-139-25.compute-1.amazonaws.com:5432/ddelbso61aigs8"```
 - ```export APP_SERVER_URL="https://chotuve-app-server-dev.herokuapp.com"```

2. Ejecutamos los tests:
```python -m pytest````

## Ejecutar linter

1. Ejecutar el linter en el modelo:
```PYTHONPATH=$(pwd) pylint auth_server```

2. Ejecutar el linter en los tests:
```PYTHONPATH=$(pwd) pylint tests/*.py```


## Direcciones en Heroku
- https://chotuve-auth-server-production.herokuapp.com/
- https://chotuve-auth-server-dev.herokuapp.com/
