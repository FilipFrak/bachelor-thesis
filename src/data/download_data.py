import gdown
from decouple import config

URL1 = config('URL1')
URL2 = config('URL1')
dest = r'../../data/raw' 

gdown.download_folder(URL1, output=dest, quiet=True, use_cookies=True)
gdown.download_folder(URL2, output=dest, quiet=True, use_cookies=False)
