# Ozon PDF Parser

Фильтр этикеток Ozon: в ticket-PDF остаются только те страницы, чьи номера
отправления присутствуют в колонке «Номер отправления» листа сборки (assembly-PDF).

Формат номера — `<8–12 цифр>-<4 цифры>-<1 цифра>`, например `71491670-0203-2` или
`0118905292-0354-2`. В ticket номер напечатан повёрнутым текстом и разбит на части
(`5255 8332` + `-0322-1`), поэтому он восстанавливается из колонок этикетки.
Сравнение не зависит от ведущих нулей префикса.

## Архитектура

Трёхслойная архитектура, зависимости направлены внутрь — презентация зависит от
сервисов, сервисы от домена, инфраструктура реализует работу с PDF.

```
app/
├── domain/            # доменные модели, без внешних зависимостей
│   ├── shipment.py    # ShipmentNumber — разбор/канонический вид номера
│   └── report.py      # FilterReport — результат фильтрации
├── services/          # бизнес-логика и порты
│   ├── ports.py       # Protocol: AssemblyReader, TicketReader, PageWriter, FilterRunner
│   └── filter_service.py   # FilterService — отбор страниц по листу сборки
├── infrastructure/    # адаптеры к библиотекам PDF
│   ├── pdf_reader.py  # PdfAssemblyReader, PdfTicketReader (pdfplumber)
│   └── pdf_writer.py  # PdfPageWriter (pypdf)
├── web/               # презентация: HTTP + шаблоны
│   ├── app.py         # create_app(), роуты FastAPI
│   ├── server.py      # точка входа uvicorn
│   ├── templates/     # Jinja2: base, index, partials/*
│   └── static/style.css
├── cli.py             # презентация: консольный вход
└── config.py          # Settings + настройка логирования
```

Слой считается заменяемым: `FilterService` принимает интерфейсы читателя/писателя
(`ports.py`), поэтому инфраструктуру можно заменить без изменения бизнес-логики.

## Установка

```sh
uv sync
```

## CLI

```sh
uv run ozon-filter -a assembly.pdf -t ticket.pdf -o filtered_ticket.pdf -v
```

Коды выхода: `0` — успех, `1` — в листе сборки нет номеров, `2` — совпадений нет.

## Веб-интерфейс (FastAPI + HTMX)

```sh
uv run ozon-filter-web          # http://127.0.0.1:8000
uv run ozon-filter-web --port 8080 --reload
# или
uv run python -m app.web
```

Форма загружает один assembly и один ticket, ответ подставляется через HTMX;
результат доступен по `/download/{job_id}`. Есть `/healthz` для проверки живости.

## Конфигурация

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `OZON_HOST` | `127.0.0.1` | адрес веб-сервера |
| `OZON_PORT` | `8000` | порт веб-сервера |
| `OZON_LOG_LEVEL` | `INFO` | уровень логирования |

## Заметки по продакшену

- HTMX подключён с CDN (`unpkg.com`) — для офлайн-контура положите `htmx.min.js`
  в `app/web/static/` и замените ссылку в `base.html`.
- Готовые PDF хранятся во временных каталогах процесса; для долгого хранения
  замените `app.state.jobs` на внешнее хранилище (S3/диск с TTL).
