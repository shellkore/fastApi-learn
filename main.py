from fastapi import FastAPI, WebSocket, WebSocketDisconnect,Request
from pydantic import BaseModel
from typing import Optional
import uvicorn
import base64
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

from ImageSteganography import hideData, showData

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

class City(BaseModel):
	name: str
	timezone: str

class ImageInput(BaseModel):
    msg: str
    image_string: str
    pass_key: Optional[str] = None

db= []

def encrypt(msg,password):
    msgList = list(msg)
    pswdList = list(password)
    msglen = len(msgList)
    pswdlen = len(pswdList)

    pswdPos = 0
    for i in range(msglen):
        if(pswdPos==len(pswdList)):
            pswdPos=0
        msgList[i]= chr(ord(msgList[i])+ord(pswdList[pswdPos]))
        pswdPos+=1

    return (''.join(msgList))

def decrypt(msg,password):
    msgList = list(msg)
    pswdList = list(password)
    msglen = len(msgList)
    pswdlen = len(pswdList)

    pswdPos = 0
    for i in range(msglen):
        if(pswdPos==len(pswdList)):
            pswdPos=0
        msgList[i]= chr(ord(msgList[i])-ord(pswdList[pswdPos]))
        pswdPos+=1

    return (''.join(msgList))

@app.get('/') # instead of app.route
def index():
	return {'msg':'API working. Check /docs for more'}

@app.get('/cities')
def get_cities():
	return db

@app.get('/cities/{city_id}')
def get_city(city_id: int):
	return db[city_id-1]

@app.post('/cities')
def create_city(city: City): #type hints. City class is used to tell api the expected type of data
	db.append(city.dict())
	return db[-1]

@app.delete('/cities/{city_id}')
def delete_city(city_id:int): #automatic validation because of type hint set to 'int'
	deleted = db[city_id-1]
	db.pop(city_id-1)
	return {'delted': deleted}

@app.get('/items/{item_id}')
async def get_item(item_id: int, q: Optional[str] = None):
	return {'item_id':item_id,'q':q}

@app.post('/imgencode')
async def img_encode(data:ImageInput):
    imageName = 'image/input1.png'
    imgdata = base64.b64decode(data.image_string)
    print(data.msg)
    # print(type(pass_key))
    print(data.pass_key)
    with open (imageName,'wb') as imgFile:
        imgFile.write(imgdata)
    return "done"

@app.post('/imgdecode')
async def img_decode(key: Optional[str] = None):
	imageName = 'image/output.png'
	res = showData(imageName)
	newRes = decrypt(res,key)
	return newRes

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/chat",response_class=HTMLResponse)
async def chat_websocket(request: Request):
    return templates.TemplateResponse("chat.html",{"request": request})


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{client_id} left the chat")

if __name__ == '__main__':
    uvicorn.run(app,host='0.0.0.0')

# gunicorn
# uvloop
# httptools
# numpy