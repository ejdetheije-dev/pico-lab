"""CSV-logger voor metingen op de Pico-flash.

De Pico 2W heeft 2 MB flash. Deze logger bewaakt een maximale bestandsgrootte
en gebruikt de RTC als die staat ingesteld; anders een monotone teller.
"""

import os
import time


class CsvLogger:
    """Schrijf metingen naar een CSV-bestand op de flash."""

    def __init__(self, path, header, max_bytes=200_000):
        """Maak een logger met header (lijst van kolomnamen).

        max_bytes: zachte limiet. Boven deze grens wordt niet meer geschreven
        en geeft `log()` False terug.
        """
        self.path = path
        self.max_bytes = max_bytes
        self._counter = 0
        if not self._exists(path):
            with open(path, "w") as f:
                f.write(",".join(header) + "\n")

    def _exists(self, path):
        try:
            os.stat(path)
            return True
        except OSError:
            return False

    def _size(self):
        try:
            return os.stat(self.path)[6]
        except OSError:
            return 0

    def _timestamp(self):
        """ISO-achtige tijd uit RTC, of teller als RTC niet is ingesteld."""
        y, mo, d, h, mi, s, *_ = time.localtime()
        if y < 2024:
            self._counter += 1
            return str(self._counter)
        return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
            y, mo, d, h, mi, s
        )

    def log(self, *values):
        """Voeg een rij toe. Geeft False bij overschreden maxgrootte."""
        if self._size() >= self.max_bytes:
            return False
        row = [self._timestamp()] + [str(v) for v in values]
        with open(self.path, "a") as f:
            f.write(",".join(row) + "\n")
        return True
