import pvporcupine
import numpy as np

ACCES_KEY = 'w7aJDJRJbNPpMyQlB0v4JOGOJH8xQ/tJuDZEblhzMYFcBviP4/CL+w=='
keyword_path = 'porcupine/Alessia_es_raspberry-pi_v2_1_0.ppn'
model_path = 'porcupine/porcupine_params_es.pv'


alessia = pvporcupine.create(
    access_key=ACCES_KEY, 
    model_path = model_path, 
    keyword_paths=[keyword_path],
    sensitivities=[0.5])


def wait_for_keywoard(stream, FRAMES_PER_BUFFER):
    while True:
        data = stream.read(FRAMES_PER_BUFFER)
        # Convert to int16
        data = np.frombuffer(data, dtype=np.int16)
        keywordIndex = alessia.process(data)
        if keywordIndex == 0:
            break