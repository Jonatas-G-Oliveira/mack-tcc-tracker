import torch
import cv2
import time
import requests
from ultralytics import YOLO #<----- pip install --quiet ultralytics
#pip install torch-directml

ESP32_IP = ""

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
  quadroCentro = 70
  mover_servos(90,90)
  print('Começando')
 
  # ----- Definindo modelo
  modelo = YOLO('yolov8n.pt')

  # ----- Definições
  captura = cv2.VideoCapture("http://192.168.15.88:81/stream") #<------ Só trocar aqui para camera do ESP-32

  if not captura.isOpened():
    print('Erro ao abrir o arquivo de video')

  cv2.namedWindow('Resultado', cv2.WINDOW_NORMAL)
  cv2.namedWindow('Resultado', cv2.WINDOW_NORMAL)
  cv2.resizeWindow('Resultado', 1280, 720)
  positionX = 90
  positionY = 90
     
  quadroCentro = 90
  mover_servos(positionX,positionY)

  while True:
      ret, frame = captura.read()
      frameShow = frame.copy()

      if not ret:
        break

      altura, largura, _ = frame.shape
   
      cv2.line(frameShow, (0, int(altura / 2)), (largura, int(altura / 2)), (0, 255, 0), 2)
      cv2.line(frameShow, (int(largura / 2), 0), (int(largura / 2), altura), (0, 255, 0), 2)

      # ----- Aplicando o modelo para a classe person  
      resultados = modelo(frame, classes=[0], conf=0.6, stream =False)
      for caixas in resultados[0].boxes:
        x1, y1, x2, y2 = caixas.xyxy[0] #Quatro pontos da caixa
        conf = caixas.conf[0]
        centro_x = int(largura / 2)
        centro_y = int(altura / 2)
        centro_pessoa_horizontal = int((x1+x2)/2) + 10
        centro_pessoa_vertical = int((y1+y2)/2) + 10
        cv2.circle(frameShow, (centro_pessoa_horizontal, centro_pessoa_vertical),5,(0,255,0),-1)
        # cv2.rectangle(frameShow,(x1,y1),(x2,y2),(255,0,255),5) 
        cv2.rectangle(frameShow, (centro_x -70, centro_y-70),(centro_x + 70, centro_y + 70), (255, 0, 255), 5)

        #Movimento Eixo X
   
        if centro_pessoa_horizontal < (centro_x - quadroCentro):
            positionX += 1
            mover_servos(positionX, positionY)
        elif centro_pessoa_horizontal > (centro_x + quadroCentro):
            positionX -= 1
            mover_servos(positionX, positionY)
              
        
        #Movimento Eixo Y
        
        if centro_pessoa_vertical > (centro_y + quadroCentro):
           positionY += 1
           if positionX <= 180 and positionX >= 1:
              mover_servos(positionX, positionY)
        elif centro_pessoa_vertical < (centro_y - quadroCentro):
            positionY -= 1
            if positionX <= 180 and positionX >= 1:
               mover_servos(positionX, positionY)

      frame_anotado = resultados[0].plot()
      alpha = 0.6  # transparência — ajuste entre 0 e 1
      frame_final = cv2.addWeighted(frameShow, 1 - alpha, frame_anotado, alpha, 0)
      # cv2.imshow('Resultado', frame_anotado)
      cv2.imshow('Resultado', frame_final)
      
      # saida.write(frame_anotado)

      # ----- Encerra o programa ao apertar a tecla q
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break

  # ----- Limpa Memória
  captura.release()


main()
