
# SeismicFetch

**SeismicFetch** is a tool designed to fetch the latest seismic events by querying the following institutions:

- **SSN** (National Seismological Service of Mexico)
- **USGS** (United States Geological Survey)
- **EMSC** (European-Mediterranean Seismological Centre)

The retrieved seismic events are stored in a **MongoDB** database, and an automated message is generated for notification via **Telegram**.

## Building the Docker Container

To build the Docker image for SeismicFetch, use the following command:

```bash
docker buildx build --pull --rm -f "Dockerfile" -t seismicfetch "."
