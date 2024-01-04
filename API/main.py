
import uuid
import requests
import random
import json
import time
import os
from typing import Optional


import aiohttp
from aiohttp import ClientSession, ClientTimeout

import asyncio
from asyncio            import AbstractEventLoop

from concurrent.futures import ThreadPoolExecutor


from typing import Any, AsyncGenerator, Generator, NewType, Tuple, Union, List, Dict


from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import StreamingResponse


app = FastAPI()



AsyncResult = AsyncGenerator[str, None]
Messages = List[Dict[str, str]]


class Tones():
    creative = "Creative"
    balanced = "Balanced"
    precise = "Precise"


# Parametros de configuracion 

class Defaults:
    delimiter = "\x1e"
    ip_address = f"13.{random.randint(104, 107)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

    allowedMessageTypes = [
        "ActionRequest",
        "Chat",
        "Context",
        "Progress",
        "SemanticSerp",
        "GenerateContentQuery",
        "SearchQuery",
        "RenderCardRequest",
    ]

    sliceIds = [
        'abv2',
        'srdicton',
        'convcssclick',
        'stylewv2',
        'contctxp2tf',
        '802fluxv1pc_a',
        '806log2sphs0',
        '727savemem',
        '277teditgnds0',
        '207hlthgrds0',
    ]

    location = {
        "locale": "en-US",
        "market": "en-US",
        "region": "US",
        "locationHints": [
            {
                "country": "United States",
                "state": "California",
                "city": "Los Angeles",
                "timezoneoffset": 8,
                "countryConfidence": 8,
                "Center": {"Latitude": 34.0536909, "Longitude": -118.242766},
                "RegionType": 2,
                "SourceType": 1,
            }
        ],
    }

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-full-version': '"110.0.1587.69"',
        'sec-ch-ua-full-version-list': '"Chromium";v="110.0.5481.192", "Not A(Brand";v="24.0.0.0", "Microsoft Edge";v="110.0.1587.69"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"15.0.0"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69',
        'x-edge-shopping-flag': '1',
        'x-forwarded-for': ip_address,
    }

    optionsSets = [
        'nlu_direct_response_filter',
        'deepleo',
        'disable_emoji_spoken_text',
        'responsible_ai_policy_235',
        'enablemm',
        'iyxapbing',
        'iycapbing',
        'gencontentv3',
        'fluxsrtrunc',
        'fluxtrunc',
        'fluxv1',
        'rai278',
        'replaceurl',
        'eredirecturl',
        'nojbfedge'
    ]


default_cookies = {
    'SRCHD'         : 'AF=NOFORM',
    'PPLState'      : '1',
    'KievRPSSecAuth': '',
    'SUID'          : '',
    'SRCHUSR'       : '',
    'SRCHHPGUSR'    : f'HV={int(time.time())}',
}


def format_message(msg: dict) -> str:
    delimiter = "\x1e"
    return json.dumps(msg, ensure_ascii=False) + delimiter


def create_context(messages: Messages):
    return "".join(
        f"[{message['role']}]" + ("(#message)" if message['role']!="system" else "(#additional_instructions)") + f"\n{message['content']}\n\n"
        for message in messages
    )

    
class Conversation():
    def __init__(self, conversationId: str, clientId: str, conversationSignature: str, imageInfo: dict=None) -> None:
        self.conversationId = conversationId
        self.clientId = clientId
        self.conversationSignature = conversationSignature
        self.imageInfo = imageInfo


async def create_conversation(session: ClientSession, proxy: str = None) -> Conversation:
    url = 'https://www.bing.com/turing/conversation/create?bundleVersion=1.1199.4'
    async with session.get(url, proxy=proxy) as response:
        data = await response.json()

        conversationId = data.get('conversationId')
        clientId = data.get('clientId')
        conversationSignature = response.headers.get('X-Sydney-Encryptedconversationsignature')

        if not conversationId or not clientId or not conversationSignature:
            raise Exception('Failed to create conversation.')
        conversation = Conversation(conversationId, clientId, conversationSignature, None)
        return conversation


async def delete_conversation(session: ClientSession, conversation: Conversation, proxy: str = None) -> list:
    url = "https://sydney.bing.com/sydney/DeleteSingleConversation"
    json = {
        "conversationId": conversation.conversationId,
        "conversationSignature": conversation.conversationSignature,
        "participant": {"id": conversation.clientId},
        "source": "cib",
        "optionsSets": ["autosave"]
    }
    async with session.post(url, json=json, proxy=proxy) as response:
        try:
            response = await response.json()
            return response["result"]["value"] == "Success"
        except:
            return False


