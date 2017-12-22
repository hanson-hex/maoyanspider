# /usr/bin/env python
# -*- coding:utf-8 -*-

import re
import json
import requests
import os
from fake_useragent import UserAgent
from requests import RequestException
from multiprocessing import Pool
import time
from time import clock
from multiprocessing.dummy import Pool as threadPool

class Model(object):
    """
    基类, 用来显示类的信息
    """

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s

    def json(self):

        """
        返回当前 model 的字典表示
        """
        # copy 会复制一份新数据并返回
        d = self.__dict__.copy()
        return d


class Movie(Model):
    """
    存储电影信息
    """
    def __init__(self):
        self.name = ''
        self.score = ''
        self.actors = ''
        self.cover_url = ''
        self.release_time = ''
        self.ranking = 0


def cache(url):
    """
    用于缓存，避免多次请求，费时
    """
    folder = 'cached'
    file_name = url.split('=')[-1] + '.html'
    # file_name = '0.html'
    path = os.path.join(folder, file_name)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            content = f.read()
            return content.decode('utf-8')
    else:
        # if not os.path.exists(folder):
        #     os.mkdir(folder)
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                with open(path, 'wb') as f:
                    f.write(response.content)
                    f.close()
                return response.text
            return None
        except RequestException:
            return None


def movie_from_url(url):
    """
    解析DOM
    """
    response = cache(url)
    # print(response)
    pattern = re.compile(r'<dd>.*?board-index.*?>(\d+)</i>.*?title="(.*?)".*?data-src="(.*?)"'
                         + '.*?class="star">(.*?)</p>.*?class="releasetime">(.*?)</p>.*?class="integer">'
                         + '(.*?)</i>.*?class="fraction">(.*?)</i></p>.*?</dd>', re.S)
    items = re.findall(pattern, response)
    print(items)
    for item in items:
        m = Movie()
        m.ranking = int(item[0])
        m.name = item[1]
        m.cover_url = item[2]
        m.actors = item[3].strip()[3:]
        m.release_time = item[4].strip()[5:]
        m.score = item[5] + item[6]
        yield m


def write_to_file(content):
    """
    写入文档里
    """
    with open('result.text', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False, indent=4))
        f.close()


def main(offset):
    """
    主函数入口
    """
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    print(url)
    for movie in movie_from_url(url):
        write_to_file(movie.json())


if __name__ == '__main__':
    # # 多进程
    # start = clock()
    # pool = Pool(1)
    # pool.map(main, [i * 10 for i in range(10)])
    # pool.close()
    # pool.join()
    # end = clock()
    # print(start, end)
    # print((end - start))
    # #
    # # 单进程
    # start = clock()
    # for i in range(10):
    #     main(i * 10)
    # end = clock()
    # print((end - start))
    # 多线程
    start = clock()
    pool = threadPool(1)
    pool.map(main, [i * 10 for i in range(10)])
    pool.close()
    pool.join()
    end = clock()
    print(start, end)
    print((end - start))
