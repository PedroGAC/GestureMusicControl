import cv2
import mediapipe as mp

video = cv2.VideoCapture(0) #0, pois só tenho 1 webcam

mpHands = mp.solutions.hands #Variável responsável pelas configurações do mediapipe
hands = mpHands.Hands(max_num_hands=2) #max_num_hands=2, pois quero detectar 2 mão (responsável pela detecção)
mpDraw = mp.solutions.drawing_utils #Variável responsável por desenhar as linhas e pontos
mpHandsStyle = mp.solutions.hands.HandLandmark  

while True:
    check, image = video.read() #Captura a imagem da webcam
    image = cv2.flip(image, 1)
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) #Converte a imagem para RGB, pois o vídeo é coletado em BGR
    results = hands.process(imageRGB) #Processa a imagem e retorna os resultados
    handsPoints = results.multi_hand_landmarks #Pega os pontos das mãos detectadas
    h, w, _ = image.shape #Pega a altura e largura da imagem

    if results.multi_hand_landmarks:  # Se houver mãos detectadas
        for hand_index, points_hand in enumerate(results.multi_hand_landmarks):
            # Obtendo a mão esquerda ou direita
            hand_label = results.multi_handedness[hand_index].classification[0].label  # 'Left' ou 'Right'

            points = []  # Lista para armazenar os pontos das mãos detectadas
            mpDraw.draw_landmarks(image, points_hand, mpHands.HAND_CONNECTIONS)
            for id, cord in enumerate(points_hand.landmark):
                cx, cy = int(cord.x * w), int(cord.y * h)  # Converte as coordenadas para pixels
                cv2.putText(image, str(id), (cx, cy + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)  # Escreve o número do ponto na imagem
                points.append((cx, cy))  # Adiciona o ponto na lista de pontos

            # Pontos das pontas dos dedos (índices)
            fingers = [mpHandsStyle.INDEX_FINGER_TIP, mpHandsStyle.MIDDLE_FINGER_TIP, mpHandsStyle.RING_FINGER_TIP, mpHandsStyle.PINKY_TIP]
            contador = 0  # Armazena o número de dedos levantados

            # Verificação para o polegar com base na mão esquerda ou direita
            if hand_label == 'Right':  # Se for a mão direita
                if points[mpHandsStyle.THUMB_TIP][0] < points[mpHandsStyle.THUMB_IP][0]:  # Verifica se o polegar está à esquerda do ponto IP
                    contador += 1
            elif hand_label == 'Left':  # Se for a mão esquerda
                if points[mpHandsStyle.THUMB_TIP][0] > points[mpHandsStyle.THUMB_IP][0]:  # Verifica se o polegar está à direita do ponto IP
                    contador += 1

            # Verificação para os outros dedos (pontas dos dedos acima das articulações médias)https://open.spotify.com/playlist/4jQ39AJBagEHafGaN4LDX4
            for x in fingers:
                if points[x][1] < points[x - 2][1]:  # Se a ponta do dedo estiver acima do ponto médio
                    contador += 1

            if hand_label == 'Right':
                cv2.putText(image, f"Mao direita: {contador} dedos levantados", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            elif hand_label == 'Left':
                cv2.putText(image, f"Mao esquerda: {contador} dedos levantados", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            print(f"Mão {hand_label}: {contador} dedos levantados")

    cv2.imshow("Imagem", image) #Mostra a imagem capturada
    cv2.waitKey(1) #Espera 1ms para capturar a próxima imagem