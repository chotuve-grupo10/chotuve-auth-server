# chotuve-auth-server

## Set up para correr el auth server localmente

### Opción Docker

#### Docker compose

1. Para poder correr el server dockerizado lo primero que tenemos que hacer es descomentar el 
seteo de las variables de entorno del docker-compose.yml

2. Descomentar variables de entorno en el archivo docker-compose.yml

3. En el mismo archivo, en app/image reemplazar la variable de entorno con algun nombre que querramos que tenga la imagen.

4. Ejecutamos ```docker-compose build```

5. Una vez que buildeó, ejecutamos ```docker-compose up```


#### Dockerfile

1. Buildear la imagen ejecutando ```docker build . -t auth-server```

2. Corremos el container ejecutando ```docker run -e GUNICORN_CMD_ARGS="--bind=0.0.0.0:8000" -p 8000:8000 auth-server```

### Opción con virtualenv

1. Clonar el repo:  
```git clone https://github.com/chotuve-grupo10/chotuve-auth-server.git```

2. En el directorio del repo, creamos el virtual env (solo esta vez por ser la primera):  
```python3 -m venv my-venv```

3. Activamos el venv:  
```source my-venv/bin/activate```

4. Instalamos las dependencias de todo el proyecto:   
```pip install -e .```   

5. Hacemos export de las variables:
```export DATABASE_URL="postgres://mnigwkzorbukjg:f8d628d71867b3206dfcfa0bfd889844a5bacaf871dcafc5c72a4bd43ff16786@ec2-3-91-139-25.compute-1.amazonaws.com:5432/ddelbso61aigs8"```   

6. Corremos el server localmente:  
```gunicorn --log-level=debug 'auth_server:create_app()'```

## Direcciones en Heroku
- https://chotuve-auth-server-production.herokuapp.com/
- https://chotuve-auth-server-dev.herokuapp.com/
