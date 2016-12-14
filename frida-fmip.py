#!/usr/bin/python2.7
import frida
import sys

# Note: the SHA1 hashes seem to be the SHA1 hashes of DER certificates

session = frida.get_usb_device().attach("securityd")
fo = open("sha.bin", "wb")
fo2 = open("aesencryptkey.bin", "wb")
fo3 = open("functionlog.txt", "wt")
fo4 = open("aesdecryptkey.bin", "wb")
fo5 = open("decode.bin", "wb")
fo6 = open("aesencrypt.bin", "wb")
script = session.create_script("""
var f1 = Module.findExportByName("libcommonCrypto.dylib",
    "CCCryptorGCMEncrypt");
Interceptor.attach(f1, {
    onEnter: function (args) {
		var bytes = Memory.readByteArray(args[1], args[2].toInt32());
		send("CCCryptorGCMEncrypt", bytes);
    }
});
var f2 = Module.findExportByName("libcommonCrypto.dylib",
    "CCCryptorGCMDecrypt");
Interceptor.attach(f2, {
    onEnter: function (args) {
		var bytes = Memory.readByteArray(args[1], args[2].toInt32());
		send("CCCryptorGCMDecrypt", bytes);
    }
});
var f3 = Module.findExportByName("libcommonCrypto.dylib",
    "CCDigest");
Interceptor.attach(f3, {
    onEnter: function (args) {
		var bytes = Memory.readByteArray(args[2], args[1].toInt32());
		send("CCDigest", bytes);
    }
});
/*
var f4 = Module.findExportByName("libcrypto.so",
    "AES_cbc_encrypt");
Interceptor.attach(f4, {
    onEnter: function (args) {
		var bytes = Memory.readByteArray(args[0], args[2].toInt32());
		send("AES_cbc_encrypt", bytes);
    }
});
var f5 = Module.findExportByName("libcrypto.so",
    "EVP_DecodeUpdate");
Interceptor.attach(f4, {
    onEnter: function (args) {
		var bytes = Memory.readByteArray(args[3], args[4].toInt32());
		send("EVP_DecodeUpdate", bytes);
    }
});
var f6 = Module.findExportByName("libcrypto.so",
    "AES_set_decrypt_key");
Interceptor.attach(f4, {
    onEnter: function (args) {
		var bytes = Memory.readByteArray(args[0], 16);
		send("AES_set_decrypt_key", bytes);
    }
});
*/
""")
def on_message(message, data):
	pname = message['payload']
	fo3.write(pname+"\n")
	if (pname == "CCCryptorGCMEncrypt"):
		fo.write(data)
	elif (pname == "CCCryptorGCMDecrypt"):
		fo.write(data)
	elif (pname == "CCDigest"):
		fo2.write(data)
	elif (pname == "EVP_EncodeUpdate"):
		fo4.write(data)
	elif (pname == "EVP_DecodeBlock"):
		fo5.write(data)
	elif (pname == "AES_cbc_encrypt"):
		fo6.write(data)
try:
    script.on('message', on_message)
    script.load()
    sys.stdin.read()
except KeyboardInterrupt as e:
    fo.close()
    fo2.close()
    fo3.close()
    fo4.close()
    fo5.close()
    fo6.close()
    sys.exit(0)
