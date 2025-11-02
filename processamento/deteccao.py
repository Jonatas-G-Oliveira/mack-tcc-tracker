import torch
import cv2
import time
import requests
from ultralytics import YOLO #<----- pip install --quiet ultralytics
#pip install torch-directml

ESP32_IP = "http://192.168.15.88:8080"

def mover_servos(x, y):
    
    x = max(0, min(180,x))
    y = max(0, min(180,y))

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
  mover_servos(90,90)
  print('Começando')
  print("CUDA disponível:", torch.cuda.is_available())
  print("Versão do PyTorch:", torch.__version__)
  # ----- Definindo modelo
  modelo = YOLO('yolov8n.pt')
  if(torch.cuda.is_available()):
    print("Nome da GPU:", torch.cuda.get_device_name(0))
    modelo.to('cuda')

  # ----- Definições
  captura = cv2.VideoCapture("http://192.168.15.88:81/stream") #<------ Só trocar aqui para camera do ESP-32
  saida = './result.mp4'

  # ----- Escrita do arquivo
  fps = captura.get(cv2.CAP_PROP_FPS)
  largura = int(captura.get(cv2.CAP_PROP_FRAME_WIDTH))
  altura = int(captura.get(cv2.CAP_PROP_FRAME_HEIGHT))
  saida = cv2.VideoWriter(saida, cv2.VideoWriter_fourcc(*'mp4v'), fps, (largura, altura))

  print('-> Abrindo video')
  if not captura.isOpened():
    print('Erro ao abrir o arquivo de video')

  while True:
      ret, frame = captura.read()
      if not ret:
        break

      altura, largura = frame.shape[:2]
      centro_x, centro_y = largura/2, altura/2


      print(f'Tela: {centro_y} - {centro_x}')
   
      # ----- Aplicando o modelo para a classe person  
      resultados = modelo(frame, classes=[0], conf=0.6, stream =False)
      for caixas in resultados[0].boxes:
        x1, y1, x2, y2 = caixas.xyxy[0] #Quatro pontos da caixa
        conf = caixas.conf[0]
      
        #centro da pessoa
        x_pessoa = (x1 + x2)/2
        y_pessoa = (y1 + y2)/2

        #Distancia dos pixels até o centro da tela
        dx = centro_x - x_pessoa
        dy = y_pessoa - centro_y

        servo_x = 90 + dx * 0.2  # 90 é centro servo, fator ajusta pixels -> graus
        servo_y = 90 + dy * 0.2
        mover_servos(int(servo_x), int(servo_y))
        print(f'Ponto central da pessoa X: ({x_pessoa:.1f}, Y: ({y_pessoa:.1f})')
        print(f'Deslocamento do centro da tela X: ({dx:.1f}, Y:({dy:.1f})')
        time.sleep(0.1)
      frame_anotado = resultados[0].plot()
      cv2.imshow('Resultado', frame_anotado)
      # saida.write(frame_anotado)

      # ----- Encerra o programa ao apertar a tecla q
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break

  # ----- Limpa Memória
  captura.release()
  saida.release()


main()