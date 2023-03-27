
//===========================================================================================
// 메뉴 체크 
//===========================================================================================
if(location.pathname != '/login') {
    const activeUrls = {
        '/apiBotList' : [
            '/apiBotList',
            '/'
        ],
        '/scenarioList' : [
            '/scenarioList',
            '/scenarioAdd'
        ]
    }
    
    let key = '';
    for(let k in activeUrls){
        for(let i = 0; i < activeUrls[k].length; i++){
            if(activeUrls[k][i] == location.pathname){
                key = k;
                break;
            }
        }
        if(key != '') break; 
    }
    if(key == '') key = location.pathname;
    document.querySelector(`#kt_aside a[href='.` + key + `']`).classList.add('active');
}

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

//===========================================================================================
//Modal Close All
//===========================================================================================
var modalClose = function() {
    let modal = document.querySelectorAll('div.modal.show')
    for (let i = 0; i < modal.length; i++){
        modalFeedbackReset(modal[i]);
        (bootstrap.Modal.getInstance(modal[i])).hide();
    }
}


//===========================================================================================
//Modal feedback reset
//===========================================================================================
var modalFeedbackReset = function(modal) {
    let feedback = modal.querySelectorAll('div.invalid-feedback');
    for (let i = 0; i < feedback.length; i++){
        feedback[i].innerHTML = '';
    }
}



//===========================================================================================
// 이미지 확대
//===========================================================================================
window.addEventListener("load", function() {
    var images = document.querySelector('data-image-zoom')

});




//===========================================================================================
// 클립보드로 복사
//===========================================================================================
var copy_to_clipboard = function(str){
    window.navigator.clipboard.writeText(str);
}



//===========================================================================================
// 특수문자 decode
//===========================================================================================
function decodeHTMLEntities (str) {
    if(str !== undefined && str !== null && str !== '') {
        str = String(str);
        str = str.replace(/<script[^>]*>([\S\s]*?)<\/script>/gmi, '');
        str = str.replace(/<\/?\w(?:[^"'>]|"[^"]*"|'[^']*')*>/gmi, '');
        var element = document.createElement('div');
        element.innerHTML = str;
        str = element.textContent;
        element.textContent = '';
    }
    return str
}