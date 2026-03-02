from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QPushButton, QLineEdit, QVBoxLayout, QWidget, QApplication, QFrame, QDialog, QLabel, QTextEdit, QProgressBar, QHBoxLayout
from pathlib import Path
from yandex_music import Client
from yandex_music.exceptions import UnauthorizedError

import json
import webbrowser


class MainWindow(QMainWindow):
    WIDTH = 320
    HEIGHT = 260
    
    is_ya_api_working = False
    is_spotify_api_working = False
    
    file_path = Path("env.json")
    
    env = {
        "ya_secret" : "",
        "spotify_username" : "",
        "spotify_password" : ""
    }
    empty_data = {}
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("YaConversion")
        
        self.setFixedSize(QSize(self.WIDTH, self.HEIGHT))
        
        layout = QVBoxLayout()
        
        # Яндекс - секция
        self.text_ya_api = QLineEdit()
        self.text_ya_api.setPlaceholderText("Введите токен от вашего аккаунта Яндекс.Музыка")
        layout.addWidget(self.text_ya_api)
        
        check_ya_api_btn = QPushButton("Проверить доступ к Яндекс.API")
        check_ya_api_btn.clicked.connect(self.checkYaApi)
        layout.addWidget(check_ya_api_btn)
        
        info_ya_api_btn = QPushButton("Как получить токен Яндекс?")
        info_ya_api_btn.clicked.connect(self.get_info_ya_api)
        layout.addWidget(info_ya_api_btn)
        
        # Спотифай - секция
        self.text_spotify_login = QLineEdit()
        self.text_spotify_login.setPlaceholderText("Введите логин от Spotify")
        layout.addWidget(self.text_spotify_login)
        
        self.text_spotify_pass = QLineEdit()
        self.text_spotify_pass.setPlaceholderText("Введите пароль от Spotify")
        layout.addWidget(self.text_spotify_pass)
        
        check_spotify_btn = QPushButton("Проверить доступ к Spotify.API")
        check_spotify_btn.clicked.connect(self.check_spotify_api)
        layout.addWidget(check_spotify_btn)
        
        # info_spotify_api_btn = QPushButton("Как получить API ключ Spotify?")
        # info_spotify_api_btn.clicked.connect(self.get_info_spotify_api)
        # layout.addWidget(info_spotify_api_btn)
        
        # Разделительная линия
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # Конвертация
        self.start_conversion_btn = QPushButton("Начало конвертации")
        self.start_conversion_btn.clicked.connect(self.start_conversion)
        self.start_conversion_btn.setEnabled(self.is_api_good())
        layout.addWidget(self.start_conversion_btn)
        
        # Статус API
        api_layout = QHBoxLayout()
        
        self.ya_api_work_status_label = QLabel("Яндекс API не проверено")
        api_layout.addWidget(self.ya_api_work_status_label)
        
        self.spotify_api_work_status_label = QLabel("Spotify API не проверено")
        api_layout.addWidget(self.spotify_api_work_status_label)
        
        # Обьединение двух QVBoxLayout, QHBoxLayout
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(api_layout)
        
        # Создание разметки
        widget = QWidget()
        widget.setLayout(main_layout)
        
        self.setCentralWidget(widget)
        
        self.check_config_file()
        
    def checkYaApi(self):
        with open("env.json", "r+") as f:
            data = json.load(f)
        
        data['ya_secret'] = self.text_ya_api.text()
        
        with open("env.json", "w") as f:
            json.dump(data, f, indent=4)
            
        try:
            self.ya_client = Client(self.text_ya_api.text()).init()
        except UnauthorizedError:
            dlg = QDialog(self)
            dlg.setWindowTitle("Проверка Яндекс")
            layout = QVBoxLayout()
            message = QLabel("Токен невалидный!")
            layout.addWidget(message)
            dlg.setLayout(layout)
            dlg.exec()
            return
        
        self.is_ya_api_working = True
        self.start_conversion_btn.setEnabled(self.is_api_good())
        self.ya_api_work_status_label.setText("Яндекс API готово")
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Проверка Яндекс")
        layout = QVBoxLayout()
        message = QLabel("Токен правильный!")
        layout.addWidget(message)
        dlg.setLayout(layout)
        dlg.exec()
        
    def check_spotify_api(self):
        with open("env.json", "r+") as f:
            data = json.load(f)
        
        data['spotify_username'] = self.text_spotify_login.text()
        data['spotify_password'] = self.text_spotify_pass.text()
        
        with open("env.json", "w") as f:
            json.dump(data, f, indent=4)
            
        self.is_spotify_api_working = True
        self.start_conversion_btn.setEnabled(self.is_api_good())
        self.spotify_api_work_status_label.setText("Spotify API готово")
    
    def start_conversion(self):
        self.is_getting_tracks = True
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Экспорт")
        layout = QVBoxLayout()
        dlg.setLayout(layout)
        
        log_text = QTextEdit()
        log_text.setReadOnly(True)
        layout.addWidget(log_text)
        
        progress_bar = QProgressBar()
        layout.addWidget(progress_bar)
        
        stop_export_btn = QPushButton("Стоп")
        stop_export_btn.clicked.connect(self.stop_getting)
        layout.addWidget(stop_export_btn)
        
        dlg.show()
        
        tracks_json = self.ya_client.users_likes_tracks()
        total_tracks = len(tracks_json)
        self.ya_songs = [[]]
        
        for i, track in enumerate(tracks_json):
            if (self.is_getting_tracks):
                info = self.ya_client.tracks(track["id"])[0]
                song_title = info.title
                artist_name = info.artists[0].name
                
                message = f"{i+1}/{total_tracks}: {artist_name} - {song_title}"
                
                log_text.append(message)
                
                item = [song_title, artist_name]
                self.ya_songs.append(item)
            
            progress = int((i + 1) / total_tracks * 100)
            progress_bar.setValue(progress)
            
            QApplication.processEvents()
            
        stop_export_btn.setText("Экспорт в Spotify")
        stop_export_btn.clicked.connect(self.try_export)
        
        log_text.append("Экспорт завершен!")
        QApplication.processEvents()
        
    def check_config_file(self):
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
                self.text_ya_api.setText(data["ya_secret"])
                self.text_spotify_login.setText(data["spotify_username"])
                self.text_spotify_pass.setText(data["spotify_password"])
                
    def get_info_ya_api(self):
        webbrowser.open("https://github.com/bezdarnosti-yt/Yandex-To-Spotify/blob/master/YANDEX.md")
    
    @DeprecationWarning
    def get_info_spotify_api(self):
        webbrowser.open("https://github.com/bezdarnosti-yt/Yandex-To-Spotify/blob/master/SPOTIFY.md")
        
    def stop_getting(self):
        self.is_getting_tracks = False
    
    def try_export(self):
        pass
    
    def is_api_good(self) -> bool:
        return self.is_ya_api_working and self.is_spotify_api_working
    
        
def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
    

if __name__ == "__main__":
    main()