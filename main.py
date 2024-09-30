import cv2
import mediapipe as mp
import pygame
import time

# Inicializa o mixer do pygame para tocar sons
pygame.mixer.init()

# Carregando sons das notas musicais
sounds_notes = {
    'Do': pygame.mixer.Sound('notas_musicais/1.C_PIANO.wav'),
    'Re': pygame.mixer.Sound('notas_musicais/3.D_PIANO.wav'),
    'Mi': pygame.mixer.Sound('notas_musicais/5.E_PIANO.wav'),
    'Fa': pygame.mixer.Sound('notas_musicais/6.F_PIANO.wav'),
    'Sol': pygame.mixer.Sound('notas_musicais/8.G_PIANO.wav'),
    'La': pygame.mixer.Sound('notas_musicais/10.A_PIANO.wav'),
    'Si': pygame.mixer.Sound('notas_musicais/12.B_PIANO.wav'),
}

sounds_chords = {
    'C#': pygame.mixer.Sound('notas_musicais/2.C#_PIANO.wav'),
    'D#': pygame.mixer.Sound('notas_musicais/4.D#_PIANO.wav'),
    'F#': pygame.mixer.Sound('notas_musicais/7.F#_PIANO.wav'),
    'G#': pygame.mixer.Sound('notas_musicais/9.G#_PIANO.wav'),
    'A#': pygame.mixer.Sound('notas_musicais/11.A#_PIANO.wav'),
}

# Função para tocar uma nova nota e interromper a anterior
def musical_note(note):
    pygame.mixer.stop()  # Para qualquer som que estiver tocando
    if note in sounds_notes:
        sounds_notes[note].play()  # Toca a nova nota

# Função para tocar um acorde
def play_chord(chord):
    pygame.mixer.stop()  # Para qualquer som que estiver tocando
    if chord in sounds_chords:
        sounds_chords[chord].play()  # Toca o acorde

video = cv2.VideoCapture(0)  # 0, pois só tenho 1 webcam

mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=2)
mpDraw = mp.solutions.drawing_utils
mpHandsStyle = mp.solutions.hands.HandLandmark

# Variáveis para controle de tempo e estado
last_combination = None
start_time = 0
current_note_or_chord = None
DELAY_TIME = 0.5  # Tempo de delay em segundos

while True:
    check, image = video.read()
    image = cv2.flip(image, 1)
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(imageRGB)
    h, w, _ = image.shape

    # Inicializar variáveis para dedos levantados em cada mão
    dedos_direita = 0
    dedos_esquerda = 0

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

            # Lógica para o polegar
            if hand_label == 'Right':
                if points[mpHandsStyle.THUMB_TIP][0] < points[mpHandsStyle.THUMB_IP][0]:
                    dedos_levantados += 1
            elif hand_label == 'Left':
                if points[mpHandsStyle.THUMB_TIP][0] > points[mpHandsStyle.THUMB_IP][0]:
                    dedos_levantados += 1

            # Lógica para os outros dedos
            for x in fingers:
                if points[x][1] < points[x - 2][1]:
                    dedos_levantados += 1

            # Atribuir o número de dedos levantados à mão correspondente
            if hand_label == 'Right':
                dedos_direita = dedos_levantados
                cv2.putText(image, f"Mao direita: {dedos_direita} dedos levantados", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            elif hand_label == 'Left':
                dedos_esquerda = dedos_levantados
                cv2.putText(image, f"Mao esquerda: {dedos_esquerda} dedos levantados", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Lógica para tocar a nota ou acorde com delay
        current_time = time.time()
        combination = (dedos_esquerda, dedos_direita)

        if combination != last_combination:
            start_time = current_time
            last_combination = combination
            current_note_or_chord = None
        elif current_time - start_time >= DELAY_TIME and current_note_or_chord is None:
            chord_map = {
                (1, 1): 'C#',
                (1, 2): 'D#',
                (2, 1): 'F#',
                (2, 2): 'G#',
                (2, 3): 'A#',
            }

            chord = chord_map.get(combination)
            if chord:
                current_note_or_chord = chord
                play_chord(chord)
            else:
                total_dedos_levantados = dedos_esquerda + dedos_direita
                note = None
                if total_dedos_levantados == 1:
                    note = 'Do'
                elif total_dedos_levantados == 2:
                    note = 'Re'
                elif total_dedos_levantados == 3:
                    note = 'Mi'
                elif total_dedos_levantados == 4:
                    note = 'Fa'
                elif total_dedos_levantados == 5:
                    note = 'Sol'
                elif total_dedos_levantados == 6:
                    note = 'La'
                elif total_dedos_levantados == 7:
                    note = 'Si'
                elif total_dedos_levantados == 0:
                    pygame.mixer.stop()
                    current_note_or_chord = 'Stop'

                if note:
                    current_note_or_chord = note
                    musical_note(note)
                    print(f"Tocando nota: {note}")

        # Exibe o tempo restante para tocar a nota ou acorde
        if current_note_or_chord is None and (dedos_esquerda > 0 or dedos_direita > 0):
            remaining_time = max(0, DELAY_TIME - (current_time - start_time))
            cv2.putText(image, f"Tempo para tocar: {remaining_time:.1f}s", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        if current_note_or_chord and current_note_or_chord != 'Stop':
            cv2.putText(image, f"Tocando: {current_note_or_chord}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        print(f"Dedos esquerda: {dedos_esquerda}, Dedos direita: {dedos_direita}")

    cv2.imshow("Imagem", image)
    cv2.waitKey(1)
