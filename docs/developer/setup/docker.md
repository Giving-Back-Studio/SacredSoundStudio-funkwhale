# Develop using Docker

Funkwhale can be run in Docker containers for local development. You can work on any part of the Funkwhale codebase and run the container setup to test your changes. To work with Docker:

1. [Install Docker](https://docs.docker.com/install)
2. [Install docker compose](https://docs.docker.com/compose/install)
3. Clone the Funkwhale repository to your system.

## Set up your Docker environment

To set up your Docker environment:

1. Create a `.env` file to enable customization of your setup.

   ```sh
   touch .env
   ```

2. Add the following variables to load images and enable access to Django admin pages:

   ```text
   MEDIA_URL=http://localhost:8000/media/
   STATIC_URL=http://localhost:8000/staticfiles/
   ```

3. Create a network for federation support

   ```sh
   docker network create federation
   ```

Once you've set everything up, you are ready to run the containers. Run this command any time there are upstream changes or dependency changes to ensure you're up-to-date.

```sh
docker-compose up
```

## Hop into the api container

```sh
docker exec -it funkwhale-api bash
```

## Set up the database

Funkwhale relies on a postgresql database to store information. To set this up, you need to run the `funkwhale-manage migrate` command from within the API container:

```sh
funkwhale-manage migrate
```

This command creates all the required tables. You need to run this whenever there are changes to the API schema. You can run this at any time without causing issues.

## Set up local data

You need to create some local data to mimic a production environment.

1. Create a superuser so you can log in to your local app:

   ```sh
   funkwhale-manage fw users create --superuser
   ```

2. Populate the tags from fixtures:
   ```sh
   funkwhale-manage loaddata funkwhale_api/tags/fixtures/tags.json
   ```

## Services

You should now have access to the following:

- The Funkwhale webapp on `http://localhost:8000`
- The Funkwhale API on `http://localhost:8000/api/v1`
- The Django admin interface on `http://localhost:8000/api/admin`