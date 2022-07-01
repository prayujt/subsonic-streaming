import libsonic
import requests
from dotenv import dotenv_values

config = dotenv_values()

connection = libsonic.Connection(config['SUBSONIC_URL'], config['SUBSONIC_USERNAME'], config['SUBSONIC_PASSWORD'], config['SUBSONIC_PORT'])
connection.startScan()
