from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from fake_useragent import UserAgent
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import re
import pandas as pd

url = "https://www.xuetangx.com/search?query=&page=1&ss=manual_search&channel=i.area.manual_search"
new_page_url = "https://www.xuetangx.com/search?query=&org=&classify=&type=&status=&page=755"

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('log-level=3')
options.add_argument(f"user-agent={UserAgent.random}")

options.add_argument("enable-automation")
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-extensions")
options.add_argument("--dns-prefetch-disable")
options.add_argument("--disable-gpu")
options.page_load_strategy = 'eager'
driver = webdriver.Chrome(options)

delay = 20           # максимальная задержка для прогрузки страницы (в секундах)
cycles_in_page = 2   # количество циклов на странице при условии, что не найден ни один новый курс

mas_url = []         # глобальный список ссылок
mas_univer = []      # глобальный список найденных университетов
mas_free = []        # глобальный список бесплатных цен
mas_price = []       # глобальный список цен
mas_students = []    # глобальный список количества студентов
mas_during = []      # глобальный список продолжительности курсов
mas_names = []

page = int(input('Page: '))  # номер текущей страницы
if page != 1:
    df = pd.read_excel('Universities_all.xlsx')
    mas_url = list(df['URL'])
    mas_names = list(df['Name'])
    mas_during = list(df['Duration'])
    mas_univer = list(df['University'])
    mas_price = list(df['Price'])
    mas_free = list(df['Free'])
    mas_students = list(df['Students'])

print(len(mas_url), mas_url[-1])
print(len(mas_names), mas_names[-1])
print(len(mas_during), mas_during[-1])
print(len(mas_univer), mas_univer[-1])
print(len(mas_price), mas_price[-1])
print(len(mas_free), mas_free[-1])
print(len(mas_students), mas_students[-1])

