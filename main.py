from fastapi import FastAPI

app = FastAPI()

@app.get('/') # instead of app.route
def index():
	return {'key':'value'}