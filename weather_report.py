import os
import requests
import json
import datetime
from bs4 import BeautifulSoup

# 从测试号信息获取
appID = "wx9552f5aece196240"
appSecret = "b936876afdd4afe40b348bcc0887d16b"
# 收信人ID即 用户列表中的微信号
openIds = ["oL2dz6Wx8-_jnjp7ak7uJ-MXtabY", "oL2dz6Tbe7KI3AjjQv4-T_WE8ZSs"]
# 天气预报模板ID
weather_template_id = "1j7bpcBZu3fKuIaSPw6rKvwQiEqNs9hRp-DrjprXrRE"

def get_weather(my_city):
    urls = ["http://www.weather.com.cn/textFC/hb.shtml",
            "http://www.weather.com.cn/textFC/db.shtml",
            "http://www.weather.com.cn/textFC/hd.shtml",
            "http://www.weather.com.cn/textFC/hz.shtml",
            "http://www.weather.com.cn/textFC/hn.shtml",
            "http://www.weather.com.cn/textFC/xb.shtml",
            "http://www.weather.com.cn/textFC/xn.shtml"
            ]
    for url in urls:
        resp = requests.get(url)
        text = resp.content.decode("utf-8")
        soup = BeautifulSoup(text, 'html5lib')
        div_conMidtab = soup.find("div", class_="conMidtab")
        tables = div_conMidtab.find_all("table")
        for table in tables:
            trs = table.find_all("tr")[2:]
            for index, tr in enumerate(trs):
                tds = tr.find_all("td")
                # 这里倒着数，因为每个省会的td结构跟其他不一样
                city_td = tds[-8]
                this_city = list(city_td.stripped_strings)[0]
                if this_city == my_city:

                    high_temp_td = tds[-5]
                    low_temp_td = tds[-2]
                    weather_type_day_td = tds[-7]
                    weather_type_night_td = tds[-4]
                    wind_td_day = tds[-6]
                    wind_td_day_night = tds[-3]

                    high_temp = list(high_temp_td.stripped_strings)[0]
                    low_temp = list(low_temp_td.stripped_strings)[0]
                    weather_typ_day = list(weather_type_day_td.stripped_strings)[0]
                    weather_type_night = list(weather_type_night_td.stripped_strings)[0]

                    wind_day = list(wind_td_day.stripped_strings)[0] + list(wind_td_day.stripped_strings)[1]
                    wind_night = list(wind_td_day_night.stripped_strings)[0] + list(wind_td_day_night.stripped_strings)[1]

                    # 如果没有白天的数据就使用夜间的
                    temp = f"{low_temp}至{high_temp}摄氏度" if high_temp != "-" else f"{low_temp}摄氏度"
                    weather_typ = weather_typ_day if weather_typ_day != "-" else weather_type_night
                    wind = f"{wind_day}" if wind_day != "--" else f"{wind_night}"
                    return this_city, temp, weather_typ, wind


def get_access_token():
    # 获取access token的url
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}' \
        .format(appID.strip(), appSecret.strip())
    response = requests.get(url).json()
    print(response)
    access_token = response.get('access_token')
    return access_token


def get_daily_love():
    # 每日一句情话
    url = "https://api.lovelive.tools/api/SweetNothings/Serialization/Json"
    r = requests.get(url)
    all_dict = json.loads(r.text)
    sentence = all_dict['returnObj'][0]
    daily_love = sentence
    return daily_love

def get_limitedNumber():
    # 获取当前日期
    today = datetime.datetime.now().strftime("%Y年%m月%d日")

    # 发送请求获取限行数据
    url = "http://yw.jtgl.beijing.gov.cn/jgjxx/services/getRuleWithWeek"
    response = requests.get(url)

    # 解析限行数据
    data = json.loads(response.text)
    limited_data = data["result"]

    # 查找今天的限行信息
    today_limited_number = None
    for limited in limited_data:
        if limited["limitedTime"] == today:
            today_limited_number = limited["limitedNumber"]
            break

    return today_limited_number

def send_weather(access_token, weather, limitedNumber):
    import datetime
    today = datetime.date.today()
    today_str = today.strftime("%Y年%m月%d日")

    for openId in openIds:
        body = {
            "touser": openId.strip(),
            "template_id": weather_template_id.strip(),
            "url": "https://weixin.qq.com",
            "data": {
                "date": {
                    "value": today_str
                },
                "region": {
                    "value": weather[0]
                },
                "weather": {
                    "value": weather[2]
                },
                "temp": {
                    "value": weather[1]
                },
                "wind_dir": {
                    "value": weather[3]
                },
                "limitedNumber": {
                    "value": limitedNumber
                },
                "today_note": {
                    "value": get_daily_love()
                }
            }
        }
        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token)
        print(requests.post(url, json.dumps(body)).text)

def weather_report(this_city):
    # 1.获取access_token
    access_token = get_access_token()
    # 2. 获取天气
    weather = get_weather(this_city)
    print(f"天气信息： {weather}")
    # 3. 获取限号信息
    limitedNumber = get_limitedNumber()
    # 4. 发送消息
    send_weather(access_token, weather, limitedNumber)

if __name__ == '__main__':
    weather_report("北京")
