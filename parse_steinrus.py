from bs4 import BeautifulSoup
import requests
import pandas as pd
from time import sleep
from pprint import pprint
from random import randrange
import os.path


HOST_URL = 'https://steinrus.ru'
PROJECT_NAME = "parse_steinrus"
GUID = "2B651BA8-E029-869E-561E-21FB43148D88"
df = pd.DataFrame(columns=[
    'cml group id идентификатор группы товаров',
    'Артикул товара',
    'Название товара',
    'Текст для товара',
    'Цена товара',
    'Путь к товару',
    'Название единицы измерения',
    'Файл изображения для товара',
    'Толщина',
    'Количество м.кв в поддоне',
    'Характеристики (внизу страницы)',
    'Порядок сортировки товара',
    'Фото товара 1',
    'Фото товара 2',
    'Фото товара 3',
    'Фото на объекте 1',
    'Фото на объекте 2',
    'Фото на объекте 3'])



def get_sitemap():
    filename = PROJECT_NAME + '_sitemap.xml'
    host_url = HOST_URL + "/sitemap.xml"
    try:
        with open(filename, 'r') as file:
            content = file.read()
    except IOError:
        content = requests.get(host_url).content
        with open(filename, mode='wb') as localfile:
            localfile.write(content)
        localfile.close()
    return content


def get_page_content(item_url, path):
    filename = './html_pages/' + path + '.html'
    try:
        with open(filename, 'r') as file:
            content = file.read()
    except IOError:
        response = requests.get(item_url)
        sleep(randrange(5) + 1)
        if response.status_code == 200:
            content = response.content
        else:
            return ""
        with open(filename, mode='wb') as localfile:
            localfile.write(content)
        localfile.close()
    return content


def get_pages_urls():
    soup = BeautifulSoup(get_sitemap(), 'lxml')  # choose lxml parser
    links = [loc.text for loc in soup.find_all("loc")]
    links = [x for x in links if "colormix" in x]
    links = [x for x in links if ("trotuarnaya-plitka" in x) or ("bordyurniy-kamen" in x and "bordur-sadovui" in x)]
    return links


def dowload_img(url):
    filename = './images/' + url.rsplit('/', 2)[-1]
    if not os.path.isfile(filename):
        response = requests.get(url)
        sleep(randrange(5) + 1)
        if response.status_code == 200:
            content = response.content
        else:
            return
        with open(filename, mode='wb') as localfile:
            localfile.write(content)
        localfile.close()
    return


def get_image_array(soup_item):
    arr = ["", "", "", ""]
    found = soup_item.find("img", itemprop = "image")
    arr[0] = found['src'] if found else ""
    dowload_img(HOST_URL + arr[0])
    arr[0] = '/tmp/' + arr[0].rsplit('/', 2)[-1]
    title = soup_item.find("ul", {"class", "variants_list"})
    if not title:
        return arr
    links = title.findAll("img")
    if links:
        for i, link in enumerate(links[:3]):
            dowload_img(HOST_URL + link['src'])
            arr[i + 1] = '/tmp/' + link['src'].rsplit('/', 2)[-1]
    return arr


def get_oimage_array(soup_item):
    arr = ["", "", ""]
    title = soup_item.find("section", {"class", "item_objects"})
    if not title:
        return arr
    links = title.findAll("a", {"class", "fancybox"})
    if links:
        for i, link in enumerate(links[:3]):
            dowload_img(HOST_URL + link['href'])
            arr[i] = '/tmp/' + link['href'].rsplit('/', 2)[-1]
    return arr


def get_item_sizes(soup_item):
    item_sizes = soup_item.find("section", {"class", "item_tech"})
    item_sizes = str(item_sizes) if item_sizes else ""
    # item_sizes = item_sizes.replace("https://braer.ru/storage/params/xs/200_5wvd32mh.png", "/i/ico_height.png")
    # item_sizes = item_sizes.replace("https://braer.ru/storage/params/xs/36.png", "/i/ico_weight.png")
    # item_sizes = item_sizes.replace("https://braer.ru/storage/params/xs/colormix_malva.png", "/i/ico_color.png")
    return item_sizes


def get_thickness(soup_item):
    thickness = soup_item.find("section", {"class", "item_tech"})
    if thickness:
        thickness = thickness.find("table").findChildren("tr")[-1].findChildren("td")[-1]
        thickness = thickness.get_text() + 'мм' if thickness else ""
    else:
        thickness = ""
    return thickness


def get_pallet_count(soup_item):
    pallet_count = soup_item.find("section", {"class", "item_tech"})
    if pallet_count:
        pallet_count = pallet_count.findAll("table")[-1].findAll("td")[2]
        pallet_count = pallet_count.get_text() if pallet_count else ""
    else:
        pallet_count = ""
    return pallet_count


def get_item_text(soup_item):
    item_text = soup_item.find("section", {"class", "item_desc"})
    if item_text:
        item_text = str(item_text) if item_text else ""
    else:
        item_text = ""
    return item_text


def get_item_price(soup_item):
    item_price = soup_item.find("span", {"class", "old-price"})
    if item_price:
        item_price = item_price.get_text()[0:-2]
    else:
        item_price = soup_item.find("span", {"class", "price"}).find("b")
        item_price = item_price.get_text() if item_price else ""
    return item_price


def get_order(item_name, idx):
    if ('Старый город' in item_name):
        return 9
    return (idx + 1) * 10


# print("\n".join(get_pages_urls()))
for idx, item_url in enumerate(get_pages_urls()):
    if idx < 200:
        path = item_url.rsplit('/', 2)[-1]
        content = get_page_content(item_url, path)
        if not len(content):
            continue
        print(idx)
        print(item_url)
        soup_item = BeautifulSoup(content, 'lxml')
        item_name = soup_item.find("h1", itemprop = "name").get_text()
        item_text = get_item_text(soup_item)
        item_price = get_item_price(soup_item)
        item_sizes = get_item_sizes(soup_item)
        img = get_image_array(soup_item)
        img_o = get_oimage_array(soup_item)
        thickness = get_thickness(soup_item)
        pallet_count = get_pallet_count(soup_item)
        # print(pallet_count)
        order = get_order(item_name, idx)
        if ('Тротуарная плитка' in item_name and thickness == '60мм'):
            item_sizes = item_sizes + '<p>* &mdash; у этой плитки также есть высота h — 40мм, информацию уточняйте у менеджеров.</p>'
        if (('Тротуарная плитка' in item_name and thickness == '60мм') or not
                ('Тротуарная плитка' in item_name)):
            df.loc[idx] = [GUID, path, item_name, item_text, item_price, path,
                'м2', img[0], thickness, pallet_count, item_sizes, order,
                img[1], img[2], img[3], img_o[0], img_o[1], img_o[2]]
df.to_csv(PROJECT_NAME + '_output.csv', index=False)
