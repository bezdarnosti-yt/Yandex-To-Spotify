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
        
        self.check_ya_api_btn = QPushButton("Проверить доступ к Яндекс.API")
        self.check_ya_api_btn.clicked.connect(self.check_ya_api)
        layout.addWidget(self.check_ya_api_btn)
        
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
        
        self.check_spotify_btn = QPushButton("Проверить доступ к Spotify.API")
        self.check_spotify_btn.clicked.connect(self.check_spotify_api)
        layout.addWidget(self.check_spotify_btn)
        
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
        
        self.ya_tracks = self.get_ya_liked_tracks(self.ya_client)
        
        self.is_ya_api_working = True
        self.start_conversion_btn.setEnabled(self.is_api_good())
        self.ya_api_work_status_label.setText("Яндекс API готово")
        
        self.check_ya_api_btn.setEnabled(not self.is_ya_api_working)
        
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
            
            self.check_spotify_btn.setEnabled(not self.is_spotify_api_working)
            
            self.spotify_tracks = self.get_spotify_liked_tracks(self.spotify_login)
            self.spotify_tracks.sort(key=lambda row: (row[0], row[1]))
            
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
                
                self.spotify_tracks = self.get_spotify_liked_tracks(self.spotify_login)
                self.spotify_tracks.sort(key=lambda row: (row[0], row[1]))
                
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
            
    def start_conversion(self):
        self.tracks = self.delete_similar_tracks_from_lists(self.ya_tracks, self.spotify_tracks)
        
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
        
        total_tracks = len(self.tracks)
        
        for i, track in enumerate(self.tracks):
            if (self.is_getting_tracks):
                artist, song = track
                log_text.append(f"{i + 1}. {artist} - {song}")
            
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
                self.text_spotify_dc.setText(data["spotify_dc"])
                self.text_spotify_key.setText(data["spotify_key"])
                
    def get_info_ya_api(self):
        webbrowser.open("https://github.com/bezdarnosti-yt/Yandex-To-Spotify/blob/master/YANDEX.md")
    
    def get_info_spotify_api(self):
        webbrowser.open("https://github.com/bezdarnosti-yt/Yandex-To-Spotify/blob/master/SPOTIFY.md")
        
    def stop_getting(self):
        self.is_getting_tracks = False
    
    def try_export(self):
        self.is_exporting = True
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Экспорт")
        layout = QVBoxLayout()
        dlg.setLayout(layout)
        
        log_text = QTextEdit()
        log_text.setReadOnly(True)
        layout.addWidget(log_text)
        
        progress_bar = QProgressBar()
        layout.addWidget(progress_bar)
        
        stop_running_btn = QPushButton("Стоп")
        stop_running_btn.clicked.connect(self.stop_run)
        layout.addWidget(stop_running_btn)
        
        dlg.show()
        
        total_tracks = len(self.tracks)
        
        playlist = PrivatePlaylist(self.spotify_login, "spotify:collection:tracks")
        song = Song(playlist=playlist)
        
        for i, track in enumerate(self.tracks):
            if self.is_exporting:
                artist, name = track
                
                query = f"{artist} {name}"
                results = song.query_songs(query, limit=1)
                
                items = results["data"]["searchV2"]["tracksV2"]["items"]
                if not items:
                    is_sucessful = False
                else:
                    is_sucessful = True
                
                if is_sucessful:
                    res = items[0]["item"]["data"]
                    found_title = res["name"]
                    found_artist = res["artists"]["items"][0]["profile"]["name"]
                    song_id = items[0]["item"]["data"]["uri"].split(":")[-1]
            
                    if (name in found_title or artist in found_artist):
                        try:
                            song.like_song(song_id)
                            message = f"{i + 1}. {artist} - {name} [УДАЧНО] ({found_artist} - {found_title}))"
                            log_text.append(f'<span style="color: green;">{message}</span>')
                        except Exception as e:
                            message = f"{i + 1}. {artist} - {name} [ОШИБКА] {e}"
                            log_text.append(f'<span style="color: red;">{message}</span>')
                    else:
                        message = f"{i + 1}. {artist} - {name} [НЕ НАЙДЕНО] ({found_artist} - {found_title})"
                        log_text.append(f'<span style="color: red;">{message}</span>')
                else:
                    message = f"{i + 1}. {artist} - {name} [ОШИБКА]"
                    log_text.append(f'<span style="color: red;">{message}</span>')
                
                progress = int((i + 1) / total_tracks * 100)
                progress_bar.setValue(progress)
                
                QApplication.processEvents()
        
        log_text.append("Экспорт завершен!")
        QApplication.processEvents()
    
    def is_api_good(self) -> bool:
        return self.is_ya_api_working and self.is_spotify_api_working
    
    def get_spotify_liked_tracks(self, login: Login) -> list[list]:
        base = BaseClient(login.client)
        all_tracks = []
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
        
    def get_ya_liked_tracks(self, ya_client: Client) -> list[list]:
        tracks_json = ya_client.users_likes_tracks()
        ya_tracks = []
        for item in tracks_json.fetch_tracks():
            ya_tracks.append((item["artists"][0]["name"], item["title"]))
        ya_tracks.sort(key=lambda row : (row[0], row[1]))
        return ya_tracks
    
    def delete_similar_tracks_from_lists(self, ya_tracks: list[list],  spotify_tracks: list[list]) -> list[list]:
        spotify_set = set(tuple(track) for track in spotify_tracks)
        
        unique_ya_tracks = []
        
        for track in ya_tracks:
            track_tuple = tuple(track)
            if track_tuple not in spotify_set:
                unique_ya_tracks.append(track)
                
        return unique_ya_tracks
    
    def stop_run(self):
            self.is_exporting = False
    
def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
    

if __name__ == "__main__":
    main()