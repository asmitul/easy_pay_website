import time
import datetime
import pytz
import requests
from bs4 import BeautifulSoup
from login import check_login_status


def get_trading_volume_today(url : str , userId : str):
    result = check_login_status(url)
    if result == False:
        print(f"login status: False")
        return False
    
    timestamp = int(time.time()) 

    # Get current UTC time
    now = datetime.datetime.now(pytz.utc)
    
    # Set the time to 16:00:00
    latest_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    # Convert the time to milliseconds
    today_utc1600 = int(latest_time.timestamp() )

    if timestamp < today_utc1600:
        time_value = today_utc1600 - 24 * 60 * 60 
    else:
        time_value = today_utc1600

    print(time_value)

    session = requests.session()
    with open('fx_admin_user_CODE.txt', 'r') as file:
        fx_admin_user_CODE = file.read()
    with open('PHPSESSID.txt', 'r') as file:
        cookiesPHPSESSID = file.read()

    cookies={
            "JSESSIONID": cookiesPHPSESSID,
            'QINGZHIFU_PATH': 'qingzhifu',
            'fx_admin_user_UNAME': 'admin',
            'menudd': '0',
            'fx_admin_user_UID': '1',
            'fx_admin_user_CODE': fx_admin_user_CODE
        }
    try:
        # code that may raise an error
        response = session.get(url+"/manage/dingdan/dingdancheck.html?userid=" + userId + "&pzid=&jkstyle=&time=" + str(time_value)+"&money=&mypagenum", cookies=cookies)
    except Exception as e:
        # code to handle the error
        print(f"An error occurred: {e.args}")
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('div', {'class': 'row tagtopdiv'})
        # fild all h4 tag
        h4_tags = form.find_all('h4')
        # print h4_tags value one by one , and append to the new list
        h4_values = []
        for h4_tag in h4_tags:
            h4_values.append(h4_tag.text)
        for i in range(len(h4_values)):
            h4_values[i] = h4_values[i].strip()
        h4_values[0] = h4_values[0][1:-2]
        h4_values[2] = h4_values[2][:-2]
        h4_values[6] = h4_values[6][1:-2]
        data_object = {
            h4_values[1]: float(h4_values[0].split()[0]),  
            h4_values[3]: int(h4_values[2].split()[0]),  
            h4_values[7]: float(h4_values[6].split()[0])  ,
            "rate" : round(( 1 - float(h4_values[0].split()[0]) / float(h4_values[6].split()[0]) ) * 100 , 2 ),
        }

        print(data_object)
         