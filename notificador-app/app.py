import json
import os
import logging
import urllib.parse
import urllib.request

from confluent_kafka import Consumer, KafkaError

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': text}).encode()
    request = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(request, timeout=10) as response:
        response.read()


### Consumer
c = Consumer({
    'bootstrap.servers': 'kafka1:19091,kafka2:19092,kafka3:19093',
    'group.id': 'notificador-group',
    'client.id': 'client-1',
    'enable.auto.commit': True,
    'session.timeout.ms': 6000,
    'default.topic.config': {'auto.offset.reset': 'smallest'}
})

c.subscribe(['notificacao'])

try:
    while True:
        msg = c.poll(0.1)
        if msg is None:
            continue
        elif not msg.error():
            data = json.loads(msg.value())
            text = f"O arquivo {data['file']} foi {data['operation']}."
            logging.warning(f"SENDING: {text}")
            try:
                send_telegram(text)
            except Exception as e:
                logging.error(f"Falha ao enviar para o Telegram: {e}")
        elif msg.error().code() == KafkaError._PARTITION_EOF:
            logging.warning('End of partition reached {0}/{1}'
                  .format(msg.topic(), msg.partition()))
        elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
            # o topico so existe depois da primeira mensagem publicada
            continue
        else:
            logging.error('Error occured: {0}'.format(msg.error().str()))

except KeyboardInterrupt:
    pass
finally:
    c.close()
