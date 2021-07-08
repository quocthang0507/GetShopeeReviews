import urllib.request
import json


def get_json_product(itemid, limit, offset, shopid):
    url = 'https://shopee.vn/api/v2/item/get_ratings?filter=0&flag=1&itemid={}&limit={}&offset={}&shopid={}&type=0'.format(
        itemid, limit, offset, shopid)
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    return data


def get_json_recommend(limit, offset):
    url = 'https://shopee.vn/api/v4/recommend/recommend?bundle=daily_discover_main&limit={}&offset={}'.format(
        limit, offset)
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    return data


def get_ratings_from_json(json_data, allow_null=True):
    data = json_data['data']
    ratings = data['ratings']
    result = []
    if ratings != None:
        for r in ratings:
            itemid = r['itemid']
            shopid = r['shopid']
            rating_star = r['rating_star']
            comment = r['comment']
            if comment != '' or (comment == '' and allow_null):
                result.append(
                    {
                        'itemid': itemid,
                        'shopid': shopid,
                        'rating_star': rating_star,
                        'comment': comment
                    })
    return result


def get_products_from_json(json_data, get_top_product=False):
    data = json_data['data']
    sections = data['sections']
    result = []
    for s in sections:
        data = s['data']
        item = data['item']
        if item != None:
            for i in item:
                shopid = i['shopid']
                itemid = i['itemid']
                result.append(
                    {
                        'shopid': shopid,
                        'itemid': itemid
                    })
        if get_top_product:
            top_product = data['top_product']
            for t in top_product:
                list = t['list']
                data = list['data']
                item_lite = data['item_lite']
                if item_lite != None:
                    for i in item_lite:
                        shopid = i['shopid']
                        itemid = i['itemid']
                        result.append(
                            {
                                'shopid': shopid,
                                'itemid': itemid
                            })
    return result


def get_all_ratings(itemid, shopid, limit=6, offset=0):
    result = []
    while True:
        json_data = get_json_product(itemid, limit, offset, shopid)
        ratings = get_ratings_from_json(json_data)
        if ratings == []:
            break
        else:
            result += ratings
        offset += limit
    return result


def get_all_products(max=100, limit=10, offset=0):
    result = []
    while True:
        json_data = get_json_recommend(limit, offset)
        products = get_products_from_json(json_data)
        if products == [] or len(result) == max:
            break
        else:
            result += products
        offset += limit
    return result


if __name__ == '__main__':
    # print(get_all_ratings(9154894255, 36333676))
    print(get_all_products())
