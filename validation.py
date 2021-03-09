import socket


def port_validation(port):
    """Проверка порта на корректность"""
    try:
        if port == "":
            return False
        else:
            if 1024 <= int(port) <= 65535:
                pass
            else:
                return False
            return True
    except ValueError:
        return False


def ip_validation(ip):
    """Проверка ip-адреса на корректность"""
    if ip == "":
        return False
    else:
        try:
            octets = ip.split(".", 4)
            if len(octets) == 4:
                for octet in octets:
                    octet = int(octet)
                    if 0 <= octet <= 255:
                        pass
                    else:
                        return False
            else:
                return False
        except ValueError:
            return False
        return True
