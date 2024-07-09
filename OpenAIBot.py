import os
import openai
openai.api_key = 'YOUR_API_KEY'



class Bot():
    def __init__(self, botName, humanName, memory = 0, **openai_params):
        self.openai_params = openai_params
        self.memory = memory
        self.prompt = self.openai_params.pop('prompt')        
        self.lines = []
        self.botName = botName
        self.humanName = humanName

    async def __call__(self, transcript):
        # Asking Question from transcript 
        self.lines.append(f'{self.humanName}: '+transcript)

        # Building Prompt for OpenAIAPI
        prompt = self.getConversation() + '\n' + f'{self.botName}:'

        # Writing prompt for debugging
        with open('conversation.txt', 'w') as f:
            f.write(prompt)

        # Calling OpenAIAPI
        response = openai.Completion.create(
            prompt = prompt,
            **self.openai_params,
        )
        answer = response.choices[0].text.replace('\n', ' ')
        self.lines.append(f'{self.botName}: '+answer)
        return answer
    
    def getConversation(self):
        return self.prompt() + '\n' + '\n'.join(self.lines[-2*(self.memory+1):])