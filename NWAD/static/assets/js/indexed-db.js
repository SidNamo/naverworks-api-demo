
const DATABASE = 'Didim365ApiSampler';
const DB_VERSION = 1;

var db;
var request;
var objectSotre;

var getObjectStore = (store_name, mode) => {
    return db.transaction(store_name, mode).objectStore(store_name);
}

// 현재 날짜 시간 YYYY-MM-DD HH:MM:SS
var now = function(){
    let today = new Date();

    let year = today.getFullYear();
    let month = ('0' + (today.getMonth() + 1)).slice(-2);
    let day = ('0' + today.getDate()).slice(-2);

    let dateString = year + '-' + month  + '-' + day;

    let hours = ('0' + today.getHours()).slice(-2); 
    let minutes = ('0' + today.getMinutes()).slice(-2);
    let seconds = ('0' + today.getSeconds()).slice(-2); 
    
    let timeString = hours + ':' + minutes  + ':' + seconds;
    return dateString + " " + timeString;
}

if(!IndexedDB){
    var IndexedDB = {};
}

window.indexedDB = window.indexedDB || window.mozIndexedDB || window.webkitIndexedDB || window.msIndexedDB;

// DB 연결 
IndexedDB.open = function(){
    if(!window.indexedDB){
        return false;
    }else{
        request = window.indexedDB.open(DATABASE, DB_VERSION);

        // DB 연결 성공
        request.onsuccess = function(event){
            console.log("indexedDB : 연결성공");
            db = this.result;
        }

        // DB 연결 실패
        request.onerror = function(event){
            console.error("indexedDB : ", event.target.errorCode);
            return false;
        }

        // DB 마이그레이션
        request.onupgradeneeded = function(event){
            console.log("indexedDB.onupgradeneeded");
            
            //유저 정보
            objectSotre = event.currentTarget.result.createObjectStore("UserData",{ keyPath: 'index', autoIncrement: true });
            objectSotre.createIndex('id', 'id', { unique: false });
            objectSotre.createIndex('saveid', 'saveid', { unique: false });     // 아이디 저장 (로그인)
            objectSotre.createIndex('regdate', 'regdate', { unique: false });   // 작성일
        }
    }
    return true;
}
IndexedDB.open();

// DB 클리어
IndexedDB.clear = function(store_name){
    return getObjectStore(store_name, 'readwrite').clear();
}

// 데이터 쓰기
IndexedDB.write = function(store_name, value){
    // DB 연결 확인
    if(!db){
        // IndexedDB 사용 불가 - localStorage 로 대체
        console.log("localStorage");

        return false;
    }
    if(!value.regdate) value.regdate = now();
    let store = getObjectStore(store_name, 'readwrite');
    let req = store.add(value);
    return req;
}

// 데이터 수정
IndexedDB.update = function(store_name, key, value){
    // DB 연결 확인
    if(!db){
        // IndexedDB 사용 불가 - localStorage 로 대체
        console.log("localStorage");

        return false;
    }

    if(!value.regdate) value.regdate = now();

    let store = getObjectStore(store_name, 'readwrite');
    let req = store.get(key)

    req.onsuccess = function(event){
        let data = event.target.result;
        if(!data){
            console.log(data);
            return;
        }
        data = Object.assign(data, value);

        let updatereq = store.put(data);
        updatereq.onerror = function(event){
            console.log(event);
        }
        updatereq.onsuccess = function(event){
            console.log(event);
        }
    }
    return req;
}

// 데이터 조회
IndexedDB.get = function(store_name, key){
    // DB 연결 확인
    if(!db){
        // IndexedDB 사용 불가 - localStorage 로 대체
        console.log("localStorage");

        return false;
    }
    let store = getObjectStore(store_name, 'readwrite');
    let req;
    return store.get(key).target.result;
}

// 데이터 조회
IndexedDB.getAll = function(store_name, key){
    // DB 연결 확인
    if(!db){
        // IndexedDB 사용 불가 - localStorage 로 대체
        console.log("localStorage");

        return false;
    }
    let store = getObjectStore(store_name, 'readwrite');

    let done = false;
    let result = new Promise(
        function(resolve, reject){
            let req = store.getAll();
            req.onsuccess = function(event){
                result = event.target.result;
                done = true;
            };
        }
    )
    return result;
}