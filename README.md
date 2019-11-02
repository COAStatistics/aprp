![image](https://travis-ci.org/COAStatistics/aprp.svg?branch=master)

Template used
---------------

[Smart Admin](https://wrapbootstrap.com/theme/smartadmin-responsive-webapp-WB0573SK0)


Development
---------------

Download [Docker Desktop](https://www.docker.com/products/docker-desktop) for Mac or Windows. 
[Docker Compose](https://docs.docker.com/compose) will be automatically installed. 
On Linux, make sure you have the latest version of [Compose](https://docs.docker.com/compose/install/). 

**Linux Containers**

The Linux stack uses `Python`, `Redis` for messaging and `Postgres` for storage.

Create your own `.env` file at root, e.g. using `.env.example`:
```
$ cp .env.example .env
```

Use `--build` to rebuild image, `-d` to run containers in the background :
```
$ docker-compose up
```

List the container stacks using ```make ps```:
```bash
NAMES               IMAGE                PORTS                    STATUS
beat                aprp-web                                      Up 37 seconds
worker              aprp-web                                      Up 37 seconds
web                 aprp-web             0.0.0.0:8000->8000/tcp   Up 38 seconds
db                  postgres:10-alpine   5432/tcp                 Up 39 seconds
redis               redis:4.0            6379/tcp                 Up 40 seconds
```

Initial fixtures:
```bash
make init
```

Attach django shell using ```make shell```

Use `-v` to clean volume while stop containers:
```
$ docker-compose down -v
```

Testing
---------------
Once services are up, use the command to run tests, will ignore
the tests that involve secrets:

```bash
make test
```
