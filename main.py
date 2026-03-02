from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QPushButton, QLineEdit, QVBoxLayout, QWidget, QApplication, QFrame, QDialog, QLabel, QTextEdit, QProgressBar, QHBoxLayout
from pathlib import Path
from yandex_music import Client
from yandex_music.exceptions import UnauthorizedError
from spotapi import *

import json
import webbrowser


class MainWindow(QMainWindow):
    WIDTH = 320
    HEIGHT = 330
    
    is_ya_api_working = False
    is_spotify_api_working = False
    
    file_path = Path("env.json")
    
    env = {
        "ya_secret" : "",
        "spotify_username" : "",
        "spotify_dc" : "",
        "spotify_key" : ""
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
        check_ya_api_btn.clicked.connect(self.check_ya_api)
        layout.addWidget(check_ya_api_btn)
        
        info_ya_api_btn = QPushButton("Как получить токен Яндекс?")
        info_ya_api_btn.clicked.connect(self.get_info_ya_api)
        layout.addWidget(info_ya_api_btn)
        
        # Разделительная линия
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line1)
        
        # Спотифай - секция
        self.text_spotify_login = QLineEdit()
        self.text_spotify_login.setPlaceholderText("Введите e-mail от Spotify")
        layout.addWidget(self.text_spotify_login)
        
        self.text_spotify_dc = QLineEdit()
        self.text_spotify_dc.setPlaceholderText("Введите sp_dc от Spotify")
        layout.addWidget(self.text_spotify_dc)
        
        self.text_spotify_key = QLineEdit()
        self.text_spotify_key.setPlaceholderText("Введите sp_key от Spotify")
        layout.addWidget(self.text_spotify_key)
        
        check_spotify_btn = QPushButton("Проверить доступ к Spotify.API")
        check_spotify_btn.clicked.connect(self.check_spotify_api)
        layout.addWidget(check_spotify_btn)
        
        info_spotify_api_btn = QPushButton("Как получить cookie от Spotify?")
        info_spotify_api_btn.clicked.connect(self.get_info_spotify_api)
        layout.addWidget(info_spotify_api_btn)
        
        # Разделительная линия
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line2)
        
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
        
    def check_ya_api(self):
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
        
        tracks_json = self.ya_client.users_likes_tracks()
        self.ya_songs = [[]]
        for item in tracks_json.fetch_tracks():
            self.ya_songs.append((item["artists"][0]["name"], item["title"]))
        
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
        data['spotify_dc'] = self.text_spotify_dc.text()
        data['spotify_key'] = self.text_spotify_key.text()
        
        with open("env.json", "w") as f:
            json.dump(data, f, indent=4)
            
        cfg = Config(
            logger=NoopLogger()
        )
        
        cookie = {
            "identifier": self.text_spotify_login.text(),
            "cookies": {
                "sp_dc": self.text_spotify_dc.text(),
                "sp_key": self.text_spotify_key.text()
            }
        }
        
        self.spotify_login = Login.from_cookies(dump=cookie, cfg=cfg)
        
        if self.spotify_login.logged_in:
            self.is_spotify_api_working = True
            self.start_conversion_btn.setEnabled(self.is_api_good())
            self.spotify_api_work_status_label.setText("Spotify API готово")
            
            dlg = QDialog(self)
            dlg.setWindowTitle("Проверка Spotify")
            layout = QVBoxLayout()
            message = QLabel("Авторизация успешна!")
            layout.addWidget(message)
            dlg.setLayout(layout)
            dlg.exec()
        else:
            try:
                self.spotify_login.login()
                dlg = QDialog(self)
                dlg.setWindowTitle("Проверка Spotify")
                layout = QVBoxLayout()
                message = QLabel("Авторизация успешна!")
                layout.addWidget(message)
                dlg.setLayout(layout)
                dlg.exec()
            except Exception as e:
                print(f"SPOTIFY LOGIN ERROR: {e}")
                dlg = QDialog(self)
                dlg.setWindowTitle("Проверка Spotify")
                layout = QVBoxLayout()
                message = QLabel("Не удалось авторизоваться!")
                layout.addWidget(message)
                dlg.setLayout(layout)
                dlg.exec()
                return

        self.spotify_tracks = self.get_spotify_liked_tracks(self.spotify_login)
            
    def start_conversion(self):
        pass
        
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
                self.text_spotify_dc.setText(data["spotify_dc"])
                self.text_spotify_key.setText(data["spotify_key"])
                
    def get_info_ya_api(self):
        webbrowser.open("https://github.com/bezdarnosti-yt/Yandex-To-Spotify/blob/master/YANDEX.md")
    
    def get_info_spotify_api(self):
        webbrowser.open("https://github.com/bezdarnosti-yt/Yandex-To-Spotify/blob/master/SPOTIFY.md")
        
    def stop_getting(self):
        self.is_getting_tracks = False
    
    def try_export(self):
        pass
    
    def is_api_good(self) -> bool:
        return self.is_ya_api_working and self.is_spotify_api_working
    
    def get_spotify_liked_tracks(self, login: Login) -> list[list]:
        base = BaseClient(login.client)
        all_tracks = [[]]
        limit = 50
        offset = 0
        total = None

        while True:
            url = "https://api-partner.spotify.com/pathfinder/v1/query"
            params = {
                "operationName": "fetchLibraryTracks",
                "variables": json.dumps({"limit": limit, "offset": offset}),
                "extensions": json.dumps({
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": base.part_hash("fetchLibraryTracks"),
                    }
                }),
            }

            resp = login.client.post(url, params=params, authenticate=True)
            data = resp.response["data"]["me"]["library"]["tracks"]
            total = data["totalCount"]

            for item in data["items"]:
                track_data = item["track"]["data"]
                title = track_data["name"]
                artists = [a["profile"]["name"] for a in track_data["artists"]["items"]]
                artist = ", ".join(artists)
                all_tracks.append((artist, title))

            offset += limit

            if offset >= total:
                break

        return all_tracks
        
def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
    

if __name__ == "__main__":
    main()