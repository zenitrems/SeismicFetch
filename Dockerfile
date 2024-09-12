FROM python:3.11.9-alpine

# Install system dependencies and create the user and group
RUN apk --no-cache update && apk --no-cache upgrade && \
    apk --no-cache add bash gcc musl-dev libffi-dev openssl-dev

# Create a non-root user and set permissions
RUN addgroup -S seismic && adduser -S seismic -G seismic

# Set working directory and ensure proper ownership
RUN mkdir -p /opt/seismicfetch && chown -R seismic:seismic /opt/seismicfetch
WORKDIR /opt/seismicfetch

# Set the user context
USER seismic

# Copy the application code and set correct permissions
COPY --chown=seismic:seismic . .

# install dependencies
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt


CMD [ "python3", "main.py" ]