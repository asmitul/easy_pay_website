import requests
import re
import os
import time
from bs4 import BeautifulSoup
import ddddocr
from odin_functions import check


def login(url : str  , username : str , password : str ,quary_key : str | int, query_value : str | int ) -> None:
    """
    Login to the specified URL using the provided username and password, along with additional query parameters.
    
    Args:
        url (str): The URL to log in to.
        username (str): The username to use for authentication.
        password (str): The password to use for authentication.
        quary_key (str | int): The key for the query parameter.
        query_value (str | int): The value for the query parameter.
    
    Returns:
        dict: A dictionary containing the login result. The dictionary has the following keys:
            - "result" (bool): The result of the login attempt.
            - "message" (str): A message indicating the result of the login attempt.
            - "data" (dict): Additional data related to the login attempt.
        
    """
        
    session = requests.session()
    timestamp = int(time.time())

    try:
        response = session.get(url+"/manage.php?"+quary_key+"="+query_value)
        if check.type_name(response) == 'NoneType':
            return {
                        "result": False,
                        "message": "failed",
                        "data" : []
                    }
    except Exception as e:
        return {
                    "result": False,
                    "message": "failed",
                    "data" : []
            }
    else:
        cookiesAfter = response.cookies
        c = cookiesAfter.get_dict()
        cookiesPHPSESSID = c["PHPSESSID"]
        if check.type_name(cookiesPHPSESSID) == 'NoneType':
            return {
                        "result": False,
                        "message": "failed",
                        "data" : []
                    }

        cookiesLogin = {
                'QINGZHIFU_PATH': 'qingzhifu',
                'PHPSESSID': cookiesPHPSESSID
            }


        try:
            response = session.get(url+"/manage.php?"+quary_key+"="+query_value, cookies=cookiesLogin)
            if check.type_name(response) == 'NoneType':
                return {
                            "result": False,
                            "message": "failed",
                            "data" : []
                        }
        except Exception as e:
            return {
                        "result": False,
                        "message": "failed",
                        "data" : []
                }
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            if check.type_name(soup) == 'NoneType':
                return {
                            "result": False,
                            "message": "failed",
                            "data" : []
                        }
            form = soup.find('form', {'method': 'post'})
            if check.type_name(form) == 'NoneType':
                return {
                            "result": False,
                            "message": "failed",
                            "data" : []
                        }
            action_value = form['action']
            if check.type_name(action_value) == 'NoneType':
                return {
                            "result": False,
                            "message": "failed",
                            "data" : []
                        }
            match = re.search(r'/(\d+)\.html$', action_value)
            if check.type_name(match) == 'NoneType':
                return {
                            "result": False,
                            "message": "failed",
                            "data" : []
                        }

            if match:
                number = match.group(1)
            else:
                pass
        
            urlVerify = url + "/Manage/Index/verify.html"
            
            
            try:
                response = session.get(urlVerify, cookies=cookiesLogin)
                if check.type_name(response) == 'NoneType':
                    return {
                                "result": False,
                                "message": "failed",
                                "data" : []
                            }
            except Exception as e:
                return {
                                "result": False,
                                "message": "failed",
                                "data" : []
                            }
            else:
                with open(f"captcha_{str(timestamp)}.png", "wb") as file:
                    file.write(response.content)

                ocr = ddddocr.DdddOcr()
                with open(f"captcha_{str(timestamp)}.png", 'rb') as f:
                    image = f.read()
                
                if os.path.exists(f"captcha_{str(timestamp)}.png"):
                    os.remove(f"captcha_{str(timestamp)}.png")
                
                code = ocr.classification(image)
                
                if len(code) != 4:
                    return {
                            "result": False,
                            "message": "failed",
                            "data" : []
                    }
                
                data = {
                    "username": username,
                    "password": password,
                    "yzm": code
                }

                urlLogin = url + "/Manage/Index/login/" + number + ".html"
                

                try:
                    responseLogin = session.post(urlLogin, data=data, cookies=cookiesLogin)
                    if check.type_name(responseLogin) == 'NoneType':
                        return {
                                    "result": False,
                                    "message": "failed",
                                    "data" : []
                                }

                except Exception as e:
                    return {
                            "result": False,
                            "message": "failed",
                            "data" : []
                    }
                else:
                    if responseLogin.cookies:
                        cookiesR = responseLogin.cookies
                        d = cookiesR.get_dict()
                        fx_admin_user_CODE = d["fx_admin_user_CODE"]
                        with open('fx_admin_user_CODE.txt', 'w') as file:
                                        file.write(fx_admin_user_CODE)
                        with open('PHPSESSID.txt', 'w') as file:
                                        file.write(cookiesPHPSESSID)
                        
                        return {
                            "result": True,
                            "message": "success",
                            "data" : [{
                                "fx_admin_user_CODE": fx_admin_user_CODE,
                                "PHPSESSID": cookiesPHPSESSID
                            }]
                        }
                    
                    else:
                        return {
                            "result": False,
                            "message": "failed",
                            "data" : []
                        }
            
