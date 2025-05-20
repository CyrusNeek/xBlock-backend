# xBlock .
xBlock application with Django and React.

# How to run the project

```
docker-compose up --build 
```

You can register an account at:
```
localhost:3000/app/pages/authentication/register-simple/test
```

Sign in:
```
localhost:3000/app
```


# Libraries 
- React - frontend
- Django Rest Framework - REST API for Django
- PostgreSQL - database
- Huey - Light weight task queue
- Redis - Task queue broker for Huey

# Lint
```
cd frontend
npx prettier --write .
```

```
docker-compose exec web black .
```

### Docs
