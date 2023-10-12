import base64
import json

import rsa


class MyRSA:
    # 1048576 = 1MB
    key_size = 4096

    def __init__(self):
        # self.key_size = app_settings.JWT_SECRET_KEY
        pass

    def create_rsa_key(self):
        public_key, private_key = rsa.newkeys(self.key_size)
        public_key = public_key.save_pkcs1("PEM").decode('utf-8')
        private_key = private_key.save_pkcs1("PEM").decode('utf-8')
        return public_key, private_key

    # mã hóa và trả về kiểu base64
    def encrypt(self, payload, public_key):
        if isinstance(public_key, str):
            public_key = public_key.encode('utf-8')
        if isinstance(payload, dict):
            payload = json.dumps(payload).encode('utf-8')
        else:
            payload = payload.encode('utf-8')
        data_encrypt = rsa.encrypt(payload, public_key)
        b64encoded_data = base64.b64encode(data_encrypt)
        encrypted_str = b64encoded_data.decode("utf-8")
        return encrypted_str

    def decrypt(self, payload, private_key):
        if isinstance(private_key, str):
            private_key = private_key.encode('utf-8')

        payload = base64.b64decode(payload)
        data_decrypt = rsa.decrypt(payload, private_key)

        print("kieu du lieu sau khi decrypt RSA :")
        print(type(data_decrypt))

        decoded_decrypted_data = data_decrypt.decode('utf-8')

        print("data cuoi cung sau khi decode utf8 lun : " + decoded_decrypted_data)
        print(type(decoded_decrypted_data))

        return decoded_decrypted_data

    def loading_key_rsa(self, public_key, private_key):
        try:
            if isinstance(private_key, str):
                private_key = rsa.PrivateKey.load_pkcs1(private_key)
            else:
                private_key = None

            if isinstance(public_key, str):
                public_key = rsa.PublicKey.load_pkcs1(public_key)
            else:
                public_key = None

            if private_key is None and public_key is None:
                # Không thể load key từ cả private_key và public_key
                return None

            return public_key, private_key
        except Exception as ex:
            print(ex)
            pass
