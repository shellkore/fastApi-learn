from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn
import base64

from ImageSteganography import hideData, showData

app = FastAPI()

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

if __name__ == '__main__':
	uvicorn.run(app)

# gunicorn
# uvloop
# httptools
# numpy