import gdown
url1 = 'https://drive.google.com/drive/folders/1aKoxgjfKm9VvMwIOCd1PfezJlAotYtvH?usp=sharing'
url2 = 'https://drive.google.com/drive/folders/10KCjmmboLrmPQg1foPoWQjcRqC46o2-n?usp=sharing'
dest = r'C:/Users/Filip/Desktop/bachelor-thesis/data/raw' 

gdown.download_folder(url1, output=dest, quiet=True, use_cookies=True)
gdown.download_folder(url2, output=dest, quiet=True, use_cookies=False)
