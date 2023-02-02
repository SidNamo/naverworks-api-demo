//===========================================================================================
//쿠키
//===========================================================================================
var Cookies = function (name, value, expire) {
    if (typeof value != "undefined" && typeof expire != "undefined") {
        var day = new Date();
        day.setDate(day.getDate() + expire);
        document.cookie = name + "=" + escape(value) + "; path=/; expires=" + day.toGMTString() + ";";
    } else {
        var org = document.cookie;
        var dlm = name + "=";
        var x = 0;
        var y = 0;
        var z = 0;

        while (x <= org.length) {
            y = x + dlm.length;

            if (org.substring(x, y) == dlm) {
                if ((z = org.indexOf(";", y)) == -1) {
                    z = org.length;
                }

                return org.substring(y, z);
            }

            x = org.indexOf(" ", x) + 1;

            if (x == 0) {
                break;
            }
        }

        return "";
    }
}

//===========================================================================================
//랜덤
//===========================================================================================
function Random(lenth){
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for( var i=0; i < lenth; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    return text;
}

//===========================================================================================
//암호화
//===========================================================================================
function encodeByAES256(data){
    let key = Cookies("CRID");
    let iv = Cookies("IVID");
    if(key == ''){
        Cookies("CRID", Random(32), 365);
        Cookies("IVID", Random(16), 365);
    }
    const cipher = CryptoJS.AES.encrypt(data, CryptoJS.enc.Utf8.parse(key), {
        iv: CryptoJS.enc.Utf8.parse(iv),
        padding: CryptoJS.pad.Pkcs7,
        mode: CryptoJS.mode.CBC
    });
    return cipher.toString();
}
//===========================================================================================
//복호화
//===========================================================================================
function decodeByAES256(data){
    let key = Cookies("CRID");
    let iv = Cookies("IVID");
    if(key == ''){
        return null;
    }else{
        let cipher = CryptoJS.AES.decrypt(data, CryptoJS.enc.Utf8.parse(key), {
            iv: CryptoJS.enc.Utf8.parse(iv),
            padding: CryptoJS.pad.Pkcs7,
            mode: CryptoJS.mode.CBC
        });
        return cipher.toString(CryptoJS.enc.Utf8);
    }
};