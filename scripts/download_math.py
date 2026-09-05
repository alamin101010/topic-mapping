import urllib.request, os
url = 'https://drive.google.com/uc?export=download&id=12ygatNBK0ilJdccpnpuoT1N2G4pcaCya'
urllib.request.urlretrieve(url, 'books/temp_math.pdf')
print(f'Downloaded: {os.path.getsize("books/temp_math.pdf")} bytes')
