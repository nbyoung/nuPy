import configuration
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
import os
import tmp

async def consumer(status, name):
    for i in range(5):
        async with status.watcher as watcher:
            number = await watcher.get('object.subobject.integer')
            print('  % 5d %s' % (number, name))
        await asyncio.sleep((number % 5) / 3)

async def producer(status, name, factor):
    for i in range(5):
        async with status.setter as setter:
            number = await setter.get('object.subobject.integer')
            product = number * factor
            print('%s: % 5d * %d = % 6d' % (name, number, factor, product))
            setter.set('object.subobject.integer', product)
        await asyncio.sleep((number % 5) / 2)

async def _amain():
    with tmp.Path('store.json') as storePath:
        JSON = """
{
    "object":   {
        "string":       "value",
        "boolean":      false,
        "float":        1.0,
        "subobject":    {
            "integer":    2
        }
    }
}
        """
        status = configuration.Status(configuration.JSONStore(storePath, JSON))
        await asyncio.gather(
            consumer(status, 'consumerA'),
            consumer(status, 'consumerB'),
            producer(status, 'producerP', 2),
            producer(status, 'producerQ', 3),
        )

def main():
    asyncio.run(_amain())
    
main()
