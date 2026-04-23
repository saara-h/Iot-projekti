import paho.mqtt.client as mqtt
from datetime import datetime

TS_BROKER = "mqtt3.thingspeak.com"
TS_PORT = 1883

TS_CLIENT_ID = "HBMtAgcBATk1LA0YJDkWDjo"
TS_USERNAME = "HBMtAgcBATk1LA0YJDkWDjo"
TS_PASSWORD = "mr7eQWX+3H2pk3pcNiBB/BQn"
TS_CHANNEL_ID = "3251687"

TS_TOPIC = f"channels/{TS_CHANNEL_ID}/publish"


def connect():
    client = mqtt.Client(
        client_id=TS_CLIENT_ID,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION1
    )
    client.username_pw_set(TS_USERNAME, TS_PASSWORD)
    client.connect(TS_BROKER, TS_PORT)
    return client


def publish_event(client, known: bool, motion_time: float):
    # known -> 1/0 ThingSpeak fieldiin
    field1 = 1 if known else 0

    dt = datetime.fromtimestamp(motion_time).strftime("%Y-%m-%d %H:%M:%S")
    status = f"motion {dt}; {'known' if known else 'unknown'}"

    payload = f"field1={field1}&status={status}"
    client.publish(TS_TOPIC, payload)

def publish_noresult(client, motion_time: float):
    dt = datetime.fromtimestamp(motion_time).strftime("%Y-%m-%d %H:%M:%S")
    payload = f"status=motion {dt}; no result"
    client.publish(TS_TOPIC, payload)