try:
    driver.get(new_page_url)

    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, "el-pager")))
    # ищем кол-во страниц:
    num_pages = driver.find_element(By.CLASS_NAME, "el-pager").text  # проверяем больше ли одной страницы
    if page == 1:
        num_pages = num_pages.replace("123456", "")
        num_pages = int(num_pages)   # количество страниц текущего университета
    else:
        num_pages = num_pages[-3]+num_pages[-2]+num_pages[-1]
        num_pages = int(num_pages)
    print(num_pages)

    num_back = 0
    cycle = 1
    click_back = 0
    myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, "leftImg")))
    items_0 = driver.find_elements(By.CLASS_NAME, "leftImg")       # список доступа к курсам с текущей стрицы
    len_temp = len(mas_url)          # количество курсов поиска текущего университета на просмотренных страницах

    while page <= num_pages:
        print('page = ', page)
        print("len(mas_url_temp) < (page * len(items)):", len(mas_url), page * len(items_0))
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, "leftImg")))
        items = driver.find_elements(By.CLASS_NAME, "leftImg")
        if (click_back != 1) and (len(mas_url) < (page * len(items_0))):
            len_temp += len(items)
        print(len_temp)

        links = 0                                                  # номер текущей ссылки
       # links_univer = 0
        cycle = 0                                                  # количество циклов без нахождения нового курса
        click_back = 0                                             # флаг нужен ли переход на предыдущую страницу

        len_page = len(items_0)
        mas_url_temp = []  # список ссылок для текущего университета
        mas_univer_temp = []  # список найденных университетов для текущего университета
        mas_free_temp = []  # список бесплатных цен для текущего университета
        mas_price_temp = []  # список цен для текущего университета
        mas_students_temp = []  # список количества студентов для текущего университета
        mas_during_temp = []  # список продолжительности курсов для текущего университета
        mas_names_temp = []

        print("len(mas_url_temp) != len_temp:", len(mas_url), len_temp)
        print("cycle <= cycles_in_page:", cycle, cycles_in_page)
        print("len(mas_url_temp) != len_page: ", len(mas_url_temp), len_page)
        while (len(mas_url) != len_temp) and (cycle <= cycles_in_page) and (len(mas_url_temp) != len_page):   # цикл
            print('start', links)
            WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.CLASS_NAME, "leftImg")))
            items_temp = driver.find_elements(By.CLASS_NAME, "leftImg")
            class_teacher = driver.find_elements(By.CLASS_NAME, "teacher")
            names_courses = driver.find_elements(By.CLASS_NAME, "titletext")
            class_org_con = driver.find_elements(By.CLASS_NAME, "org_con")
            len_page = len(items_temp)
            if links == len(items_temp):
                links = 0
              #  links_univer = 0
                cycle += 1
                print('cycle =', cycle)
            if cycle > cycles_in_page:
                if page != 1:
                    page -= 2
                    click_back = 1
                else:
                    cycle = 0
          #  print('links', links)
            students = class_teacher[links].text
            name_course = names_courses[links].text
          #  print(len(class_org_con))
          #   try:
          #       org = class_org_con[links_univer].text[1:].strip()
          #   except IndexError:
          #       pass

            print(name_course)

            actions = ActionChains(driver)
            actions.move_to_element(items_temp[links]).perform()
            items_temp[links].click()
            cur_url = driver.current_url
            print(cur_url)
            if re.search(r'https://www.xuetangx.com/course', cur_url):
                cur_url = re.search(r'https://www.xuetangx.com/course/[\D\d]*[/\?]', cur_url).group(0)
                print(cur_url)
                myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, "price")))
                try:
                    univer = driver.find_element(By.CLASS_NAME, "tip-org-teacher").text
                    univer = re.search(r': \D*,', univer).group(0).replace(":", "").replace(",", "").strip()
                except:
                    univer = ''
               # links_univer += 1

                if (not cur_url in mas_url) and (not cur_url in mas_url_temp):
                    cycle = 0
                    mas_univer_temp.append(univer)
                    mas_url_temp.append(cur_url)
                    courses = driver.find_elements(By.CLASS_NAME, "chapter")
                    mas_during_temp.append(len(courses))
                    price = driver.find_elements(By.CLASS_NAME, "price")
                    if len(price) == 2:
                        mas_free_temp.append(price[0].text)
                        mas_price_temp.append(price[1].text)
                    else:
                        mas_free_temp.append('-')
                        mas_price_temp.append(price[0].text)
                    students = re.search(r'\d+', students).group(0)
                    print("NEW...........................", students)
                    mas_students_temp.append(int(students))
                    mas_names_temp.append(name_course)
            else:
                if re.search(r'https://www.xuetangx.com/live', cur_url):
                    cur_url = re.search(r'https://www.xuetangx.com/live/[\D\d]*[/\?]', cur_url).group(0)
                    print(cur_url)
                    if (not cur_url in mas_url) and (not cur_url in mas_url_temp):
                        print("NEW...........................live")
                        cycle = 0
                        mas_url_temp.append(cur_url)
                        mas_univer_temp.append('')
                        mas_free_temp.append('')
                        mas_price_temp.append('')
                        mas_students_temp.append('')
                        mas_during_temp.append('')
                        mas_names_temp.append('')
                elif re.search(r'https://www.xuetangx.com/program', cur_url):
                    cur_url = re.search(r'https://www.xuetangx.com/program/[\D\d]*[/\?]', cur_url).group(0)
                    print(cur_url)
                    if (not cur_url in mas_url) and (not cur_url in mas_url_temp):
                        print("NEW...........................live")
                        cycle = 0
                        mas_url_temp.append(cur_url)
                        mas_univer_temp.append('')
                        mas_free_temp.append('')
                        mas_price_temp.append('')
                        mas_students_temp.append('')
                        mas_during_temp.append('')
                        mas_names_temp.append('')
                else:
                    cur_url = re.search(r'https://www.xuetangx.com/training/[\D\d]*[/\?]', cur_url).group(0)
                    if (not cur_url in mas_url) and (not cur_url in mas_url_temp):
                        print("NEW...........................training")
                        cycle = 0
                        mas_url_temp.append(cur_url)
                        mas_univer_temp.append('')
                        mas_free_temp.append('')
                        mas_price_temp.append('')
                        mas_students_temp.append('')
                        mas_during_temp.append('')
                        mas_names_temp.append('')
            links += 1

            time.sleep(2)
            driver.back()
            time.sleep(2)
            if (len(mas_url) == len_temp) and (len(mas_url_temp) == len_page):
                cycle = 0

        i = 0

        for i in range(len(mas_url_temp)):
            mas_names.append(mas_names_temp[i])
            mas_url.append(mas_url_temp[i])
            mas_free.append(mas_free_temp[i])
            mas_price.append(mas_price_temp[i])
            mas_students.append(mas_students_temp[i])
            mas_univer.append(mas_univer_temp[i])
            mas_during.append(mas_during_temp[i])


        #print('page =', page)
        print("(num_pages > 1) and (page != num_pages):", page, num_pages)
        if page != num_pages:
            if click_back:
                WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-prev")))
                prev = driver.find_element(By.CLASS_NAME, "btn-prev")
                actions.move_to_element(prev).perform()
                prev.click()
                num_back+=1
            else:
                for back in range(num_back+1):
                    print("next page")
                    WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-next")))
                    nxt = driver.find_element(By.CLASS_NAME, "btn-next")
                    actions.move_to_element(nxt).perform()
                    print("before click")
                    nxt.click()
                    print("after click")
                num_back = 0

        page += 1



    time.sleep(5)
except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()

df = pd.DataFrame(
    {'Name': mas_names, 'University': mas_univer, 'URL': mas_url, 'Students': mas_students,
     'Free': mas_free, 'Price': mas_price, 'Duration': mas_during})
df.to_excel('./Universities_all.xlsx', index=False)
#i = 0
#print(mas_url)
# while i < len(mas_url):
#   #  print(mas_url[i])
#     if re.search(r'https://www.xuetangx.com/live/[\D\d]*[/\?]', mas_url[i]):
#         mas_url.pop(i)
#     else:
#         i += 1
# mas_univer.insert(0,'')
# mas_url.insert(0,'')
# mas_students.insert(0,'')
# mas_free.insert(0,'')
# mas_price.insert(0,'')
# mas_during.insert(0,'')



# while i < len(mas_url):
#     if re.search(r'https://www.xuetangx.com/live/[\D\d]*[/\?]', mas_url[i]):
#         mas_url.pop(i)
#     else:
#         i += 1

# for i in range(len(mas_url)):
#     print(mas_univer[i], mas_url[i], mas_students[i], mas_price[i])