import ampache
import requests
from dotenv import dotenv_values

config = dotenv_values()

catalog_id = 3
client = ampache.API()

passphrase = client.encrypt_string(config['API_KEY'], 'prayuj')
auth = client.handshake('http://prayujt.com:1025', passphrase)

client.catalog_action('add_to_catalog', catalog_id)
client.catalog_action('verify_catalog', catalog_id)
client.catalog_action('clean_catalog', catalog_id)
