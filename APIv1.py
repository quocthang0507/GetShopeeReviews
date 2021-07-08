import urllib.request
import json
import datetime
import time
import re


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


def remove_adjacent_duplicates(str):
    return re.sub(r'(.)\1+', r'\1\1', str)


def format_string(str):
    if str:
        vietnamese_chars = ' ,.\n\tABCDEGHIKLMNOPQRSTUVXYabcdeghiklmnopqrstuvxyÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
        bad_chars = [('\t', ', '), ('\n', '. '), ('  ', ' '), (' .', '.'),
                     (' ,', ','), ('..', '.'), (',,', ','), (',.', '.'), ('.,', ',')]
        # Keep only specific characters
        str = ''.join(c for c in str if c in vietnamese_chars)
        str = remove_adjacent_duplicates(str)
        for c in bad_chars:
            str = str.replace(c[0], c[1])
        str = str.strip()
    return str


def get_ratings_from_json(json_data, min_len_str=4):
    data = json_data['data']
    ratings = data['ratings']
    result = []
    if ratings != None:
        for r in ratings:
            itemid = r['itemid']
            shopid = r['shopid']
            userid = r['userid']
            cmtid = r['cmtid']
            mtime = datetime.datetime.fromtimestamp(
                r['mtime']).strftime('%d-%m-%Y %H:%M:%S')
            rating_star = r['rating_star']
            comment = format_string(r['comment'])
            if len(comment) >= min_len_str:
                result.append(
                    {
                        'itemid': itemid,
                        'shopid': shopid,
                        'userid': userid,
                        'cmtid': cmtid,
                        'mtime': mtime,
                        'rating_star': rating_star,
                        'comment': format_string(comment)
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


def get_all_ratings(itemid, shopid, limit=6, offset=0, min_len_str=4):
    result = []
    while True:
        json_data = get_json_product(itemid, limit, offset, shopid)
        ratings = get_ratings_from_json(json_data, min_len_str)
        if ratings == []:
            break
        else:
            result += ratings
        offset += limit
    return result


def get_all_products(max_products=100, limit=10, offset=0):
    result = []
    if max_products < limit:
        limit = max_products
    while True:
        start_time = time.time()
        # Notes: The number of products may be smaller than limit number although max_products < limit
        # So the number of result can be larger than the max_products
        json_data = get_json_recommend(limit, offset)
        products = get_products_from_json(json_data)
        if products == [] or len(result) >= max_products:
            break
        else:
            result += products
            print('Đã lấy về {} sản phẩm trên tổng số tối đa {} sản phẩm. Mất {:0.2f} mili giây'.format(
                len(result), max_products, (time.time() - start_time)*1000))
        offset += limit
    return result


def export_to_text_file(array_of_json, filename, only_header=False):
    f = open(filename, 'a+', encoding='utf-8')
    if only_header:
        f.write('userid\tmtime\trating_star\tcomment\n')
    else:
        for j in array_of_json:
            f.write('{}\t{}\t{}\t{}\n'.format(
                j['userid'], j['mtime'], j['rating_star'], j['comment']))
    f.close()


def collect_reviews_product(max_products, min_len_str=4):
    products = get_all_products(max_products)
    length_products = len(products)
    export_to_text_file(None, 'sentiments.txt', True)
    for p in products:
        start_time = time.time()
        itemid = p['itemid']
        shopid = p['shopid']
        ratings = get_all_ratings(itemid, shopid, min_len_str=min_len_str)
        length_products -= 1
        export_to_text_file(ratings, 'sentiments.txt')
        print('Đã thu thập và ghi {} đánh giá của sản phẩm {} tại shop {}. Còn {} sản phẩm nữa. Mất {:0.2f} mili giây'.format(
            len(ratings), itemid, shopid, length_products, (time.time() - start_time)*1000))


if __name__ == '__main__':
    # print(get_all_ratings(9154894255, 36333676))
    collect_reviews_product(5)
