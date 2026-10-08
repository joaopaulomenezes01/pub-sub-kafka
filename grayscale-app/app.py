from PIL import Image, ImageOps
from confluent_kafka import Consumer, Producer, KafkaError
import json
import os
from time import sleep
import logging

OUT_FOLDER = '/processed/grayscale/'
NEW = '_grayscale'
IN_FOLDER = "/appdata/static/uploads/"

### Producer (avisa o notificador quando termina)
p = Producer({'bootstrap.servers': 'kafka1:19091,kafka2:19092,kafka3:19093'})


def notify(filename, operation):
    msg = {'file': filename, 'operation': operation}
    p.produce('notificacao', json.dumps(msg).encode('utf-8'))
    p.flush()


def create_grayscale(path_file):
    pathname, filename = os.path.split(path_file)
    output_folder = pathname + OUT_FOLDER

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    original_image = Image.open(path_file)
    gray_image = ImageOps.grayscale(original_image)

    name, ext = os.path.splitext(filename)
    gray_image.save(output_folder + name + NEW + ext)

#sleep(30)
### Consumer
c = Consumer({
    'bootstrap.servers': 'kafka1:19091,kafka2:19092,kafka3:19093',
    'group.id': 'grayscale-group',
    'client.id': 'client-1',
    'enable.auto.commit': True,
    'session.timeout.ms': 6000,
    'default.topic.config': {'auto.offset.reset': 'smallest'}
})

c.subscribe(['image'])
#{"timestamp": 1649288146.3453217, "new_file": "9PKAyoN.jpeg"}

try:
    while True:
        msg = c.poll(0.1)
        if msg is None:
            continue
        elif not msg.error():
            data = json.loads(msg.value())
            filename = data['new_file']
            logging.warning(f"READING {filename}")
            create_grayscale(IN_FOLDER + filename)
            notify(filename, 'convertido para preto e branco')
            logging.warning(f"ENDING {filename}")
        elif msg.error().code() == KafkaError._PARTITION_EOF:
            logging.warning('End of partition reached {0}/{1}'
                  .format(msg.topic(), msg.partition()))
        else:
            logging.error('Error occured: {0}'.format(msg.error().str()))

except KeyboardInterrupt:
    pass
finally:
    c.close()
