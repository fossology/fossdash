# FossDash : Reporting dahsboard for Fossology and other open source tools

FossDash deploys a [Graphite](https://hub.docker.com/r/graphiteapp/docker-graphite-statsd)/[Grafana](https://hub.docker.com/r/grafana/grafana/) stack that will collect metrics produced by a Fossology instance, and possibly other tools.

This project is **work in progress**, and is made available under the MIT License.

# Introduction
In Fossology, a cron-scheduled exporter script publishes data regularly to the FossDash service, which collects, stores in the InfluxDB database. 
See this branch for the implementation of the exporter: [dev/fossdash-exporter](https://github.com/Orange-OpenSource/fossology/tree/dev/fossdash-exporter)

A default dashboard is available in Grafana that lets you visualize the data straight away.

For the moment, the metrics produced by Fossology and graphed by Grafana are about **Fossology usage** (number of scans, users, etc) and are exported daily.
But FossDash can also be used for real-time system metrics.

FossDash is designed to be accessible behind a single http access, both to browse the Grafana interface and to publish the metrics. An Apache reverse proxy is configured to redirect trafic such as:
- `http://fossdash/grafana` points to Grafana
- `http://fossdash/influxdb` is used to POST metrics

The docker-compose file and Grafana/Influx DB are configured to be used on the same server as Fossology, also delpoyed with Docker, for simplicity - but both services can be hosted on separate servers.

Grafana allows the configuration of anonymous users, see the `grafana.ini` file and
the documentation on [anonymous-authentication](https://grafana.com/docs/grafana/latest/auth/overview/#anonymous-authentication)

# How to run

- Edit the `.env` file next to docker compose and provide required environment variables:

```sh
GF_SERVER_ROOT_URL=<full-url>
GF_SERVER_DOMAIN=<server-domain-name>
GF_SECURITY_ADMIN_PASSWORD=<first-run-password>
```

- initialize instance

```sh
docker-compose up -p fossdash -d
```

- Data generator scripts can be used to produce random test data
- A specific Fossology version must be deployed to regularly publish metrics to the FossDash server.


# Architecture

Fossology `reporting` feature is based on cyclical reporting of the predefined metrics.
Those metrics are gathered by `Python` script.
The script reads the database configuration from `Fossology` DB config file.
Default location is set to `/usr/local/etc/fossology/Db.conf`, but it can be changed by `DB_CONFIG_FILE` environment variable. (*also see CRON)

Python script executes queries against the database, prepare the specific output format and simply print the output to standard output.
The Python script is by default executed by shell script -  `fossdash.run`, which takes the output and put it into a temporary file.
Such prepared file is being sent with `curl` to InfluxDB service URL configured by `FOSSDASH_URL` var within `docker-compose.yaml`.

Not setting the `FOSSDASH_URL` will prevent the script from running the query (it will exit after being initialized by CRON).

Above operations are scheduled in `CRON` service, which is added to `web` variant of the fossology instance, but also run if Fossology is instantiated as a `all in one` variant.


# CONFIGURATION

docker-compose.yaml

```yaml
services:
  
  web:
    image: fossology:latest
    environment:      
      - REPORTING_URL=http://influxdb:8086
      - REPORTING_DB_NAME=fossology_db
    command: web
```

- If the `FOSSDASH_URL` is not set - there will be no reporting enaled.
- If `FOSSDASH_DB_NAME` is not set - the default value will be used `fossology_db`


## CRON

The reporting is done in intervals defined in CRON job.
The file in which the CRON job is defined is `install/db/db.cron` - the file was being installed by default but it may not be ideal, as it suggests DB operations.

```
*/1 * * * * root /fossology/fossdash.run >> /tmp/fossdash.txt 2>&1
```

In above example the job is configured to run every minute.
the output of the whole operation is redirected to `/tmp/fossdash.txt`

### CRON environment

By default, a CRON triggered task have no access to the docker environment.
They need to be passed somehow to the script run by CRON.
For this there is an entry in the `docker-entrypoint.sh` script.

```sh
env|grep REPORTING > /usr/local/etc/fossology/fossdash.conf || echo "No FOSSDASH configuration found."
```

At the end there is a `fossdash.conf` file created, with values of environment variables containing `FASSDASH` word.
The `fossdash.conf` is being read by the `fossdash.run` file when executed by CRON:


```sh

. /usr/local/etc/fossology/fossdash.conf

[ -z "$FOSSDASH_URL" ] && echo "Missing FOSSDASH_URL variable. Exiting." && exit 0

which python >/dev/null || exit 1
database=${FOSSDASH_DB_NAME:-fossology_db}
# ...
```

# futurer Scope
* We Can include error, fatal and warning count of fossology in a Dashboard.

# Caveats and known bugs

- The Fossology export does not work if no upload has ever been performed.
   - FIX: run a scan !

>>>>>>> master
