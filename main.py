import asyncio, websockets, json
import requests, tls_client, time
import markdown, re
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

token = ""

def extract_emoji(text):
    emoji_regex = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    emoji_list = emoji_regex.findall(text)
    text_without_emoji = emoji_regex.sub('', text)
    return text_without_emoji, emoji_list

def extract_mention(text):
    mention = None
    if "<@" in text:
        for word in text.split():
            if word.startswith("<@"):
                mention = word
                text = text.replace(mention, "")
                break
    return text.strip(), mention

def has_markdown(text):
    html = markdown.markdown(text).replace('<p>', 'r').replace('</p>', '')
    if '<' in html and '>' in html:
        return True
    else:
        return False

def create_image(text):
    font = ImageFont.truetype('arial.ttf', size=30)
    lines = text.split('\n')

    max_width = max(font.getsize(line)[0] for line in lines)
    total_height = sum(font.getsize(line)[1] for line in lines)

    image_size = (max_width + 50, total_height + 50)
    image = Image.new('RGB', image_size, color='white')

    draw = ImageDraw.Draw(image)
    y = 25
    for line in lines:
        text_width, text_height = font.getsize(line)
        x = (image_size[0] - text_width) / 2
        draw.text((x, y), line, font=font, fill='black')
        y += text_height

    return image

async def read_messages():
    async with websockets.connect('wss://gateway.discord.gg/?v=9&encoding=json') as websocket:
        await websocket.send(json.dumps(
            {"op":2,"d":{"token":token,"capabilities":8189,"properties":{"os":"Windows","browser":"Chrome","device":"","system_locale":"fr-FR","browser_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36","browser_version":"111.0.0.0","os_version":"10","referrer":"","referring_domain":"","referrer_current":"","referring_domain_current":"","release_channel":"stable","client_build_number":185832,"client_event_source":None,"design_id":0},"presence":{"status":"online","since":0,"activities":[],"afk":False},"compress":False,"client_state":{"guild_versions":{},"highest_last_message_id":"0","read_state_version":0,"user_guild_settings_version":-1,"user_settings_version":-1,"private_channels_version":"0","api_code_version":0}}}
        ))

        response = await websocket.recv()

        print('Ready')

        while True:
            response = await websocket.recv()
            if response:
                message_data = json.loads(response)
                if message_data['op'] == 0 and message_data['t'] == 'MESSAGE_CREATE' and message_data['d']['author']['id'] == '1091029190263976007':
                    started = time.time()
                    content = message_data['d']['content']
                    channelId = message_data['d']['channel_id']
                    msgId = message_data['d']['id']

                    if content != "" and "᲼᲼" not in content and not has_markdown(content):
                        content, mention = extract_mention(content)
                        content, emojiInC = extract_emoji(content)

                        image = create_image(content)
                        image_bytes = BytesIO()
                        image.save(image_bytes, format='PNG')
                        image_bytes.seek(0)

                        client = tls_client.Session(client_identifier="chrome_111")

                        headers = {
                            'authority': 'discord.com',
                            'accept': '*/*',
                            'accept-language': 'fr-FR,fr;q=0.9',
                            'authorization': token,
                            'content-type': 'application/json',
                            'origin': 'https://discord.com',
                            'referer': 'https://discord.com/channels/@me/' + channelId,
                            'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
                            'sec-ch-ua-mobile': '?0',
                            'sec-ch-ua-platform': '"Windows"',
                            'sec-fetch-dest': 'empty',
                            'sec-fetch-mode': 'cors',
                            'sec-fetch-site': 'same-origin',
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
                            'x-debug-options': 'bugReporterEnabled',
                            'x-discord-locale': 'fr',
                            'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImZyLUZSIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExMS4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTExLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjE4NTgzMiwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbCwiZGVzaWduX2lkIjowfQ==',
                        }

                        client.delete(
                            f'https://discord.com/api/v9/channels/{channelId}/messages/{msgId}',
                            headers=headers
                        )

                        response = client.post(
                            f'https://discord.com/api/v9/channels/{channelId}/attachments',
                            headers=headers,
                            json={
                                'files': [
                                    {
                                        'filename': 'clown.png',
                                        'file_size': len(image_bytes.getbuffer()),
                                        'id': '100',
                                    },
                                ],
                            },
                        )
                        uploadUrl = response.json()['attachments'][0]['upload_url']
                        uploadFileName = response.json()['attachments'][0]['upload_filename']
                        response = requests.put(
                            uploadUrl,
                            data=image_bytes,
                            headers={'Content-Type': 'image/png'}
                        )

                        payload = {
                                'content': '',
                                'channel_id': channelId,
                                'type': 0,
                                'sticker_ids': [],
                                'attachments': [
                                    {
                                        'id': '0',
                                        'filename': 'clown.png',
                                        'uploaded_filename': uploadFileName,
                                    },
                                ],
                        }

                        if mention != None:
                            payload['content'] = f"{mention} "
                        
                        if len(emojiInC) != 0:
                            for emote in emojiInC:
                                payload['content'] += f" {emote}"
                            payload['content'] += "\n"

                        if len(message_data['d']['attachments']) > 0:
                            for attachment in message_data['d']['attachments']:
                                payload['content'] += f"\n{attachment['url']}"
                        
                        payload['content'] += "\n᲼᲼"

                        if message_data['d']['referenced_message'] != None:
                            payload['message_reference'] = {
                                'channel_id': message_data['d']['referenced_message']['channel_id'],
                                'message_id': message_data['d']['referenced_message']['id']
                            }

                        response = client.post(
                            f'https://discord.com/api/v9/channels/{channelId}/messages',
                            headers=headers,
                            json=payload
                        )
                        if response.status_code == 200:
                            print(f'Sended Message "{content}" in {round(time.time()-started,3)}s')
                        else:
                            if "retry_after" in response.json():
                                time.sleep(response.json()['retry_after'])
                                client.post(
                                    f'https://discord.com/api/v9/channels/{channelId}/messages',
                                    headers=headers,
                                    json=payload
                                )
                            else:
                                print(response.text)
                                print(response.status_code)



asyncio.get_event_loop().run_until_complete(read_messages())
