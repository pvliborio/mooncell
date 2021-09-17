import socket
import config
import errno
import os
import signal
import platform

SUPPORTED_FORMATS = ["html", "htm", "js", "jpeg", "jpg", "png", "gif"]

def mooncell_SERAPH(signum, frame):
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
        except OSError:
            return
        
        if pid == 0:
            return

def mooncell_dir_file(requested_resource):
    last_index = requested_resource.rfind("/")
    if (last_index == 0 and len(requested_resource) > 1):
        return "", requested_resource[last_index+1:]
    return requested_resource[0:last_index], requested_resource[last_index+1:]

def mooncell_search_page(res_dir, res_file):
    for root, dirs, files in os.walk(config.ROOT_DIR + res_dir):
        for name in files:
            if name == res_file:
                return config.ROOT_DIR + res_dir + '/' + res_file
    return None

def mooncell_content_type(file_extension):
    if(file_extension == "html" or file_extension == "htm"):
        return "text/html"
    elif(file_extension == "js"):
        return "text/javascript"
    elif(file_extension == "jpeg" or file_extension == "jpg"):
        return "image/jpeg"
    elif(file_extension == "png"):
        return "image/png"
    elif(file_extension == "gif"):
        return "image/gif"

def mooncell_create_response(file_path):
    response = "HTTP/1.1 "
    if file_path == None:
        response += "404 NOT FOUND\n"
        response += "Content-Type: text/html; charset=utf-8\n"
        response += "Content-Length: " + str(os.path.getsize(config.ROOT_DIR + '/' + config.ERROR_PAGE)) + "\n\n"
        file = open(config.ROOT_DIR + '/' + config.ERROR_PAGE, "rb")
        response = response.encode()
        response += file.read()
        file.close()
        return response
    
    _, res_file = mooncell_dir_file(file_path)
    file_type = res_file[res_file.rfind(".")+1:].lower()
    if file_type in SUPPORTED_FORMATS:
        response += "200 OK\n"
        response += "Content-Type: " + mooncell_content_type(file_type) + "; charset=utf-8\n"
        response += "Content-Length: " + str(os.path.getsize(file_path)) + "\n\n"
        file = open(file_path, "rb")
        response = response.encode()
        response += file.read()
        file.close()
    else:
        response += "415 Unsupported Media Type\n"
        response += "Content-Type: text/html; charset=utf-8\n\n"
        response += config.MESSAGE_NOT_SUPPORTED
        response = response.encode()
    return response

def gacha_handle_request(mooncell_con):
    request = mooncell_con.recv(1024)
    print(request.decode().strip().split())
    if(len(request.decode().strip().split()) == 0):
        return
    requested_resource = request.decode().strip().split()[1]
    result = ""
    if "." not in requested_resource:
        for file in config.DEFAULT_FILES:
            result = mooncell_search_page('', file)
            if not result == None:
                break
    else:
        res_dir, res_file = mooncell_dir_file(requested_resource)
        result = mooncell_search_page(res_dir, res_file)

    response = ""

    if result == None:
        response = mooncell_create_response(None)
    else:
        response = mooncell_create_response(result)

    mooncell_con.sendall(response)

def main():
    mooncell_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mooncell_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mooncell_socket.bind(('', config.SERVER_PORT))
    mooncell_socket.listen(1024)
    print("Servidor iniciado na porta %d"%(config.SERVER_PORT))

    signal.signal(signal.SIGCHLD, mooncell_SERAPH)

    while True:
        try:
            mooncell_con, mooncell_client = mooncell_socket.accept()
        except IOError as error:
            code, message = error.args
            if code == errno.EINTR:
                continue
            else:
                raise
        
        pid = os.fork()
        if (pid == 0):
            mooncell_socket.close()
            gacha_handle_request(mooncell_con)
            mooncell_con.close()
            os._exit(0)
        else:
            mooncell_con.close()

if __name__ == "__main__":
    main()