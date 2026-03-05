import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def encryptByAES(message: str, key: str) -> str:
    """
    使用 AES-CBC 模式加密消息，密钥同时作为 IV，PKCS7 填充。
    返回 Base64 编码的密文。
    """
    # 将密钥和消息转为字节（UTF-8）
    key_bytes = key.encode('utf-8')
    iv_bytes = key_bytes  # IV 与密钥相同
    message_bytes = message.encode('utf-8')

    # 创建 AES 加密器（密钥长度 16 字节，即 AES-128）
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)

    # PKCS7 填充
    padded_data = pad(message_bytes, AES.block_size)

    # 加密
    encrypted_bytes = cipher.encrypt(padded_data)

    # 返回 Base64 编码的密文字符串
    return base64.b64encode(encrypted_bytes).decode('utf-8')

def get_uname_password(uname: str, password: str) -> dict:
    """
    对用户名和密码分别使用固定密钥进行 AES 加密，
    返回包含加密结果的字典。
    """
    transferKey = "u2oh6Vu^HWe4_AES"
    encrypted_uname = encryptByAES(uname, transferKey)
    encrypted_password = encryptByAES(password, transferKey)
    return {
        'uname': encrypted_uname,
        'password': encrypted_password
    }
