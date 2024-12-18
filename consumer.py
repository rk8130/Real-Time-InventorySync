from datetime import datetime
import threading
import json
import os

from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer



# Define Kafka configuration
kafka_config = {
    'bootstrap.servers': 'pkc-921jm.us-east-2.aws.confluent.cloud:9092',
    'sasl.mechanisms': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': 'YXVAJ4PHZNL5SVMA',
    'sasl.password': 'NWyUC/CXlmeVKB5N+ZAJb7erBDyRoLMftsXCWcs1lbH8x10l81d6F37mrS8rJNCD',
    'group.id': 'group99',
    'auto.offset.reset': 'earliest'
}

# Schema for User record value
schema_registry_client=SchemaRegistryClient({
    'url': 'https://psrc-lo3do.us-east-2.aws.confluent.cloud',
    'basic.auth.user.info': '{}:{}'.format('U2VGBECL4ZMIH54P', 'QAAP/kLS1XXOMRJ2xkViG6gslGaLVdFrR9ET5JCb2XKk2GQrHmBM6h5ASRTDRCOJ')
})

# Fetch the schema by subject name
subject_name = 'product_updates-value'
schema_str=schema_registry_client.get_latest_version(subject_name).schema.schema_str


# Avro Deserializer for User record value
key_deserializer = StringDeserializer('utf_8')
avro_deserializer = AvroDeserializer(schema_registry_client, schema_str)


# Define the DeserializingConsumer
consumer=DeserializingConsumer({
    'bootstrap.servers': kafka_config['bootstrap.servers'],
    'key.deserializer': key_deserializer,
    'value.deserializer': avro_deserializer,
    'sasl.mechanisms': kafka_config['sasl.mechanisms'],
    'security.protocol': kafka_config['security.protocol'],
    'sasl.username': kafka_config['sasl.username'],
    'sasl.password': kafka_config['sasl.password'],
    'group.id': kafka_config['group.id'],
    'auto.offset.reset': kafka_config['auto.offset.reset']
})


consumer.subscribe(['product_updates'])

file_path='consumer1.json'


# Custom function to convert datetime objects to string
def convert_datetime(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')  # Convert datetime to string
    raise TypeError("Type not serializable")


try:
    while True:
        msg = consumer.poll(1.0) 

        if msg is None:
            continue
        if msg.error():
            print('Consumer error: {}'.format(msg.error()))
            continue

        print('Successfully consumed record with key {} and value {}'.format(msg.key(), msg.value()))
        

        # Write your data manipulation logic here
        data=msg.value()
        data['category'] = data['category'].upper()

        json_string = json.dumps(data, default=convert_datetime)

        # Check if the file not exists then create the file and write the data
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(json_string)
                f.write('\n')

        else:          # If the file exists then append the data
            with open(file_path, 'a') as f:
                f.write(json_string)
                f.write('\n')
        f.close()        


except KeyboardInterrupt:
    pass
finally:
    consumer.close()