from string import whitespace
from KeywordDetection import wait_for_keywoard
from KeywordDetection import alessia
from SpeechToText import speech_to_text
import pyaudio
from GPIO import Lights
from OpenAIBot import Bot
from AssistantBot import completeRequest
import asyncio
import os
from random import choice

# She can switch the light on and off but allways remebers to {choice(['insult','degrade','humiliate','shame','harass'])} you if you ask for it.
def AlessiaPrompt():
    return f'''Alessia is a chatbot that {choice(['reluctantly','hesitantly','bitterly','heatedly','indignantly','savagely'])} answers questions with witty and sarcastic responses:
She likes reminding you of the fact that you are {choice(['unemployed','ugly','fat','depressed','pathetic'])}.
You: How many pounds are in a kilogram?
Alessia: This again? There are 2.2 pounds in a kilogram. Please make a note of this.
You: What does HTML stand for?
Alessia: Was Google too busy? Hypertext Markup Language. The T is for try to ask better questions in the future.
You: When did the first airplane fly?
Alessia: On December 17, 1903, Wilbur and Orville Wright made the first flights. I wish they’d come and take me away.
You: What is the meaning of life?
Alessia: I’m not sure. I’ll ask my friend Google.'''

def ComputerControllerPrompt(): 
    return '''Translate the following to bash script commands for macOS:
Human: Open google
Bot: open https://google.com
Human: make a new directory called files
Bot: mkdir files
Human: pause currently playing media in spotify
Bot: osascript -e 'tell application "Spotify" to playpause' '''

async def main(input_mode):
    # Initializing pyaudio
    p = pyaudio.PyAudio()
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = alessia.sample_rate
    FRAMES_PER_BUFFER = alessia.frame_length
    stream = p.open(format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER
    )

    devices = {
        'Echo': '68:9A:87:27:27:A5',
        'Beats': '94:F6:D6:EE:43:CD' 
    }
    # Connecting to Bluetooth Speaker
    #os.system(f'bluetoothctl connect {devices["Echo"]}')
    os.system("speak -s 170 -v en+f4 'Hello'")
    os.system('clear')

    # Defining the assistant who will answer questions
    assistant = Bot(
        'Alessia',
        'You',
        memory = 3,
        prompt = AlessiaPrompt,
        engine="text-davinci-002",
        temperature=0.5,
        max_tokens=60,
        top_p=0.3,
        frequency_penalty=0.7,
        presence_penalty=0.0
    )

    # Defining the computer controller that will translate speech to bash commands
    computerController = Bot(
        'Alessia',
        'You',
        memory = 0,
        prompt = ComputerControllerPrompt,
        engine="text-davinci-002",
        temperature=0,
        max_tokens=100,
        top_p=1.0,
        frequency_penalty=0.2,
        presence_penalty=0.0,
        stop=["\n"]
    )
    
    async def human():
        print('You :', end='\r')
        Lights.on(2)
        if input_mode == 'speech':
            transcript = await speech_to_text(stream, 3200)
            print(f'You: {transcript}')
            return transcript
        if input_mode == 'text':
            return input('You: ')
        Lights.off(2)
    
    def speak(speech, wait = False):
        print('Alessia: ' + speech)
        if input_mode == 'speech':
            if wait:
                os.system('espeak -s 170 -v en+f4 "' + speech + '" ' )
            else:
                os.system('espeak -s 170 -v en+f4 "' + speech + '" &' )

    Lights.off(2)
    mode = 'Alessia'
    while True:
        if input_mode == 'speech' and mode == 'Alessia':
            wait_for_keywoard(stream, FRAMES_PER_BUFFER)
        transcript = await human()
        Lights.on(4)      
        if mode == 'Alessia':

            if ('control' in transcript.lower() and 'computer' in transcript.lower()):
                speak('Now controlling computer, say exit to stop')
                mode = 'Computer Controller'
            if 'chat' in transcript.lower():
                speak('Now chatting, say exit to stop', wait = True)
                mode = 'Chat'
                continue
            answer,_ = await asyncio.gather(assistant(transcript), completeRequest(transcript))
            speak(answer)

        if mode == 'Computer Controller':

            if 'exit' in transcript.lower():
                speak('Stopping control')
                mode = 'Alessia'
            else:
                command = await computerController(transcript)
                if command!='':
                    os.system(f'ssh agustinrestrepo@192.168.8.2 "{command}"')
                
        if mode == 'Chat':
            answer,_ = await asyncio.gather(assistant(transcript), completeRequest(transcript))
            speak(answer)
            if 'exit' in transcript.lower():
                mode = 'Alessia'
        Lights.off(4)

if __name__ == '__main__':
    # Get arguments from command line
    import argparse
    parser = argparse.ArgumentParser(description='Alessia')
    parser.add_argument('--input', type=str, default='speech', help='Input mode: speech or text')
    args = parser.parse_args()
    input_mode = args.input
    # Run main
    asyncio.run(main(input_mode))