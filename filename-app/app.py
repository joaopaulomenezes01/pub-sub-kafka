from PIL import Image, ImageDraw, ImageFont
from confluent_kafka import Consumer, KafkaError
import json
import os
import logging

OUT_FOLDER = '/processed/filename/'
NEW = '_filename'
IN_FOLDER = "/appdata/static/uploads/"


def write_filename(path_file):
    pathname, filename = os.path.split(path_file)
    output_folder = pathname + OUT_FOLDER

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image = Image.open(path_file)
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")

    draw = ImageDraw.Draw(image)

    # tamanho da letra proporcional a largura da imagem
    font_size = max(16, image.width // 20)
    try:
        font = ImageFont.load_default(size=font_size)
    except TypeError:
        # versoes antigas do Pillow nao aceitam o parametro size
        font = ImageFont.load_default()

    # escreve o nome do arquivo no canto superior esquerdo, com fundo preto
    x, y = 10, 10
    left, top, right, bottom = draw.textbbox((x, y), filename, font=font)
    draw.rectangle((left - 5, top - 5, right + 5, bottom + 5), fill="black")
    draw.text((x, y), filename, fill="white", font=font)

    name, ext = os.path.splitext(filename)
    image.save(output_folder + name + NEW + ext)


### Consumer
c = Consumer({
    'bootstrap.servers': 'kafka1:19091,kafka2:19092,kafka3:19093',
    'group.id': 'filename-group',
    'client.id': 'client-1',
    'enable.auto.commit': True,
    'session.timeout.ms': 6000,
    'default.topic.config': {'auto.offset.reset': 'smallest'}
})

c.subscribe(['image'])

try:
    while True:
        msg = c.poll(0.1)
        if msg is None:
            continue
        elif not msg.error():
            data = json.loads(msg.value())
            filename = data['new_file']
            logging.warning(f"READING {filename}")
            write_filename(IN_FOLDER + filename)
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
