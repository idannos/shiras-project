import socket
import select
import json
import sys
import smtplib
import pickle
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

HTTP_FORMATS = ["GET", "POST"]


def valid_http(data):
    """
    :param data:
    :return: if the http is valid and relevant to us.
    """
    data = str(data, 'utf-8')

    temp = data.split(" ")
    if temp[0] in HTTP_FORMATS and "HTTP/1.1" in temp[2]:
        return True
    return False


def focus(data):
    """
    :param data:
    :return: the http format
    """
    data = str(data, 'utf-8')
    temp = data.split(" ")
    if temp[0] == "GET":
        return temp[1]
    elif temp[0] == "POST":
        data = data.split("\r\n\r\n")
        return data[1]


def clean(data):
    """
    :param data:
    :return: "cleaned" data- now python can understand the data
    """
    data = data.replace("%22", '"', 100)  # we want " instead %22
    data = data.replace("%20", ' ', 100)  # we want space instead %20
    data = data.replace("%3Cbr/%3E", "\n", 100)
    data = data.replace("<br/>", "\n", 100)
    return data


open_client_sockets = []
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 80))
server_socket.listen(100)
image = ""
while True:
    rlist, wlist, xlist = select.select(open_client_sockets + [server_socket], open_client_sockets, [])
    for current_socket in rlist:
        if current_socket is server_socket:
            (new_socket1, address1) = server_socket.accept()
            open_client_sockets.append(new_socket1)

        else:
            data = current_socket.recv(4096)
            if data != "":
                image = ""
                original_data = data
                if valid_http(data):
                    data = focus(data)
                    if data == "/":
                        f = open("index.html", "r")
                        txt = f.read()
                        txt = str.encode("HTTP/1.1 200 Ok\r\n\r\n" + txt)
                        current_socket.send(txt)
                        f.close()
                    if data == "/favicon.ico":
                        try:
                            with open("image.png", "rb") as image_file:
                                a = image_file.read()
                                current_socket.send(a)
                                image_file.close()
                        except:
                            # print("no favicon image in this server")
                            pass
                    else:
                        data = clean(data)
                        if data != "/":
                            # print(data)
                            if data != "ended":
                                with open("image.txt", "a") as fe:
                                    fe.write(data)

                            if data == "ended":
                                with open("image.txt", "r") as f:
                                    image1 = f.read()
                                    #print(image1)

                                with open("ImageSentFromClient.png", "wb") as fh:
                                    fh.write(base64.decodebytes(str.encode(image1)))
                                    print("wrote image")
                                with open("image.txt", "wb") as ff:
                                    ff.write(str.encode(""))
                            to_send = "henlo"
                            to_send = str.encode("HTTP/1.1 200 Ok\r\n\r\n" + to_send)
                            current_socket.send(to_send)
            # print(image)

            open_client_sockets.remove(current_socket)
            current_socket.close()
