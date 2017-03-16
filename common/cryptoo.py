from Crypto.Cipher import AES
import base64
import binascii
import json 
with open('./key/conf.json') as conf_json:
    conf = json.load(conf_json)

BLOCK_SIZE = 32
PADDING = ' '
secret = conf["aes"]["key"]
# iv = '1234512345123451'
# cipher = AES.new(secret,AES.MODE_CBC,iv)
cipher = AES.new(secret)
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

def encryptt(pw):		
	return base64.b64encode(cipher.encrypt(pad(pw))).decode()
def decryptt(encodeAES):
	return cipher.decrypt(base64.b64decode(encodeAES)).decode('utf-8').rstrip(PADDING)

	