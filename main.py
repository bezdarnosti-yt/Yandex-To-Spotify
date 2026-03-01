from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QPushButton, QLineEdit, QVBoxLayout, QWidget, QApplication, QFrame

import json


class MainWindow(QMainWindow):
    WIDTH = 320
    HEIGHT = 200
    
    isYaApiWorking = False
    isSpotifyApiWorking = False
    isFirstLaunch = True
    
    def __init__(self):
        self.checkConfigFile()
        
        super().__init__()
        
        self.setWindowTitle("YaConversion")
        
        self.setFixedSize(QSize(self.WIDTH, self.HEIGHT))
        
        layout = QVBoxLayout()
        
        textYaApi = QLineEdit()
        textYaApi.setPlaceholderText("Введите токен от вашего аккаунта Яндекс.Музыка")
        layout.addWidget(textYaApi)
        
        checkYaApiButton = QPushButton("Проверить доступ к Яндекс.API")
        checkYaApiButton.clicked.connect(self.checkYaApi)
        layout.addWidget(checkYaApiButton)
        
        textSpotifyApi = QLineEdit()
        textSpotifyApi.setPlaceholderText("Введите api ключ от Spotify")
        layout.addWidget(textSpotifyApi)
        
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
        
    def checkYaApi(self):
        pass
    
    def checkSpotifyApi(self):
        pass
    
    def startConversion(self):
        pass
    
    def checkConfigFile(self):
        pass


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
    

if __name__ == "__main__":
    main()