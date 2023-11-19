FROM benchpilot/raspbian-picamera2
COPY nightwatch.py ./
ENTRYPOINT ["python3","./nightwatch.py"]
