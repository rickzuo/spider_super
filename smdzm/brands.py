import os

import requests
from bs4 import BeautifulSoup
import csv

import setttings.private as conf

start_url = "https://pinpai.smzdm.com/jp/"

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Cookie": "device_id=213070643316549918053847426bb7dca31bf1c8f6dea25e1f1fe467b6; r_sort_type=score; smzdm_user_source=634D546D37F947A2FF617F6A6C803EC9; homepage_sug=a; Hm_lvt_9b7ac3d38f30fe89ff0b8a0546904e58=1679807817; __ckguid=jNr2WVaPraBVfJPy2cocwy5; __jsluid_s=9503cb835a8055b59284da83dcf17e54; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221815532dce2497-04fc245f49e8b3-26021b51-2073600-1815532dce376a%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%2C%22%24latest_landing_page%22%3A%22https%3A%2F%2Fpinpai.smzdm.com%2Fjp%2F%22%7D%2C%22%24device_id%22%3A%221815532dce2497-04fc245f49e8b3-26021b51-2073600-1815532dce376a%22%7D",
    "Host": "pinpai.smzdm.com",
    "Pragma": "no-cache",
    "Referer": "https://pinpai.smzdm.com/jp/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
}

parse_urls = [start_url]

csv_filename = 'brand.csv'

def crawl(url):
    print(f"crawl url:{url}")
    parse_urls.append(url)
    resp = requests.get(url, headers=headers)
    text = resp.text
    parse(text)
    next_page = parse_next_page(text)
    if next_page not in parse_urls and next_page:
        crawl(next_page)


def parse(html_doc):
    # 创建beautifulsoup解析对象
    soup = BeautifulSoup(html_doc, 'html.parser')
    # 根据属性，获取标签的属性值，返回值为列表
    # 查找所有a标签并返回
    ul_text = soup.find("ul", class_="brands")
    li_list = ul_text.find_all("li")
    brand_list = []
    for tag in li_list:
        img_ele = tag.find("a").find("img")
        brands_ele = tag.find("div", class_="brands-name")
        img_url = "https:" + img_ele["src"]
        brands_name = brands_ele.text
        print(brands_name, img_url)

        img_url_split = img_url.split("/")
        new_img_url = conf.IMAGE_PREFIX_URL+img_url_split[len(img_url_split) - 1]

        brand_list.append({"name":brands_name,"img_url":new_img_url})

    save_to_csv(brand_list)

def read_csv():
    data = []
    with open(csv_filename, 'r') as f:
        lines = f.readlines()
    for line in lines:
        rows = line.replace("\n","")
        data.append(rows)
    return data

def download_image():
    rows = read_csv()
    for row in rows:
        ele = row.split(",")
        img_url = ele[1]
        save_img(img_url)

# def get_file_format():
def save_to_csv(lines):
    with open(csv_filename, 'a+') as f:
        write = csv.writer(f)
        for data in lines:
            write.writerow([data["name"],data["img_url"]])


def save_img(img_url):
    urlSplit = img_url.split("/")
    file_suffix = urlSplit[len(urlSplit) - 1]
    file_path = f"static/images/{file_suffix}"
    print(f"start save image:{img_url}")
    if os.path.exists(file_path):
        print(f"file {file_path} exist")
        return
    r = requests.get(img_url)

    with open(file_path,"wb") as f:
        f.write(r.content)
    print(f"save image:{img_url} done.")

def parse_next_page(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    ul_text = soup.find("ul", id="J_feed_pagenation")
    # next_page_ele = ul_text.find("li",class_="page-number current").next_sibling
    next_page_ele = ul_text.find("li", class_="page-turn next-page")
    if not next_page_ele:
        print("not found next page")
        return
    next_page = next_page_ele.find("a")["href"]
    print(f"next_page:{next_page}")
    return next_page


if __name__ == '__main__':
    crawl(start_url)
    # download_image()
    # img_url = "https://y.zdmimg.com/202211/25/6380703a6d5392946.jpg_d200.jpg "




