import requests
import time

ESP32_IP = ""

def mover_servos(x, y):
    
    x = max(0, min(180,x))
    y = max(0, min(180, y))

    url = f'{ESP32_IP}/X{x}Y{y}'

    try:
        resposta = requests.get(url, timeout=2)
        if resposta.status_code == 200:
            print(f'Servos movidos -> X={x}, Y={y}')
        else:
            print(f"Erro {resposta.status_code} ao enviar o comando")
    except requests.exceptions.RequestException as e:
        print(f'Falha na comunicação: {e}')


def main():
    # for ang in range(0,191,30):
    #     mover_servos(ang, 180 - ang)
    #     time.sleep(2)

    mover_servos(90, 90)

    print("Encerrando")

main()
