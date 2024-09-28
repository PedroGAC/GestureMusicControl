import cv2
import mediapipe as mp
import pygame
import time

# Inicializa o mixer do pygame para tocar sons
pygame.mixer.init()

# Carregando sons das notas musicais
sounds = {
    'Do': pygame.mixer.Sound('notas_musicais/1.C_PIANO.wav'),
    'Re': pygame.mixer.Sound('notas_musicais/3.D_PIANO.wav'),
    'Mi': pygame.mixer.Sound('notas_musicais/5.E_PIANO.wav'),
    'Fa': pygame.mixer.Sound('notas_musicais/6.F_PIANO.wav'),
    'Sol': pygame.mixer.Sound('notas_musicais/8.G_PIANO.wav'),
    'La': pygame.mixer.Sound('notas_musicais/10.A_PIANO.wav'),
    'Si': pygame.mixer.Sound('notas_musicais/12.B_PIANO.wav'),
}

# Função para tocar uma nova nota e interromper a anterior
def musical_note(note):
    pygame.mixer.stop()  # Para qualquer som que estiver tocando
    if note in sounds:
        sounds[note].play()  # Toca a nova nota

video = cv2.VideoCapture(0)  # 0, pois só tenho 1 webcam

mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=2)
mpDraw = mp.solutions.drawing_utils
mpHandsStyle = mp.solutions.hands.HandLandmark

# Variáveis para controle de tempo e estado
last_total_dedos_levantados = -1
start_time = 0
current_note = None
DELAY_TIME = 0.5  # Tempo de delay em segundos

while True:
    check, image = video.read()
    image = cv2.flip(image, 1)
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(imageRGB)
    h, w, _ = image.shape

    total_dedos_levantados = 0

    if results.multi_hand_landmarks:
        for hand_index, points_hand in enumerate(results.multi_hand_landmarks):
            hand_label = results.multi_handedness[hand_index].classification[0].label

            points = []
            mpDraw.draw_landmarks(image, points_hand, mpHands.HAND_CONNECTIONS)
            for id, cord in enumerate(points_hand.landmark):
                cx, cy = int(cord.x * w), int(cord.y * h)
                cv2.putText(image, str(id), (cx, cy + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                points.append((cx, cy))

            fingers = [mpHandsStyle.INDEX_FINGER_TIP, mpHandsStyle.MIDDLE_FINGER_TIP, mpHandsStyle.RING_FINGER_TIP, mpHandsStyle.PINKY_TIP]
            dedos_levantados = 0

            if hand_label == 'Right':
                if points[mpHandsStyle.THUMB_TIP][0] < points[mpHandsStyle.THUMB_IP][0]:
                    dedos_levantados += 1
            elif hand_label == 'Left':
                if points[mpHandsStyle.THUMB_TIP][0] > points[mpHandsStyle.THUMB_IP][0]:
                    dedos_levantados += 1

            for x in fingers:
                if points[x][1] < points[x - 2][1]:
                    dedos_levantados += 1

            total_dedos_levantados += dedos_levantados

            if hand_label == 'Right':
                cv2.putText(image, f"Mao direita: {dedos_levantados} dedos levantados", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            elif hand_label == 'Left':
                cv2.putText(image, f"Mao esquerda: {dedos_levantados} dedos levantados", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Lógica para tocar a nota com delay
        current_time = time.time()
        
        if total_dedos_levantados != last_total_dedos_levantados:
            start_time = current_time
            last_total_dedos_levantados = total_dedos_levantados
            current_note = None
        elif current_time - start_time >= DELAY_TIME and current_note is None:
            if total_dedos_levantados == 1:
                current_note = 'Do'
            elif total_dedos_levantados == 2:
                current_note = 'Re'
            elif total_dedos_levantados == 3:
                current_note = 'Mi'
            elif total_dedos_levantados == 4:
                current_note = 'Fa'
            elif total_dedos_levantados == 5:
                current_note = 'Sol'
            elif total_dedos_levantados == 6:
                current_note = 'La'
            elif total_dedos_levantados == 7:
                current_note = 'Si'
            elif total_dedos_levantados == 0:
                pygame.mixer.stop()
                current_note = 'Stop'
            
            if current_note:
                if current_note != 'Stop':
                    musical_note(current_note)
                print(f"Tocando nota: {current_note}")

        # Exibe o tempo restante para tocar a nota
        if current_note is None and total_dedos_levantados > 0:
            remaining_time = max(0, DELAY_TIME - (current_time - start_time))
            cv2.putText(image, f"Tempo para tocar: {remaining_time:.1f}s", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        if current_note and current_note != 'Stop':
            cv2.putText(image, f"Nota: {current_note}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        print(f"Total de dedos levantados: {total_dedos_levantados}")

    cv2.imshow("Imagem", image)
    cv2.waitKey(1)