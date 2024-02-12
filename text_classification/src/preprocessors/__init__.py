import logging

from pandarallel import pandarallel

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(message)s",
    level=logging.DEBUG,
    datefmt="%I:%M:%S",
)
pandarallel.initialize(progress_bar=True)
