"""Read Zigbee2MQTT Cube JSON; never publish device commands."""
import argparse
from datetime import datetime, timezone
import getpass
import json
import os
from pathlib import Path


def decode_event(raw):
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError('Payload must be a JSON object')
    return {k: data.get(k) for k in ('action', 'side', 'operation_mode', 'linkquality', 'battery')}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=1883)
    p.add_argument('--topic', default='zigbee2mqtt/VTT')
    p.add_argument('--username')
    p.add_argument('--tls', action='store_true', help='Use system trusted CA; set broker TLS port separately')
    p.add_argument('--output', default='cube_events.jsonl')
    p.add_argument('--demo', action='store_true', help='Offline synthetic data, no MQTT connection')
    args = p.parse_args()
    output = Path(args.output)
    def record(raw, topic, retained=False, synthetic=False):
        try:
            event = decode_event(raw)
        except (ValueError, UnicodeError) as exc:
            print('Skip invalid payload:', exc)
            return
        row = dict(time_utc=datetime.now(timezone.utc).isoformat(), topic=topic,
                   retained=bool(retained), synthetic=synthetic, **event)
        print(json.dumps(row, ensure_ascii=False))
        with output.open('a', encoding='utf-8') as f:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    if args.demo:
        for side in (5, 6):
            record(json.dumps({'action': 'flip_to_side', 'side': side}),
                   args.topic, synthetic=True)
        return
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        p.error('Install dependencies: py -m pip install -r requirements.txt')
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if args.username:
        password = os.environ.get('MQTT_PASSWORD')
        if password is None:
            password = getpass.getpass('MQTT password: ')
        client.username_pw_set(args.username, password)
    if args.tls:
        client.tls_set()
    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print('MQTT connection rejected:', reason_code)
            return
        print('Connected; subscribing to', args.topic)
        client.subscribe(args.topic, qos=0)
    def on_message(client, userdata, message):
        record(message.payload, message.topic, message.retain)
    client.on_connect = on_connect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=30)
    try:
        client.connect(args.host, args.port, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        print('Stopped.')
    except OSError as exc:
        p.exit(1, f'MQTT/file error: {exc}\n')
    finally:
        client.disconnect()


if __name__ == '__main__':
    main()
