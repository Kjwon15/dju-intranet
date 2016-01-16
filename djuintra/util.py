encode_map = {
    '0': 'W4-',
    '1': 'W1-',
    '2': 'LT-',
    '3': 'LK-',
    '4': 'L0-',
    '5': 'L2-',
    '6': 'LW-',
    '7': 'LL-',
    '8': 'LS-',
    '9': 'L7-',
}


def get_photo_url(userid):
    encoded = ''.join(map(encode_map.get, str(userid)))
    return 'http://was81.dju.kr/photos/{}.jpg'.format(encoded)
