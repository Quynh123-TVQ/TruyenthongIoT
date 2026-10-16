"""Optional integration-test broker, not the required production Mosquitto setup."""
import asyncio,signal
from amqtt.broker import Broker
async def main():
 broker=Broker({'listeners':{'default':{'type':'tcp','bind':'127.0.0.1:18884'}},'plugins':{'amqtt.plugins.authentication.AnonymousAuthPlugin':{'allow_anonymous':True}}})
 await broker.start();print('READY MQTT 18884',flush=True)
 stop=asyncio.Event();asyncio.get_running_loop().add_signal_handler(signal.SIGTERM,stop.set)
 await stop.wait();await broker.shutdown()
asyncio.run(main())
