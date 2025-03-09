#!/usr/bin/env python

import logging
import sys
import time

import yaml

from lib.notifier import Notifier
from providers.processor import process_properties

# logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# configuration
with open("configuration.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

disable_ssl = False
if "disable_ssl" in cfg:
    disable_ssl = cfg["disable_ssl"]

notifier = Notifier.get_instance(cfg["notifier"], disable_ssl)

new_properties = []
for provider_name, provider_data in cfg["providers"].items():
    try:
        logging.info(f"Processing provider {provider_name}")
        new_properties += process_properties(provider_name, provider_data)
    except Exception as e:
        logging.error(f"Error processing provider {provider_name}.\n{str(e)}")

if len(new_properties) > 0:
    # Split properties into batches of 10
    batch_size = 10
    batches = [
        new_properties[i : i + batch_size]
        for i in range(0, len(new_properties), batch_size)
    ]

    # Send each batch with a 30-second delay
    for i, batch in enumerate(batches):
        if i > 0:
            print(
                f"Waiting 30 seconds before sending next batch ({i+1}/{len(batches)})..."
            )
            time.sleep(30)  # Wait 30 seconds between batches
        notifier.notify(batch)
