from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class City(BaseModel):
	name: str
	timezone: str

db= []

@app.get('/') # instead of app.route
def index():
	return {'key':'value'}

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