# Yandex-To-Spotify

[Поддержать автора (DonationAlerts)](https://www.donationalerts.com/r/bezdarnosti1)

Десктопное приложение для переноса понравившихся треков из **Яндекс.Музыки** в **Spotify**.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Как это работает

1. Приложение получает список лайкнутых треков из Яндекс.Музыки
2. Получает список уже лайкнутых треков в Spotify
3. Убирает дубликаты
4. Находит оставшиеся треки в Spotify и добавляет их в «Мне нравится»

---

## Быстрый старт

### Вариант 1 — Готовый exe

1. Скачай `YaConversion.exe` из [Releases](../../releases)
2. Запусти и следуй инструкциям в приложении

### Вариант 2 — Запуск из исходников

```bash
# Клонировать репозиторий
git clone https://github.com/bezdarnosti-yt/Yandex-To-Spotify.git
cd Yandex-To-Spotify

# Установить зависимости
pip install -r requirements.txt

# Запустить
python main.py
```

---

## Получение токенов

### Яндекс.Музыка

Подробная инструкция: [YANDEX.md](YANDEX.md)

Кратко: установи расширение для браузера и скопируй токен одной кнопкой.

### Spotify

Подробная инструкция: [SPOTIFY.md](SPOTIFY.md)

Кратко: установи расширение Cookie-Editor, открой Spotify в браузере и скопируй значения `sp_dc` и `sp_key`.

---

## Зависимости

| Пакет | Назначение |
|---|---|
| `PyQt6` | Графический интерфейс |
| `yandex-music` | API Яндекс.Музыки |
| `spotapi` | API Spotify |

---

## Сборка exe самостоятельно

```bash
pip install pyinstaller

pyinstaller --onefile --windowed --name "YaConversion" --collect-all PyQt6 --collect-all yandex_music --collect-all spotapi --collect-all tls_client --add-binary "tls-client-windows-64.dll;tls_client/dependencies/" main.py
```

Готовый файл появится в папке `dist/`.

---

## Важно

- Токены и куки хранятся локально в файле `env.json` рядом с приложением
- Антивирусы могут ложно срабатывать на `.exe` — это нормальное поведение для PyInstaller-сборок
- Приложение не передаёт данные третьим лицам

---

## 📄 Лицензия

[MIT](LICENCE.txt)
