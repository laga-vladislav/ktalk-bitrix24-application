# Import necessary libraries
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

from crest import CRest


# Define FastAPI app
app = FastAPI()


# Define request model for adding contact
class Contact(BaseModel):
    name: str
    last_name: str
    email: str
    phone: str


@app.get("/index")
async def add_contact():
    contact = Contact(
        name="Отец", last_name="Григорий", email="fdfds@gmail.com", phone="92992"
    )
    result = CRest.call(
        method="crm.contact.add",
        params={
            'FIELDS': {
                'NAME': contact.name,
                'LAST_NAME': contact.last_name,
                'EMAIL': [{'VALUE': contact.email, 'VALUE_TYPE': 'WORK'}],
                'PHONE': [{'VALUE': contact.phone, 'VALUE_TYPE': 'WORK'}],
            }
        },
    )
    return result


@app.get("/check_server")
async def check_server():
    return CRest.check_server()


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app='main:app', host="127.0.0.1", port=8000, reload=True)