def create_message(conversation: Conversation, prompt: str, tone: str, context: str = None, web_search: bool = False) -> str:
    options_sets = Defaults.optionsSets
    if tone == Tones.creative:
        options_sets.append("h3imaginative")
    elif tone == Tones.precise:
        options_sets.append("h3precise")
    elif tone == Tones.balanced:
        options_sets.append("galileo")
    else:
        options_sets.append("harmonyv3")
    if not web_search:
        options_sets.append("nosearchall")
    
    request_id = str(uuid.uuid4())
    
    # Agregar parametros adicionales a message
    msgs = Defaults.location.copy()
    msgs.update({
        'author': 'user',
        'inputMethod': 'Keyboard',
        'text': prompt,
        'messageType': 'Chat',
        'requestId': request_id,
        'messageId': request_id,
    })
    
    with open("output.txt", "w") as file:
        file.write(f"tone: {tone}\n")
    
    # Armar cuerpo json para enviar a Bing
    struct = {
        'arguments': [
            {
                'source': 'cib',
                'optionsSets': options_sets,
                'allowedMessageTypes': Defaults.allowedMessageTypes,
                'sliceIds': Defaults.sliceIds,
                'traceId': os.urandom(16).hex(),
                'isStartOfSession': True,
                'requestId': request_id,
                'message': msgs,
                "scenario": "SERP",
                'tone': tone,
                'spokenTextMode': 'None',
                'conversationId': conversation.conversationId,
                'participant': {
                    'id': conversation.clientId
                },
            }
        ],
        'invocationId': '1',
        'target': 'chat',
        'type': 4
    }
    
    # Si existen mensajes agregarlos a los parametros la peticion (CONTEXTO)
    if context:
        struct['arguments'][0]['previousMessages'] = [{
            "author": "user",
            "description": context,
            "contextType": "WebPage",
            "messageType": "Context",
            "messageId": "discover-web--page-ping-mriduna-----"
        }]
    return format_message(struct)



async def stream_generate(
        prompt: str,
        tone: str,
        image: str = None,
        context: str = None,
        proxy: str = None,
        cookies: dict = None,
        web_search: bool = False
    ):
    async with ClientSession(
            timeout=ClientTimeout(total=900),
            headers=Defaults.headers if not cookies else {**Defaults.headers, "Cookie": "; ".join(f"{k}={v}" for k, v in cookies.items())},
        ) as session:
        conversation = await create_conversation(session, proxy)

        try:
            async with session.ws_connect('wss://sydney.bing.com/sydney/ChatHub', autoping=False, params={'sec_access_token': conversation.conversationSignature}, proxy=proxy) as wss:

                await wss.send_str(format_message({'protocol': 'json', 'version': 1}))
                await wss.receive(timeout=900)
                await wss.send_str(create_message(conversation, prompt, tone, context, web_search))

                response_txt = ''
                returned_text = ''
                final = False
                while not final:
                    msg = await wss.receive(timeout=900)
                    objects = msg.data.split(Defaults.delimiter)
                    for obj in objects:
                        if obj is None or not obj:
                            continue

                        response = json.loads(obj)

                        if response.get('type') == 1 and response['arguments'][0].get('messages'):
                            message = response['arguments'][0]['messages'][0]
                            if (message['contentOrigin'] != 'Apology'):
                                if 'adaptiveCards' in message:
                                    card = message['adaptiveCards'][0]['body'][0]
                                    if "text" in card:
                                        response_txt = card.get('text')
                                    if message.get('messageType'):
                                        inline_txt = card['inlines'][0].get('text')
                                        response_txt += inline_txt + '\n'
                            if response_txt.startswith(returned_text):
                                new = response_txt[len(returned_text):]
                                if new != "\n":
                                    yield new
                                    returned_text = response_txt
                        elif response.get('type') == 2:
                            result = response['item']['result']
                            if result.get('error'):
                                raise Exception(f"{result['value']}: {result['message']}")
                            return
        finally:
            await delete_conversation(session, conversation, proxy)






def create_async_generator(
    model: str,
    messages: Messages,
    proxy: str = None,
    cookies: dict = None,
    tone: str = Tones.creative,
    #tone: str = Tones.precise,
    image: str = None,
    web_search: bool = False,
    **kwargs
) -> AsyncResult:
    if len(messages) < 2:
        prompt = messages[0]["content"]
        context = None
    else:
        prompt = messages[-1]["content"]
        context = create_context(messages[:-1])
        
    if not cookies:
        cookies = default_cookies
    else:
        for key, value in default_cookies.items():
            if key not in cookies:
                cookies[key] = value
    return stream_generate(prompt, tone, image, context, proxy, cookies, web_search)


 


@app.post("/chat1")
async def procesar(
    msj: str = Body(..., description="Mensaje a procesar"),
    model: Optional[str] = Body("gpt-4", description="Modelo a utilizar"),
    tone: Optional[str] = Body("Creative", description="Tono del procesamiento"),
    hist: Optional[str] = Body(None, description="historial de chat"),
    return_transfer: Optional[str] = Body(..., description="stream or normal"),
):
    try:
        history=[]
        if( hist is not None ):
            history = json.loads(hist)
        
        if(len(history) > 1):
             messages = []
             for msg in history:
                messages.append({'content':msg['content'], 'role':msg['role']})   
             messages.append({'content':msj, 'role':'user'})
        else:
            messages = [{"content": "Hola, estoy aquí para servirte", "role": "system"},{'role':'user','content':msj}]
        
        
        if( return_transfer == "stream"):
            # STREAM RESPONSE
            async def generateStream():
                wss = create_async_generator(model, messages, tone=tone)
                async for chunk in wss:
                    yield chunk
                await wss.aclose()

            return StreamingResponse(generateStream(), media_type="text/html")
        else:
            # NORMAL RESPONSE
            result_lines = []
            wss = create_async_generator(model, messages, tone=tone)
            async for chunk in wss:
                result_lines.append(chunk)
            await wss.aclose()

            result = "".join(result_lines)
            return {"resultado": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))