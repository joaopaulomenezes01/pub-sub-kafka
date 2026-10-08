
import json
import logging
import os
import urllib.parse
import urllib.request

from confluent_kafka import Consumer, KafkaError

TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': text}).encode('utf-8')
    try:
        with urllib.request.urlopen(url, data=data, timeout=10) as resp:
            logging.warning(f"Telegram respondeu {resp.status}")
    except Exception as e:
        logging.error(f"Falha ao enviar pro Telegram: {e}")


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
        if msg.error():
            code = msg.error().code()
            # o tópico só passa a existir depois da primeira publicação
            if code in (KafkaError._PARTITION_EOF, KafkaError.UNKNOWN_TOPIC_OR_PART):
                continue
            logging.error('Error occured: {0}'.format(msg.error().str()))
            continue

        data = json.loads(msg.value())
        text = f"O arquivo {data['file']} foi {data['operation']}."
        logging.warning(f"NOTIFICANDO: {text}")
        send_telegram(text)

except KeyboardInterrupt:
    pass
finally:
    c.close()
