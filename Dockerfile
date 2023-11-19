FROM arm64v8/python:3.12.0-bookworm
# Needed to install picamera
ENV READTHEDOCS=True
# Install picamera
RUN pip install picamera --break-system-packages
# Copy the code into the container and run it.
COPY nightwatch.py ./
ENTRYPOINT ["python","./nightwatch.py"]