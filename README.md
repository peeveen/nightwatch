# nightwatch

Daft little python program to keep an eye on a room (via `picamera`).

- Saves JPEG images periodically.
- Discards images if they do not differ sufficiently (in size) from the previous one ... saves disk space.
- Deletes data after so-many days.
