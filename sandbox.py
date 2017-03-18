from Crypto.Cipher import AES
import base64
import binascii
BLOCK_SIZE = 32
PADDING = ' '

# iv = '1234512345123451'
# cipher = AES.new(secret,AES.MODE_CBC,iv)
cipher = AES.new(secret)
s = "valuel"

pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
# print(len(pad(s)))
encodeAES = base64.b64encode(cipher.encrypt(pad(s)))

print(encodeAES)

enc = base64.b64decode(encodeAES)
print(enc)
decodeAES = cipher.decrypt(enc).decode('utf-8').rstrip(PADDING)

print(decodeAES)

# from common import cryptoo
# 						encodeAES = cryptoo.encryptt('passwrd')
# 						print(cryptoo.decryptt(encodeAES))