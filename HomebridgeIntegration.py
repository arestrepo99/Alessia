import aiohttp
import asyncio
# Senf an http post request to http://pi.local:8581/api/auth/login with json data
# HOMEBDRIGE_AUTH_DATA = {
auth_data = {
    # "username": '',
    # "password": '',
    # "opt": "string"
}

# asyncronously await a response from server http://pi.local:8581/api/auth/login
async def getAccessToken():
    async with aiohttp.ClientSession() as session:
        async with session.post('http://pi.local:8581/api/auth/login', json=auth_data) as response:
            response = await response.json()
            access_token = response['access_token']
            return access_token

async def getUniqueID(access_token):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://pi.local:8581/api/accessories',headers = {'Authorization': f'Bearer {access_token}'}) as response:
            response = await response.json()
            uniqueID = {resp['serviceName']:resp['uniqueId'] for resp in response}
            return uniqueID

access_token = asyncio.run(getAccessToken())
uniqueID = asyncio.run(getUniqueID(access_token))

# turn to async
async def setServiceValue(serviceName, value):
    async with aiohttp.ClientSession() as session:
        async with session.put(f'http://pi.local:8581/api/accessories/{uniqueID[serviceName]}', 
        headers={'Authorization': f'Bearer {access_token}'},
        json={
            "characteristicType": "On",
            "value": value
        }) as response:
            response = await response.json()
            return response

async def completeRequest(request):
    # If 'light' or 'lights' in request, return 'on'
    if 'light' in request.lower():
        for serviceName in uniqueID.keys():
            if serviceName.lower() in request.lower():
                if 'on' in request:
                    await setServiceValue(serviceName, '1')
                    return
                if 'off'in request:
                    await setServiceValue(serviceName, '0')
                    return
        if 'on' in request:
            await asyncio.gather(*[setServiceValue(serviceName, '1') for serviceName in ['Computer','Sofa']])
            return
        if 'off' in request:
            await asyncio.gather(*[setServiceValue(serviceName, '0') for serviceName in ['Computer','Sofa']])
            return

