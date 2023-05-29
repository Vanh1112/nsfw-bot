from fastapi import FastAPI
import requests
import mimetypes
import os
from pydantic import BaseModel
from fastapi import Security, Depends, FastAPI, HTTPException
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from starlette.status import HTTP_403_FORBIDDEN,HTTP_500_INTERNAL_SERVER_ERROR,HTTP_400_BAD_REQUEST
from starlette.responses import RedirectResponse, JSONResponse
import urllib.request
from open_nsfw_python3 import NSFWClassifier
import os
from time import time

API_KEY = os.getenv('API_KEY')
api_key_query = APIKeyQuery(name='api_key', auto_error=False)
app = FastAPI()


global classifier, folder_to_write
classifier = NSFWClassifier()
folder_to_write = '/app/data'

class Image_Url(BaseModel):
      image_url: str

# Download image function
def download_img(url):
    supported_types = ['image/jpe','image/jpeg','image/jpg','image/png']
    start = time()
    response = requests.get(url)
    content_type = response.headers['content-type']
    if content_type not in supported_types :
        raise ValueError(f'Unsupported image type {content_type}')
    extension = mimetypes.guess_extension(content_type)
    file_name = int(round(time(), 0))
    full_path_with_ext = folder_to_write + '/'  + str(file_name) + str(extension)
    f = open(full_path_with_ext,'wb')
    f.write(response.content)
    f.close()
    return time()-start,full_path_with_ext

# Delete image function
def del_img(full_path_file):
  if os.path.exists(full_path_file):
    os.remove(full_path_file)
  else:
    print("The file does not exist")

@app.get("/ml/nsfw_detector")
async def hello(image_url:Image_Url, api_key:str=Security(api_key_query)):
    if api_key == API_KEY:
        try:
            image_url= dict(image_url)
        except:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Could not parse payload content"
            )
        url = image_url["image_url"]
        try:
            download_interval,img = download_img(url)
        except ValueError as e:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail=str(e)
            )
        except:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail=f"Could not download image from url {url}"
            )
        score = classifier.get_score(img)
        del_img(img)
        return {"score": score,'download_interval':download_interval, 'is_safe': 1 if score <0.3 else 0}
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )

