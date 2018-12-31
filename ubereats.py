import csv
from selenium import webdriver
import time
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys
import json

urls = []
city_names = []
data = {}

driver = webdriver.Chrome()
# ubereatsURL.tsv contains list of lists and every item in list have City name on 0th element and URL to city for ubereats on 1st element position
# This is a tab separated file
# For example, Abilene	https://ubereats.com/abilene/
with open('ubereatsURL.tsv') as tsvfile:
	for item in tsvfile:
		urls.append(item.split('\t')[1].strip('\n').strip())
		city_names.append(item.split('\t')[0].strip())
		data[item.split('\t')[0].strip()] = []
for index, url in enumerate(urls):
	while 1:
		try:
			driver.get(url)
			break
		except:
			continue
	try:
		title = driver.find_element_by_css_selector('div.base_ h1').text
	except:
		data[city_names[index]] = 'No Data Availabe'
		continue
	if 'not found' in title.lower():
		data[city_names[index]] = 'Page Not Found'
		continue
	restaurant_url = driver.find_elements_by_css_selector('div.base_ a.base_')
	lenOfPage = driver.execute_script("var lenOfPage=document.body.scrollHeight;return lenOfPage;")
	current_position = 1000
	ru = []
	for i in restaurant_url:
		ru.append(i.get_attribute('href'))
	while current_position < lenOfPage:
		driver.execute_script("window.scrollTo(0, " + str(current_position)+ ")")
		restaurant_url = driver.find_elements_by_css_selector('div.base_ a.base_')
		time.sleep(5)
		for j in restaurant_url:
			try:
				ru.append(j.get_attribute('href'))
			except:
				pass
		current_position = current_position + 1000
	resurl = set(ru)
	print('//////////////////////////////////////')
	print(len(resurl))
	print('---------')
	print(city_names[index])
	if len(resurl) == 0:
		data[city_names[index]] = 'No Data Availabe'
		continue
	print('//////////////////////////////////////')
	for res_count, k in enumerate(resurl):
		print('================================')
		print(res_count)
		while 1:
			try:
				driver.get(k)
				break
			except:
				continue
		restaurant_name = driver.find_element_by_xpath('//div[contains(@class,"content_")]//h1').text
		cousine_name = driver.find_element_by_xpath('//div[contains(@class,"content_")]//h1/../div/div').text
		print(restaurant_name)
		print(cousine_name.strip('$').strip().split('•'))
		subsec = driver.find_elements_by_xpath('//div[contains(@id,"subsection")]')
		sub_category = []
		temp = []
		print('Sub Sections:')
		for ss in subsec:
			print(ss.text.strip())
			sub_category.append(ss.text.strip())
			temp.append(ss.text.strip())
		print('-----------------')
		actual_subcat = {}
		dishes = driver.find_elements_by_xpath('//div[contains(@id,"subsection")]/../div/*')
		for p in sub_category:
			print('SubCategory: ', p)
			for ds in dishes:
				if len(ds.text.split('\n')) == 1:
					if ds.text.split('\n')[0] == p:
						try:
							del temp[0]
						except:
							pass
						actual_subcat[p] = []
						continue
					if temp:
						if ds.text.split('\n')[0] == temp[0]:
							break
				if p in actual_subcat:
					actual_subcat[p].append(ds.text.split('\n'))
		data[city_names[index]].append({'Restaurant Name': restaurant_name, 'Cuisine Type(s)': cousine_name.strip('$').strip().split('•'), 'Menu': actual_subcat})
		restaurant_name = ''
		cousine_name = ''
		actual_subcat = ''
	print('==============================================================')

with open('ubereats1.json', 'w') as fp:
	json.dump(data, fp)