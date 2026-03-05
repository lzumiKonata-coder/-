import hashlib

def get_doc_enc(s):
    """
    计算字符串 s 与固定密钥拼接后的 MD5 值。
    """
    key = "NrRzLDpWB2JkeodIVAn4"
    data = (s + key).encode('utf-8')
    return hashlib.md5(data).hexdigest()
