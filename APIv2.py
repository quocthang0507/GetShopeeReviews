import urllib.request
import json


def get_json_ratings(itemid, limit, offset, shopid):
	url = 'https://shopee.vn/api/v2/item/get_ratings?filter=0&flag=1&itemid={}&limit={}&offset={}&shopid={}&type=0'.format(
		itemid, limit, offset, shopid)
	response = urllib.request.urlopen(url)
	data = json.loads(response.read)
	return data


if __name__ == '__main__':
	print(get_json_ratings(3631471845, 6, 0, 31982992))
