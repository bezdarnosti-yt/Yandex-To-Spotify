from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QPushButton, QLineEdit, QVBoxLayout, QWidget, QApplication, QFrame, QDialog, QLabel, QTextEdit, QProgressBar
from pathlib import Path
from yandex_music import Client
from yandex_music.exceptions import UnauthorizedError

import json
import webbrowser


class MainWindow(QMainWindow):
    WIDTH = 320
    HEIGHT = 300
    
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
        
        # Яндекс - секция
        self.textYaApi = QLineEdit()
        self.textYaApi.setPlaceholderText("Введите токен от вашего аккаунта Яндекс.Музыка")
        layout.addWidget(self.textYaApi)
        
        checkYaApiButton = QPushButton("Проверить доступ к Яндекс.API")
        checkYaApiButton.clicked.connect(self.checkYaApi)
        layout.addWidget(checkYaApiButton)
        
        infoYaApiButton = QPushButton("Как получить токен Яндекс?")
        infoYaApiButton.clicked.connect(self.getInfoYaApi)
        layout.addWidget(infoYaApiButton)
        
        # Спотифай - секция
        self.textSpotifyApi = QLineEdit()
        self.textSpotifyApi.setPlaceholderText("Введите api ключ от Spotify")
        layout.addWidget(self.textSpotifyApi)
        
        checkSpotifyApiButton = QPushButton("Проверить доступ к Spotify.API")
        checkSpotifyApiButton.clicked.connect(self.checkSpotifyApi)
        layout.addWidget(checkSpotifyApiButton)
        
        infoSpotifyApiButton = QPushButton("Как получить API ключ Spotify?")
        infoSpotifyApiButton.clicked.connect(self.getInfoSpotifyApi)
        layout.addWidget(infoSpotifyApiButton)
        
        # Разделительная линия
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # Конвертация
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
            
        try:
            self.yaClient = Client(self.textYaApi.text()).init()
        except UnauthorizedError:
            dlg = QDialog(self)
            dlg.setWindowTitle("Проверка Яндекс")
            layout = QVBoxLayout()
            message = QLabel("Токен невалидный!")
            layout.addWidget(message)
            dlg.setLayout(layout)
            dlg.exec()
            return
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Проверка Яндекс")
        layout = QVBoxLayout()
        message = QLabel("Токен правильный!")
        layout.addWidget(message)
        dlg.setLayout(layout)
        dlg.exec()
        
    def checkSpotifyApi(self):
        with open("env.json", "r+") as f:
            data = json.load(f)
        
        data['spotify_secret'] = self.textSpotifyApi.text()
        
        with open("env.json", "w") as f:
            json.dump(data, f, indent=4)
    
    def startConversion(self):
        self.isGettingTracks = True
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Экспорт")
        layout = QVBoxLayout()
        dlg.setLayout(layout)
        
        log_text = QTextEdit()
        log_text.setReadOnly(True)
        layout.addWidget(log_text)
        
        progress_bar = QProgressBar()
        layout.addWidget(progress_bar)
        
        stopExportButton = QPushButton("Стоп")
        stopExportButton.clicked.connect(self.stopGetting)
        layout.addWidget(stopExportButton)
        
        dlg.show()
        
        tracks_json = self.yaClient.users_likes_tracks()
        total_tracks = len(tracks_json)
        self.songs = [[]]
        
        for i, track in enumerate(tracks_json):
            if (self.isGettingTracks):
                info = self.yaClient.tracks(track["id"])[0]
                songTitle = info.title
                artistName = info.artists[0].name
                
                message = f"{i+1}/{total_tracks}: {artistName} - {songTitle}"
                
                log_text.append(message)
                
                item = [songTitle, artistName]
                self.songs.append(item)
            
            progress = int((i + 1) / total_tracks * 100)
            progress_bar.setValue(progress)
            
            QApplication.processEvents()
            
        stopExportButton.setText("Экспорт в Spotify")
        stopExportButton.clicked.connect(self.tryExport)
        
        log_text.append("Экспорт завершен!")
        QApplication.processEvents()
        
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
                
    def getInfoYaApi(self):
        webbrowser.open("https://github.com/bezdarnosti-yt/Yandex-To-Spotify/blob/master/YANDEX.md")
    
    def getInfoSpotifyApi(self):
        webbrowser.open("https://github.com/bezdarnosti-yt/Yandex-To-Spotify/blob/master/SPOTIFY.md")
        
    def stopGetting(self):
        self.isGettingTracks = False
    
    def tryExport(self):
        pass
        
def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
    

if __name__ == "__main__":
    main()