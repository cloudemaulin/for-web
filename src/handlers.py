import socket
import ssl
import re
import html2text
import json
from collections import Counter
from nltk.corpus import stopwords
from urllib.parse import ParseResult

STOP_WORDS = set(stopwords.words("english"))


def handle_keywords(url: ParseResult) -> str:
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.settimeout(1)
    socket_ssl: ssl.SSLSocket = ssl.wrap_socket(
        socket_, ssl_version=ssl.PROTOCOL_TLSv1_2)
    addr = (url.netloc, 443)
    socket_ssl.connect(addr)
    socket_ssl.send(f'\
GET {url.path} HTTP/1.1\r\n\
Host: {url.netloc}\r\n\r\n'.encode())
    response, data = socket_ssl.recv(2048), b''
    while response:
        data += response
        try:
            response = socket_ssl.recv(2048)
        except socket.error:
            break
    socket_ssl.close()
    parser = html2text.HTML2Text()
    parser.ignore_links = True
    text = parser.handle(data.decode())
    text = re.sub(r'[^a-zA-Z_]', ' ', text).strip().lower().split()
    text = [word for word in text if word and word not in STOP_WORDS]
    counter = Counter(text)
    return json.dumps(dict(counter.most_common(10)))
