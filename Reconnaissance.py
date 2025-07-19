import cv2
import face_recognition
import numpy as np
import pygame
import sqlite3
from datetime import datetime

# SQLite
conn = sqlite3.connect('detections.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS detection (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        date_heure TEXT
    )
''')

# Charger les signatures
data = np.load('SignaturesAll.npy', allow_pickle=True)
signatures = data[:, :-1].astype('float')
noms = data[:, -1]

# Alarme 
pygame.init()
pygame.mixer.init()
alarme = pygame.mixer.Sound('alert.wav')

# Accès 
capture = cv2.VideoCapture(0)

while True:
    reponse, image = capture.read()
    if not reponse:
        break

    image_reduite = cv2.resize(image, (0, 0), None, 0.25, 0.25)
    image_RGB = cv2.cvtColor(image_reduite, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(image_RGB)
    encodings = face_recognition.face_encodings(image_RGB, face_locations)

    for encode, loc in zip(encodings, face_locations):
        comparaison = face_recognition.compare_faces(signatures, encode)
        distances = face_recognition.face_distance(signatures, encode)
        min_index = np.argmin(distances)
        y1, x2, y2, x1 = [v * 4 for v in loc]

        if comparaison[min_index]:
            nom = noms[min_index]
            couleur = (0, 255, 0)
        else:
            nom = "Inconnu"
            couleur = (0, 0, 255)
            alarme.play()

        # Save DB
        cursor.execute("INSERT INTO detection (nom, date_heure) VALUES (?, ?)", 
                       (str(nom), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

        cv2.rectangle(image, (x1, y1), (x2, y2), couleur, 3)
        cv2.putText(image, nom, (x1 + 5, y2 + 25), cv2.FONT_HERSHEY_COMPLEX, 1, couleur, 2)

    cv2.imshow("Surveillance IA2", image)

    if cv2.waitKey(1) == ord('q'):
        break

capture.release()
conn.close()
cv2.destroyAllWindows()
