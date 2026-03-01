from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QPushButton, QLineEdit, QVBoxLayout, QWidget, QApplication, QFrame

import json

from pathlib import Path


class MainWindow(QMainWindow):
    WIDTH = 320
    HEIGHT = 200
    
    isYaApiWorking = False
    isSpotifyApiWorking = False
    
    file_path = Path("env.json")
    
    env = {
        "ya_secret" : "",
        "spotify_secret" : ""
    }
    empty_data = {}
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("YaConversion")
        
        self.setFixedSize(QSize(self.WIDTH, self.HEIGHT))
        
        layout = QVBoxLayout()
        
        self.textYaApi = QLineEdit()
        self.textYaApi.setPlaceholderText("Введите токен от вашего аккаунта Яндекс.Музыка")
        layout.addWidget(self.textYaApi)
        
        checkYaApiButton = QPushButton("Проверить доступ к Яндекс.API")
        checkYaApiButton.clicked.connect(self.checkYaApi)
        layout.addWidget(checkYaApiButton)
        
        self.textSpotifyApi = QLineEdit()
        self.textSpotifyApi.setPlaceholderText("Введите api ключ от Spotify")
        layout.addWidget(self.textSpotifyApi)
        
        checkSpotifyApiButton = QPushButton("Проверить доступ к Spotify.API")
        checkSpotifyApiButton.clicked.connect(self.checkSpotifyApi)
        layout.addWidget(checkSpotifyApiButton)
        
        # Разделительная линия
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        startConversionButton = QPushButton("Начало конвертации")
        startConversionButton.clicked.connect(self.startConversion)
        layout.addWidget(startConversionButton)
        
        widget = QWidget()
        widget.setLayout(layout)
        
        self.setCentralWidget(widget)
        
        self.checkConfigFile()
        
    def checkYaApi(self):
        with open("env.json", "r+") as f:
            data = json.load(f)
        
        data['ya_secret'] = self.textYaApi.text()
        
        with open("env.json", "w") as f:
            json.dump(data, f, indent=4)
    
    def checkSpotifyApi(self):
        with open("env.json", "r+") as f:
            data = json.load(f)
        
        data['spotify_secret'] = self.textSpotifyApi.text()
        
        with open("env.json", "w") as f:
            json.dump(data, f, indent=4)
    
    def startConversion(self):
        pass
    
    def checkConfigFile(self):
        # Проверка файла на существовании и в случае чего его создание по шаблону
        if not self.file_path.is_file():
            try:
                with open("env.json", "w") as json_file:
                    json.dump(self.env, json_file, indent=4)
            except IOError as e:
                print(f"Error creating file: {e}")
        else:
            with open("env.json", "r") as f:
                data = json.load(f)
                self.textYaApi.setText(data["ya_secret"])
                self.textSpotifyApi.setText(data["spotify_secret"])
        
        
def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
    

if __name__ == "__main__":
    main()