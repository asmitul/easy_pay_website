import requests
import re
import os
import time
from bs4 import BeautifulSoup
import ddddocr

def login(url : str  , username : str , password : str ,quary_key : str | int, query_value : str | int ) -> None:
    

    session = requests.session()
    timestamp = int(time.time())

    try:
        # code that may raise an error
        response = session.get(url+"/manage.php?"+quary_key+"="+query_value)
    except Exception as e:
        # code to handle the error
        print(f"An error occurred: {e.args}")
    else:
        # logger.info(f"login response: {response.text}")
        cookiesAfter = response.cookies
        c = cookiesAfter.get_dict()
        cookiesPHPSESSID = c["PHPSESSID"]
        print(f"1 . get PHPSESSID: {cookiesPHPSESSID}")

    cookiesLogin = {
            'QINGZHIFU_PATH': 'qingzhifu',
            'PHPSESSID': cookiesPHPSESSID
        }


    try:
        # code that may raise an error
        # logger.info(f"2 . get number , url :{URL}/manage.php?{KEY}={VALUE}")
        response = session.get(url+"/manage.php?"+quary_key+"="+query_value, cookies=cookiesLogin)
    except Exception as e:
        # code to handle the error
        print(f"An error occurred: {e.args}")
    else:
        # logger.info(f"login response: {response.text}")
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form', {'method': 'post'})
        action_value = form['action']
        match = re.search(r'/(\d+)\.html$', action_value)

        if match:
            number = match.group(1)
            print(f"3 . login number: {number}")
        else:
            print("Number not found")
    
    urlVerify = url + "/Manage/Index/verify.html"
    
    
    try:
        # code that may raise an error
        print(f"4 . capcha url: {urlVerify}")
        response = session.get(urlVerify, cookies=cookiesLogin)
    except Exception as e:
        # code to handle the error
        print(f"An error occurred: {e.args}")
    else:
        # code to execute if there is no error
        with open(f"captcha_{str(timestamp)}.png", "wb") as file:
            # Write the image data to the file
            file.write(response.content)

        # cookiesAfter = response.cookies
        # c = cookiesAfter.get_dict()
        # cookiesPHPSESSID = c["PHPSESSID"]

        # # read captcha
        ocr = ddddocr.DdddOcr()
        with open(f"captcha_{str(timestamp)}.png", 'rb') as f:
            image = f.read()
        
        # delete the f"captcha_{str(timestamp)}.png"
        if os.path.exists(f"captcha_{str(timestamp)}.png"):
            os.remove(f"captcha_{str(timestamp)}.png")
        code = ocr.classification(image)
        print(f"5 . capcha code: {code}")
        print(f"login code: {code}")
        
        if len(code) != 4:
            print(f"5 . capcha code error: {code}")
            return False
        
        data = {
            "username": username,
            "password": password,
            "yzm": code
        }

        urlLogin = url + "/Manage/Index/login/" + number + ".html"
        

        try:
            # code that may raise an error
            print(f"6 . login url: {urlLogin} , data: {data}")
            responseLogin = session.post(urlLogin, data=data, cookies=cookiesLogin)
        except Exception as e:
            # code to handle the error
            print(f"An error occurred: {e.args}")
        else:
            # check responseLogin.cookies exist or not , if not , return
            if responseLogin.cookies:
                print(f"6 . login response: True , cookies : {responseLogin.cookies}")
                cookiesR = responseLogin.cookies
                d = cookiesR.get_dict()
                fx_admin_user_CODE = d["fx_admin_user_CODE"]
                with open('fx_admin_user_CODE.txt', 'w') as file:
                                # Write some text to the file
                                file.write(fx_admin_user_CODE)
                with open('PHPSESSID.txt', 'w') as file:
                                # Write some text to the file
                                file.write(cookiesPHPSESSID)
                
                return {
                    "fx_admin_user_CODE": fx_admin_user_CODE,
                    "PHPSESSID": cookiesPHPSESSID
                }
            

            else:
                print(f"6 . login response: False")
                return False
            
def check_login_status(url : str):
    # start
    # check if fx_admin_user_CODE.txt exist or not 
    
    if os.path.exists('fx_admin_user_CODE.txt'):
        with open('fx_admin_user_CODE.txt', 'r') as file:
            fx_admin_user_CODE = file.read()
    else:
        print(f"login status: False")
        return False
    
    if os.path.exists('PHPSESSID.txt'):
        with open('PHPSESSID.txt', 'r') as file:
            cookiesPHPSESSID = file.read()
    else:
        print(f"login status: False")
        return False
    
    url = url + "/manage/main/index.html"
    cookies={
            "JSESSIONID": cookiesPHPSESSID,
            'QINGZHIFU_PATH': 'qingzhifu',
            'fx_admin_user_UNAME': 'admin',
            'menudd': '0',
            'fx_admin_user_UID': '1',
            'fx_admin_user_CODE': fx_admin_user_CODE
        }
    
    session = requests.session()

    try:
        # code that may raise an error
        response = session.get(url, cookies=cookies)
    except Exception as e:
        # code to handle the error
        print(f"An error occurred: {e.args}")
    else:
        # if response.headers lens 12 returm true else return false
        if len(response.headers) == 12:
            print(f"login status: True")
            return True
        else:
            print(f"login status: False")
            return False
        
