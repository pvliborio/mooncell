import socket
import config
import errno
import os
import signal
import platform
import time

SUPPORTED_FORMATS = ["html", "htm", "js", "jpeg", "jpg", "png", "gif"]

def mooncell_SERAPH(signum, frame):
    """ 'Handler' de signal.SIGCHLD para esperar todos processos filhos terminarem, 
    assim não é possível que filhos cujo processo pai não recebeu
    status terminado ainda acumulem desnecessáriamente """
    
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG) 
        except OSError:
            return
        
        if pid == 0:
            return

def mooncell_dir_file(requested_resource):
    """ Separa a path recebida, entre conjunto de diretórios e file final, retornando ambos"""   
    last_index = requested_resource.rfind("/")
    if (last_index == 0 and len(requested_resource) > 1):
        return "", requested_resource[last_index+1:]
    return requested_resource[0:last_index], requested_resource[last_index+1:]

def mooncell_search_page(res_dir, res_file):
    """ Realiza a busca em ordem do path requisitado, retorna o Path completo do arquivo caso encontre, ou None caso contrário. """   
    for root, dirs, files in os.walk(config.ROOT_DIR + res_dir):
        for name in files:
            if name == res_file:
                return config.ROOT_DIR + res_dir + '/' + res_file
    return None

def mooncell_content_type(file_extension):
    """ 'Getter' de extensões para construir as respostas do server devidamente formatadas, 
    recebe uma extensão e retorna o texto formatado para a resposta do GET apropriada"""
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
    """ Cria as respostas devidamente formatadas para as requisições possíveis,
    recebe um path e retorna a devida resposta para o request"""
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
    """ Lida com as requisições definindo se é preciso procurar o arquivo ou não, recebe a conexão do socket
    e realiza as respostas para cada caso"""
    request = mooncell_con.recv(1024)
    print(request.decode().strip().split())
    if(len(request.decode().strip().split()) == 0): #Se o request for vazio return
        return
    requested_resource = request.decode().strip().split()[1] #Indentifica a o recurso que tentou se acessado 
    result = ""
    if "." not in requested_resource: # Se não houver "." buscar arquivo na lista de Default Files ?***
        for file in config.DEFAULT_FILES:
            result = mooncell_search_page('', file)
            if not result == None:
                break
    else: # Se houver "." ou seja, tiver uma extensão, procurar o diretório, ou arquivo requisitado
        res_dir, res_file = mooncell_dir_file(requested_resource)
        result = mooncell_search_page(res_dir, res_file)

    response = ""

    if result == None: #Cria a resposta com base no resultado das buscas pelo que foi requisitado
        response = mooncell_create_response(None)
    else:
        response = mooncell_create_response(result)

    mooncell_con.sendall(response)
    time.sleep(30) #Delay usado para testar a conexão de mais de um cliente simultâneamente

def mooncell_check_config():
    """ Verifica a confiabilidade dos dados presentes em config.py"""
    if config.ROOT_DIR == None or config.ROOT_DIR == '':
        print("Diretório definido como ROOT é Nulo/Vazio, verifique o arquivo config.py\n")
        return False
    if not os.path.exists(config.ROOT_DIR):
        return False
        print("Diretório definido como ROOT não existe, verifique o arquivo config.py\n")
    if os.getcwd() != config.ROOT_DIR:
        print("Diretório definido como ROOT diferente do local do arquivo atual, verifique o arquivo config.py\n")
        return False
    if config.DEFAULT_FILES.__len__() == 0:
        print("Lista de Default Files vazia, verifique o arquivo config.py\n")
        return False
    if config.ERROR_PAGE == None or config.ERROR_PAGE == '':
        print("Página de Error definida é Nula/Vazia, verifique o arquivo config.py\n")
        return False
    if not os.path.exists(config.ERROR_PAGE):
        print("Página de Error não existe, verifique o arquivo config.py\n")
        return False
    if config.MESSAGE_NOT_SUPPORTED == None or config.MESSAGE_NOT_SUPPORTED == '':
        print("Mensagem de tratamento para extensões não suportadas pelo servidor é Nula/Vazia, verifique o arquivo config.py\n")
        return False
    if config.SERVER_PORT == None:
        print("Porta de acesso Nula, verifique o arquivo config.py\n")
    return True


def main():
    """Setup Inicial do server com fork para multiplos clientes"""

    if(not mooncell_check_config()):
        return

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