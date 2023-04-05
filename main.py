import requests
from bs4 import BeautifulSoup
from lxml import etree
import csv

url = "https://restaurants.pizzahut.co.in/"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
dom = etree.HTML(str(soup))
i = 2
state_list = []
while True:
    try:
        state_list.append(dom.xpath(f"/html/body/section[1]/div/div/div[1]/div/div/div[2]/div[2]/form/ul/li[1]/select/option[{i}]")[0].text)
        i += 1

    except IndexError:
        break
print(state_list)
state_list_url = ["https://restaurants.pizzahut.co.in/"+x.replace(" ","%20") for x in state_list]
print(state_list_url)

def get_iterator(dom,xpath):
    tmp = []
    i = 1
    while True:
        try:
            tmp.append(dom.xpath(xpath.format(i))[0].text)
            i += 1

        except IndexError:
            break
    return tmp



main_list = []
for cnt,state_link in enumerate(state_list_url):
    pgs = 1
    while True:
        response_tmp = requests.get(state_link+f"?page={pgs}")
        soup = BeautifulSoup(response_tmp.content, "html.parser")
        dom = etree.HTML(str(soup))
        if soup.find_all("div",{"class":"no-outlets"}):
            print(f"Only {pgs-1} pages and done with {state_list[cnt]}")
            break
        lats = [lat['value'] for lat in soup.find_all("input",{"class":"outlet-latitude"})]
        longs = [long['value'] for long in soup.find_all("input",{"class":"outlet-longitude"})]
        names = get_iterator(dom,"/html/body/section[2]/div/div[1]/div[2]/div/div[{}]/ul/li[2]/div[2]")
        adds = get_iterator(dom,"/html/body/section[2]/div/div[1]/div[2]/div/div[{}]/ul/li[3]/div[2]/span[1]")
        adds2 = get_iterator(dom,"/html/body/section[2]/div/div[1]/div[2]/div/div[{}]/ul/li[3]/div[2]/span[2]/span")
        adds3 = ["".join([add.text for add in j]) for j in soup.find_all("span",{"class":"merge-in-next"})]

        main_list.extend(list(zip(names,adds,adds2,adds3,lats,longs)))
        pgs += 1

with open('data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    field = ["Store Name", "Address", "Timings","Phone Number","Latitude","Longitude"]
    writer.writerow(field)
    for i in main_list:
        writer.writerow([i[0],i[1]+", "+i[2]+", "+i[3],"Open until 11:00 PM","18002022022",i[4],i[5]])
