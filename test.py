import asyncio
import logging

import grpc
import translate_pb2
import translate_pb2_grpc

async def run() -> None:
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = translate_pb2_grpc.VoTranslateStub(channel)
        response = await stub.DownloadTranslation(translate_pb2.Link(link="https://www.youtube.com/watch?v=X98VPQCE_WI"))
    print(response)
    print("Greeter client received: " + response.filename)


if __name__ == "__main__":
    logging.basicConfig()
    asyncio.run(run())
