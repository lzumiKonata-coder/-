const CryptoJS = require('crypto-js');

function encryptByAES(message, key) {
    let CBCOptions = {
        iv: CryptoJS.enc.Utf8.parse(key),
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
    };
    let aeskey = CryptoJS.enc.Utf8.parse(key);
    let secretData = CryptoJS.enc.Utf8.parse(message);
    let encrypted = CryptoJS.AES.encrypt(
        secretData,
        aeskey,
        CBCOptions
    );
    return CryptoJS.enc.Base64.stringify(encrypted.ciphertext);
}

// transferKey = "u2oh6Vu^HWe4_AES"
// pwd = encryptByAES("PN1234567", transferKey)
// phone = encryptByAES("15542504095", transferKey)
// console.log(phone)
// console.log(pwd)

function get_uname_password(uname ,password){
    data = {}
    transferKey = "u2oh6Vu^HWe4_AES"
    password = encryptByAES(password , transferKey)
    uname = encryptByAES(uname , transferKey)
    data['uname'] = uname
    data['password'] = password
    return data
}

console.log(get_uname_password('15542504095','PN1234567'))
