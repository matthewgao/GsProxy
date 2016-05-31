#! /usr/bin/env python3

import re

target_str = b'GET http://mat1.gtimg.com/www/css/qq2012/hot_word_sogou.css HTTP/1.1\r\nHost: mat1.gtimg.com\r\nProxy-Connection: keep-alive\r\nCache-Control: max-age=0\r\nAccept: text/css,*/*;q=0.1\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36\r\nReferer: http://www.qq.com/\r\nAccept-Encoding: gzip, deflate, sdch\r\nAccept-Language: en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4\r\n\r\n'

m = re.compile(b'(?<=\r\nHost:).*\r\n')
# m.match(target_str).groups()
print(m.search(target_str).group(0))