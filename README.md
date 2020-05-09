# chotuve-auth-server

## Set up para correr el auth server localmente

### Opción Docker

1. Para poder correr el server dockerizado lo primero que tenemos que hacer es descomentar el 
seteo de las variables de entorno del docker-compose.yml

2. Ejecutamos ```docker-compose build```

3. Una vez que buildeó, ejecutamos ```docker-compose up```

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
```export FLASK_APP=auth_server```   
```export FLASK_ENV=development```   

6. Corremos el server localmente:  
```flask run```

## Direcciones en Heroku
- https://chotuve-auth-server-production.herokuapp.com/
- https://chotuve-auth-server-dev.herokuapp.com/
