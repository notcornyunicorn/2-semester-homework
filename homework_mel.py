import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')
import re
import urllib.request
import json


def vk_api(method, **kwargs):
    api_request = 'https://api.vk.com/method/'+method + '?'
    api_request += '&'.join(['{}={}'.format(key, kwargs[key]) for key in kwargs])
    req = urllib.request.Request(api_request)
    with urllib.request.urlopen(req) as response:
        res = response.read().decode('utf-8')
    return json.loads(res)


def download_posts(domain):
	posts = []
	result = vk_api('wall.get', domain=domain, count=100)
	count = result['response'][0]
	posts = result['response'][1:]
	while len(posts) < 150:
		result = vk_api('wall.get', domain=domain, count=100, offset=len(posts))
		posts += result['response'][1:]
	return posts



def age(bdate):
	day_now = 1
	month_now = 5
	year_now = 2017
	res = re.search('((([1-3]?[0-9])\.)?(1?[0-9])\.)?([0-9]{4})', bdate)
	try:
		year = int(res.group(5))
		age = year_now - year
	except:
		return None
	try:
		month = int(res.group(4))
		if month > month_now:
			return age - 1
		elif month < month_now:
			return age
		else:
			try:
				day = int(res.group(3))
				if day > day_now:
					return age - 1
				else:
					return age
			except:
				return age
	except:
		return age

def download_comments(posts):
	for post in posts:
		comments = []
		result = vk_api('wall.getComments', owner_id=post['to_id'], post_id=post['id'], count=100)
		count = result['response'][0]
		comments += result['response'][1:]
		while len(comments) < count:
			result = vk_api('wall.getComments', owner_id=post['to_id'], post_id=post['id'], count=len(comments))
			comments += result['response'][1:]
		post['comments'] = comments
		for i, comment in enumerate(post['comments']):
			post['comments'][i]['city'], post['comments'][i]['age'] = get_city_age(comment)
			post['comments'][i]['len'] = len(post['comments'][i]['text'].split( ))
	return posts
	

def get_city_age(post):
	if post['from_id'] < 0:
		return None, None
	else:
		result = vk_api('users.get', user_ids=post['from_id'], fields='city,bdate')
		try:
			city =  result['response'][0]['city']
		except:
			city = None
		try:
			user_age = age(result['response'][0]['bdate'])
		except:
			user_age = None
		return city, user_age


def graph_length(posts):
	lengths = []
	for post in posts:
		count = len(post['comments'])
		if count > 0:
			sum_comments = 0
			for comment in post['comments']:
				sum_comments += comment['len']
			lengths.append((post['len'], sum_comments/count))
		else:
			lengths.append((post['len'], 0))

	lengths.sort()
	lens = []
	i = 0
	el = 0
	while i <= max(lengths)[0]:
		while lengths[el][0] > i:
			i += 1
		count = 0
		sum_el = 0
		while len(lengths) > el and lengths[el][0] == i:
			count += 1
			sum_el += lengths[el][1]
			el += 1
		lens.append((lengths[el-1][0], sum_el/count))
		i += 1

	plt.figure(figsize=(20,10))
	keys = [i[0] for i in lens]
	values = [i[1] for i in lens]
	plt.bar(keys, values)
	plt.savefig('длина-поста-длина-коммента.png')


def graph_city_comment_length(posts):
	comments = [comment for post in posts for comment in post['comments'] if comment['city']]
	cities = [(comment['city'], comment['len']) for comment in comments]

	cities.sort()
	cities_lens = []
	i = 0
	el = 0
	while i <= max(cities)[0]:
		while cities[el][0] > i:
			i += 1
		count = 0
		sum_el = 0
		while len(cities) > el and cities[el][0] == i:
			count += 1
			sum_el += cities[el][1]
			el += 1
		cities_lens.append((cities[el-1][0], sum_el/count))
		i += 1
        cities_lens = sorted(cities_lens, key=lambda city: city[1], reverse=True)
	plt.figure(figsize=(20,10))
	plt.bar(
		range(len(cities_lens)),
		[i[1] for i in cities_lens]
	)
	plt.xticks(
		range(len(cities_lens)),
		[i[0] for i in cities_lens],
		rotation = 'vertical'
	)
	plt.savefig('город-длина-коммента.png')


def graph_age_comment_length(posts):
	comments = [comment for post in posts for comment in post['comments'] if comment['age']]
	ages = [(comment['age'], comment['len']) for comment in comments]

	ages.sort()
	ages_lens = []
	i = 0
	el = 0
	while i <= max(ages)[0]:
		while ages[el][0] > i:
			i += 1
		count = 0
		sum_el = 0
		while len(ages) > el and ages[el][0] == i:
			count += 1
			sum_el += ages[el][1]
			el += 1
		ages_lens.append((ages[el-1][0], sum_el/count))
		i += 1

	plt.figure(figsize=(20,10))
	keys = [i[0] for i in ages_lens]
	values = [i[1] for i in ages_lens]
	plt.bar(keys, values)
	plt.savefig('возраст-длина-коммента.png')


def main():
	posts = download_posts('melfmru')

	for post in posts:
		post['len'] = len(post['text'].split( ))
		#Все посты от сообщества, поэтому не извлекаю город и возраст.
	#with open('posts.json', 'r', encoding='utf-8') as f:
	#with open('posts.json', 'w', encoding='utf-8') as f:
		#json.dump(posts, f, ensure_ascii=False, indent = 4)
		#posts = json.loads(f.read())

	posts = download_comments(posts)

	with open('posts.json', 'w', encoding='utf-8') as f:
		json.dump(posts, f, ensure_ascii=False, indent = 4)

	graph_length(posts)
	graph_city_comment_length(posts)
	graph_age_comment_length(posts)


if __name__ == '__main__':
	main()
