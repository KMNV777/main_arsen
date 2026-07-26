# С праздником, любовь моя

Лендинг-викторина к годовщине: титул + 4 квартала по 4 вопроса.

## Локальный запуск (с hot reload)

Нужны Node.js 18+ и npm.

```bash
cd anniversary
npm install
npm run dev
```

Открой [http://localhost:8080](http://localhost:8080).

Правки в `index.html`, `css/`, `js/` подхватываются сразу — страница обновляется сама.

### Команды

| Команда | Что делает |
| --- | --- |
| `npm run dev` | Dev-сервер на `:8080` с hot reload |
| `npm run build` | Сборка в `dist/` |
| `npm run preview` | Превью собранного сайта |

### Без Node (запасной вариант)

```bash
cd anniversary
python3 -m http.server 8080
```

## Свои фото

Положи снимки в `assets/photos/`:

| Файл | Где используется |
| --- | --- |
| `hero.jpg` | Титульная страница |
| `q1.jpg` … `q4.jpg` | Фоны кварталов |
| `finale.jpg` | Финальный экран |

## Вопросы

Тексты и правильные ответы — в `js/quiz.js` (объект `quarters`).
