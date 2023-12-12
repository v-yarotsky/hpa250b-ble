from bleak.uuids import normalize_uuid_16, uuid16_dict


uuid16_lookup = {v: normalize_uuid_16(k) for k, v in uuid16_dict.items()}

# Commonly known BLE characteristics
SYSTEM_ID_UUID = uuid16_lookup["System ID"]
MODEL_NBR_UUID = uuid16_lookup["Model Number String"]
DEVICE_NAME_UUID = uuid16_lookup["Device Name"]
MANUFACTURER_NAME_UUID = uuid16_lookup["Manufacturer Name String"]
PNP_ID_UUID = uuid16_lookup["PnP ID"]

# Device-specific BLE characteristics
COMMAND_UUID = normalize_uuid_16(0xFFE9)
STATE_UUID = normalize_uuid_16(0xFFE4)

# First byte for both Commands and State
PREAMBLE = 0b10100101
