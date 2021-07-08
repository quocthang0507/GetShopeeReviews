import urllib.request
import json


def get_json(itemid, limit, offset, shopid):
    url = 'https://shopee.vn/api/v2/item/get_ratings?filter=0&flag=1&itemid={}&limit={}&offset={}&shopid={}&type=0'.format(
        itemid, limit, offset, shopid)
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    return data


def get_ratings_from_json(json, allow_null=True):
    data = json['data']
    ratings = data['ratings']
    result = []
    if ratings != None:
        for r in ratings:
            rating_star = r['rating_star']
            comment = r['comment']
            if comment != '' or (comment == '' and allow_null):
                result.append((rating_star, comment))
    return result


def get_all_ratings(itemid, shopid, limit=6, offset=0):
    result = []
    while True:
        json = get_json(itemid, limit, offset, shopid)
        ratings = get_ratings_from_json(json)
        if ratings == []:
            break
        else:
            result.append(ratings)
        offset += limit
    return result


if __name__ == '__main__':
    print(get_all_ratings(9154894255, 36333676))
