import datetime
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import pandas as pd
import sys
import os

#######################################################
############### 뉴스 스크래핑 기간 설정 #################
#######################################################

print('\'보험\' 키워드로 검색한 네이버 뉴스 기사를 스크랩하는 프로그램입니다.')
print('네이버의 자동 봇 탐지 이슈로 인해 한번에 \'최대 500개씩 스크랩\'하여 엑셀 파일로 저장합니다.')
print('-')

today = datetime.date.today()
minutes = "분 전"
hours = "시간 전"
dates = "일 전"

# 스크랩 시작일자 설정
input_start = input('스크랩 시작 날짜를 8자리 숫자로 입력하세요 \'ex)20230123\' : ')
start_year = int(str(input_start)[:4])
start_month = int(str(input_start)[4:6])
start_day = int(str(input_start)[-2:])
date_start = datetime.date(start_year, start_month, start_day)

# 스크랩 종료일자 설정
input_end = input('스크랩 종료 날짜를 8자리 숫자로 입력하세요 \'ex)20231231\' : ')
end_year = int(str(input_end)[:4])
end_month = int(str(input_end)[4:6])
end_day = int(str(input_end)[-2:])
date_end = datetime.date(end_year, end_month, end_day)

# date = datetime.date(start_year, start_month, start_day)
terms = (date_end - date_start).days
search = 0
plus = 1

# 스크래핑을 위한 데이터프레임 및 변수 생성
total_df = pd.DataFrame(columns=['Timestamp', 'Press', 'Title', 'URL'])
total_index = total_df.shape[0]
now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

# 자동 봇 탐지 우회를 위해 500개씩 끊어서 스크랩 (500개마다 반복문)
for search in range(terms+1):
    scrap = 0
    scrap_url = 0
    file = 0
    end_scrap = 0
    end_page = 0

    while True:

        #######################################################
        #################### 드라이버 설치 #####################
        #######################################################

        # 크롬 드라이버 설치
        chromedriver_autoinstaller.install()
        driver_service = Service('chromedriver.exe')
        driver = webdriver.Chrome(service=driver_service)
        driver.implicitly_wait(10)

        # 스크래핑을 위한 데이터프레임 및 변수 생성
        news_df = pd.DataFrame(columns=['Timestamp', 'Press', 'Title', 'URL'])
        news_index = news_df.shape[0]
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        #######################################################
        #################### 뉴스 스크래핑 #####################
        #######################################################

        # 스크래핑 시작 페이지 접속
        if scrap == 0:
            print('{}년 {}월 {}일의 뉴스 스크랩을 시작합니다. 스크랩이 진행되는 동안 프로그램을 종료하지 마세요'.format(str(date_start)[:4], str(date_start)[5:7], str(date_start)[-2:]))
            pass
        else:
            scrap_url = scrap + 1
        search_date_dot = str(date_start).replace("-",".")
        search_date_plain = str(date_start).replace("-","")
        driver.get("https://search.naver.com/search.naver?where=news&query=%EB%B3%B4%ED%97%98&sm=tab_opt&sort=2&photo=0&field=0&pd=3&ds={}&de={}&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Ar%2Cp%3Afrom{}to{},a:all&start={}".format(search_date_dot, search_date_dot, search_date_plain, search_date_plain, scrap_url))
        time.sleep(1)

        pages = 0
        # 봇 감지 방지를 위해 스크래핑을 50페이지로 제한
        for pages in range(50):

            news = 0
            # 한페이지에 뉴스기사 10개씩 스크래핑
            for news in range(10):
                scrap += 1

                # 타임스탬프(기사) 없으면 스크래핑 종료하고 페이지 넘기는 for문으로 break
                try:
                    timestamp = driver.find_element(By.CSS_SELECTOR, '#sp_nws{} > div > div > div.news_info > div.info_group > span'.format(scrap)).text
                    if dates in timestamp:
                        timestamp = today - datetime.timedelta(days=int(timestamp.replace("일 전", "")))
                    elif hours in timestamp:
                        timestamp = today - datetime.timedelta(days=int(timestamp.replace("일 전", "")))
                    elif minutes in timestamp:
                        timestamp = today - datetime.timedelta(days=int(timestamp.replace("분 전", "")))
                    else:
                        timestamp = timestamp.replace(".","")
                        timestamp = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:]}"
                except:
                    end_scrap += 1
                    break

                press = driver.find_element(By.CSS_SELECTOR, '#sp_nws{} > div > div > div.news_info > div.info_group > a'.format(scrap)).text
                title = driver.find_element(By.CSS_SELECTOR, '#sp_nws{} > div > div > a'.format(scrap)).text
                url = driver.find_element(By.CSS_SELECTOR, '#sp_nws{} > div > div > a'.format(scrap)).get_attribute("href")
                news_df.loc[news_index] = [timestamp, press, title, url]
                news_index += 1
                news += 1
            # 여기까지가 10개씩 뉴스긁기

            # 타임스탬프(기사) 없어서 빠져나왔으면 페이지 넘기는 for문도 종료
            if end_scrap != 1:
                pass
            else:
                end_page += 1
                break

            # 페이지 넘기기
            # 페이지 넘기는 버튼 없으면 페이지 넘기기 종료
            try:
                driver.find_element(By.CSS_SELECTOR, '#main_pack > div.api_sc_page_wrap > div > a.btn_next').click()
                driver.implicitly_wait(1)
            except:
                end_page += 1
                break
            # 여기까지가 50페이지 넘기기

        # 50페이지를 채웠을 수도 있고, 못 채웠을 수도 있음

        #######################################################
        ###################### 파일 저장 #######################
        #######################################################

        # 스크래핑한 뉴스의 제목과 URL을 엑셀 파일로 저장
        file += 1
        total_df = total_df.append(news_df, ignore_index=False)
        # 다음 스크래핑 시작을 위해 현재 페이지 URL 프린트
        driver.quit()

        # 만약 50페이지 채웠으면 다시 while문 반복 (못 채웠으면 while문 종료)
        if end_page == 1:
            print('현재 날짜의 스크랩을 종료하고 날짜를 변경합니다.')
            print('현재 날짜 : ', date_start)
            print('현재 스크랩 : ', scrap)
            break
        else:
            print('같은 날짜로 스크랩을 계속합니다.')
            print('현재 날짜 : ', date_start)
            print('현재 스크랩 : ', scrap)
            pass
    
    search += 1
    # date = date + datetime.timedelta(days=next_days)
    date_start = date_start + datetime.timedelta(days=plus)


total_df.to_excel('news.xlsx', index=False)

print('스크랩이 모두 종료되었습니다.')