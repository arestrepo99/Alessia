import pyaudio
import websockets
import asyncio
import base64
from GPIO import Lights
import json
auth_key = '43419e770b06499e9f8f45f81630f33b'


# the AssemblyAI endpoint we're going to hit
URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"
 
async def speech_to_text(stream, FRAMES_PER_BUFFER):
    async with websockets.connect(
        URL,
        extra_headers=(("Authorization", auth_key),),
        ping_interval=5,
        ping_timeout=20
    ) as _ws:
        await asyncio.sleep(0.1)
        session_begins = await _ws.recv()

        global active
        active = True

        async def send():
            global active
            while active:
                try:
                    data = stream.read(FRAMES_PER_BUFFER)
                    data = base64.b64encode(data).decode("utf-8")
                    json_data = json.dumps({"audio_data":str(data)})
                    await _ws.send(json_data)
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    assert False, "Not a websocket 4008 error"
                await asyncio.sleep(0.01)
            return True
        
        async def receive():
            global active
            while active:
                try:
                    result_str = await _ws.recv()
                    response = json.loads(result_str)
                    transcript = response['text']
                    
                    print(transcript, end='\r')
                    if response['message_type'] == 'FinalTranscript' and transcript!='':
                        active = False
                        return transcript
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    assert False, "Not a websocket 4008 error"
        _, transcript = await asyncio.gather(send(), receive())
        return transcript


async def get_microphone_text():
    FRAMES_PER_BUFFER = 3200
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    p = pyaudio.PyAudio()
    # starts recording
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER
    )
    await send_receive(stream)
    stream.close()

