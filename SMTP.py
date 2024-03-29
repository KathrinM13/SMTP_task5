import base64
import codecs
import socket
import ssl
import configparser
import datetime


class UnsupportedTypeError(Exception):
    pass


def create_boundary():
    return str(hash(datetime.datetime.now()))


def read_message():
    text = ''
    with open('message/message.txt', 'r', encoding='utf-8') as f:
        for line in f:
            if line[-1] == '\n' and line.count('.') == len(line) - 1 \
                    and len(line) - 1 != 0:
                text += line[:-1] + '.\n'
            elif line.count('.') == len(line) and len(line) != 0:
                text += line + '.'
            else:
                text += line
        return text


def get_type(type):
    if type == 'jpeg' or type == 'jpg':
        return 'image/jpeg;'
    elif type == 'png':
        return 'image/png;'
    elif type == 'pdf':
        return 'application/pdf;'
    elif type == 'zip':
        return 'application/zip;'
    else:
        raise UnsupportedTypeError()


def get_code_file_base64(a):
    with open('message/' + a, 'br') as f:
        return base64.b64encode(f.read())


def form_message(theme, addresses, message, attachmenets):
    text = ""
    text += "From: malyhyekaterina@mail.ru\n"
    text += "To: " + ','.join(addresses) + '\n'
    text += "Subject: " + '=?UTF-8?B?' + base64.b64encode(
        theme.encode()).decode() + '?=' + '\n'
    if attachments:
        text += "Content-Type: multipart/mixed; boundary =" + boundary + "\n\n\n"
        if message:
            text += '--' + boundary + '\n'
            text += 'Content-Type: text/plain; charset=utf-8\n\n'
            text += message
        for a in attachments:
            name_base64 = '"=?UTF-8?B?' + base64.b64encode(
                a.encode()).decode() + '?="'
            text += '--' + boundary + '\n'
            text += 'Content-Disposition: attachment; filename=' + name_base64 + '\n'
            text += 'Content-Transfer-Encoding: base64\n'
            text += "Content-Type: " + get_type(
                a.split('.')[1]) + ' name=' + name_base64 + '\n\n'
            text += get_code_file_base64(a).decode() + '\n'
        text += '--' + boundary + '--'
    else:
        text += 'Content-Type: text/plain; charset=utf-8\n\n'
        text += message
    return text + '\n.'


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read_file(codecs.open('message/setting.ini', "r", "utf-8"))

    addresses = config.get("Settings", "Recievers").split(', ')
    theme = config.get("Settings", 'Theme')

    attachments = config.get("Settings", "Attachments").split(', ')
    if '' in attachments:
        attachments.remove('')

    boundary = create_boundary()
    message = read_message()
    while message.count('--' + boundary) != 0:
        boundary = create_boundary()
        message = read_message()

    input_lines = ['EHLO smtpclient.ru', 'AUTH LOGIN',
                   base64.b64encode(
                       'malyhyekaterina@mail.ru'.encode()).decode(),
                   base64.b64encode('katyaPROGRAM!1308'.encode()).decode(),
                   'MAIL FROM: malyhyekaterina@mail.ru']
    for recipient in addresses:
        input_lines.append(f'RCPT TO: {recipient}')
    input_lines.append('DATA')
    input_lines.append(form_message(theme, addresses, message, attachments))
    input_lines.append('QUIT')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('smtp.mail.ru', 465))
    ssl_sock = ssl.wrap_socket(sock)
    data = ssl_sock.recv(1024)
    print(data.decode())
    for i in input_lines:
        ssl_sock.send((i + '\r\n').encode())
        data = ssl_sock.recv(1024)
        print(data.decode())
    ssl_sock.close()