def check_login_status(url : str):
    """
    Check the login status by sending a GET request to the specified URL.
    
    Parameters:
        url (str): The URL to send the GET request to.
        
    Returns:
        dict: A dictionary containing the result of the login status check. The dictionary has the following keys:
            - result (bool): True if the login status check is successful, False otherwise.
            - message (str): A message indicating the result of the login status check.
            - data (dict): Additional data related to the login status check. The dictionary has the following keys:
                - fx_admin_user_CODE (str): The code of the admin user.
                - PHPSESSID (str): The PHP session ID.
    """
    if os.path.exists('fx_admin_user_CODE.txt'):
        with open('fx_admin_user_CODE.txt', 'r') as file:
            fx_admin_user_CODE = file.read()
    else:
        print("fx_admin_user_CODE.txt not found")
        return {
                "result": False,
                "message": "failed",
                "data" : []
            }
    
    if os.path.exists('PHPSESSID.txt'):
        with open('PHPSESSID.txt', 'r') as file:
            cookiesPHPSESSID = file.read()
    else:
        print("PHPSESSID.txt not found")
        return {
                "result": False,
                "message": "failed",
                "data" : []
            }
    
    url = url + "/manage/main/index.html"
    cookies={
            "JSESSIONID": cookiesPHPSESSID,
            'QINGZHIFU_PATH': 'qingzhifu',
            'fx_admin_user_UNAME': 'beidou',
            'menudd': '0',
            'fx_admin_user_UID': '17',
            'fx_admin_user_CODE': fx_admin_user_CODE
        }
    
    session = requests.session()

    try:
        response = session.get(url, cookies=cookies)
        if check.type_name(response) == 'NoneType':
            print(f"check 251")
            return {
                "result": False,
                "message": "failed",
                "data" : []
            }
    except Exception as e:
        print(f"check 258")
        return {
                "result": False,
                "message": "failed",
                "data" : []
            }
    else:
        # print(response.text)
        if len(response.headers) == 12:
            return {
                "result": True,
                "message": "success",
                "data" : [{
                    "fx_admin_user_CODE": fx_admin_user_CODE,
                    "PHPSESSID": cookiesPHPSESSID
                }]
            }
        else:
            print(f"check 275")
            return {
                "result": False,
                "message": "failed",
                "data" : []
            }


def main(url : str , path : str ,query : dict):
    """
    Executes a main function that performs a series of operations.
    
    Args:
        url (str): The URL to send the request to.
        path (str): The path to append to the URL.
        query (dict): The query parameters to include in the request.
        
    Returns:
        dict: A dictionary with the following keys:
            - result (bool): Indicates whether the operation was successful.
            - message (str): A message describing the result of the operation.
            - data (list): A list of data returned by the operation.
    """
    result = check_login_status(url)
    if check.type_name(result) == 'NoneType':
        return {
                "result": False,
                "message": "check_login_status() result is NoneType",
                "data" : []
            }
    
    if result["result"] == False:
        return {
                "result": False,
                "message": "login failed",
                "data" : []
            }
    elif result["result"] == True:
        if os.path.exists('fx_admin_user_CODE.txt'):
            with open('fx_admin_user_CODE.txt', 'r') as file:
                fx_admin_user_CODE = file.read()
        else:
            return {
                    "result": False,
                    "message": "failed",
                    "data" : []
                }
        
        if os.path.exists('PHPSESSID.txt'):
            with open('PHPSESSID.txt', 'r') as file:
                cookiesPHPSESSID = file.read()
        else:
            return {
                    "result": False,
                    "message": "failed",
                    "data" : []
                }

        cookies={
            "JSESSIONID": cookiesPHPSESSID,
            'QINGZHIFU_PATH': 'qingzhifu',
            'fx_admin_user_UNAME': 'beidou',
            'menudd': '0',
            'fx_admin_user_UID': '17',
            'fx_admin_user_CODE': fx_admin_user_CODE
        }

        session = requests.session()

        try:
            response = session.get(url+path,params=query, cookies=cookies)
            if check.type_name(response) == 'NoneType':
                return {
                    "result": False,
                    "message": "failed",
                    "data" : []
                }
        except Exception as e:
            return {
                    "result": False,
                    "message": "failed",
                    "data" : []
                }
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            form = soup.find('form', {'method': 'post'})
            table = form.find('table', {'class': 'table table-hover'})
            tbody = table.find('tbody')

            trs = tbody.find_all('tr')
            data = []

            for tr in trs:
                tds = tr.find_all('td')
                row = []
                for td in tds:
                    row.append(td.text)
                # if row equl to []
                if len(row) == 0:
                    continue
                data.append(row)

            return {
                "result": True,
                "message": "success",
                "data" : data
            }
            
    else:
        return {
                "result": False,
                "message": "failed",
                "data" : []
        }



