import grpc
import translate_pb2
import translate_pb2_grpc


async def download_speech(link:str):
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = translate_pb2_grpc.VoTranslateStub(channel)
        return await stub.DownloadTranslation(translate_pb2.Link(link=link))
