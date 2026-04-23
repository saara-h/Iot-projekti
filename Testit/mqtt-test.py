import paho.mqtt.client as mqtt

broker = "mqtt3.thingspeak.com"
port = 1883

clientID = "HBMtAgcBATk1LA0YJDkWDjo"
username = "HBMtAgcBATk1LA0YJDkWDjo"
password = "mr7eQWX+3H2pk3pcNiBB/BQn"

channelID = "3251687"

topic = "channels/" + channelID + "/publish"

client = mqtt.Client(clientID)
client.username_pw_set(username, password)

client.connect(broker, port)

payload = "field1=25"

client.publish(topic, payload)

client.disconnect()
