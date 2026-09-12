# Контекст для переноса проекта MarketApp Smart Rent в новый чат

Скопируй/прикрепи этот файл и архив `marketapp_smart_rent_transfer_pack.zip` в новый чат и скажи: **«Продолжай разработку с этого состояния. Сначала прочитай контекст и файлы, не начинай заново.»**

## 1. Цель проекта

Разрабатывается плагин **MarketApp Smart Rent** для **FunPay Cardinal**, который автоматизирует аренду Telegram NFT Gifts через MarketApp, а в дальнейшем — полный цикл выдачи арендованного подарка покупателю через Fragment/Telegram.

У пользователя уже существует **78 действующих FunPay-лотов**. Их нельзя заставлять пересоздавать, вручную менять описания или вставлять lot_id в каждый лот.

### Ручной процесс, который нужно автоматизировать

1. Клиент оплачивает заказ на FunPay.
2. Определяется нужная коллекция NFT и оплаченный срок.
3. Через Fragment → Connect Telegram получается короткоживущая Telegram OAuth-ссылка вида `https://t.me/oauth?startapp=...`.
4. Ссылка отправляется покупателю, покупатель подтверждает Telegram-вход.
5. Нужный NFT арендуется на MarketApp.
6. Сейчас оплата вручную подтверждается через Tonkeeper; в будущем — server-side TON hot wallet.
7. На Fragment берётся **другая** ссылка — TON Connect из `Connect TON`.
8. TON Connect передаётся в MarketApp → Assign to Telegram.
9. Fragment → My Assets → Gifts → Display in Telegram → Personal account → Save.
10. После выдачи Telegram/TON-сессия очищается/отключается перед следующим клиентом.

Критически важно: Telegram OAuth `t.me/oauth?startapp=...` и Fragment TON Connect — это разные ссылки.

В будущем нужна команда покупателя `!новаяссылка`, создающая новую OAuth-ссылку, если старая истекла.

## 2. FunPay Cardinal

Плагин предназначен именно для FunPay Cardinal.

Используется обработчик:

```python
BIND_TO_NEW_ORDER = [on_new_order]
```

В Cardinal core при обработке заказа могут быть доступны:

- `e.order`
- `e.order.amount`
- `e.lot_id`
- `e.lot_shortcut`

В публичном `handlers.py` Cardinal логика сопоставления заказа способна установить `e.lot_id`.

Архитектура определения лота:

1. Если `lot_id` уже известен — использовать его.
2. Иначе посмотреть сохранённый auto-binding.
3. Иначе сопоставить описание/название заказа с известной коллекцией.
4. После первого успешного сопоставления сохранить `lot_id -> collection`.
5. Все заказы, не относящиеся к whitelist NFT rental lots, игнорировать.

### Количество товара = срок

Обычно:

- 1 unit = 24 часа
- 2 units = 48 часов
- 3 units = 72 часа

Покупка нескольких единиц означает **один NFT на больший срок**, а не несколько NFT.

Специальное правило, согласованное ранее:

- `BIG YEAR`: 1 unit = 96 часов.

## 3. MarketApp

Официальный сервис: `https://marketapp.org/`

API: `https://api.marketapp.org/`

Авторизация: значение API token передаётся в заголовке `Authorization` без `Bearer`.

Из документации были найдены endpoints:

- `GET /v1/rent/gifts/`
- `GET /v1/rent/my-rented/`
- `POST /v1/rent/{nft_address}/pay/`
- `POST /v1/rent/{nft_address}/extend/`
- `POST /v1/rent/{nft_address}/tonconnect/`

Python package:

```bash
pip install -U marketapp-api
```

В исследованной версии SDK использовался `MarketappClient`, с функциями по смыслу:

- `get_gifts_available_for_rent()`
- `rent_nft()`
- `extend_rent_nft()`
- `connect_tonconnect()`

SDK/пакет также предусматривает Auto-Pay через TON wallet/tonutils.

Для автоматической оплаты планировались переменные/секреты:

- `MARKETAPP_API_TOKEN`
- `MARKETAPP_WALLET_SEED`
- `MARKETAPP_TON_API_KEY`
- `MARKETAPP_WALLET_VERSION` (обычно `V5R1`)

**Никогда не просить пользователя присылать seed phrase в чат.** Для Auto-Pay использовать отдельный low-balance hot wallet, а секрет хранить на сервере вне публичного конфига с ограниченными правами.

## 4. Главная логика выбора аренды

Нельзя хардкодить 0.01 TON и нельзя просто выбирать минимальную цену за день.

Floor аренды и наличие NFT динамические и отличаются между коллекциями.

Перед каждым заказом нужно получать свежие предложения MarketApp. Перед самой оплатой — повторный запрос и повторный выбор, потому что предложение могло исчезнуть.

### Правильный критерий

Нужно выбрать предложение с **минимальной полной стоимостью**, которое обеспечивает срок **не меньше оплаченного**.

Пример: покупатель оплатил 1 день.

- NFT A: 1 день = 0.02 TON
- NFT B: 2 дня = 0.01 TON
- NFT C: 3 дня = 0.03 TON

Выбрать NFT B: 2 дня за 0.01 TON.

Overdelivery разрешён: можно дать клиенту больше времени, если это дешевле.

Алгоритм:

```text
requested_duration = оплаченный срок
получить свежие offers
оставить offers, где actual_duration >= requested_duration
сравнить total payable cost
выбрать min(total_price)
```

Если выбранный offer исчез перед списанием — заново запросить MarketApp и пересчитать.

Защитный `max_total_ton` допустим только как пользовательская настройка, а не фиксированное бизнес-правило.

## 5. Все 78 существующих FunPay-лотов

1. HAPPY BROWNIES
2. LOOT BAGS
3. SWAG BAG
4. DESK CALENDAR
5. STELLAR ROCKET
6. LIGHT SWORD
7. LUNAR SNAKE
8. INPUT KEYS
9. SNOOP CIGARS
10. FRESH SOCKS
11. LUSH BOUQUETS
12. TAMA GADGET
13. JOLLY CHIMP
14. SPICED WINE
15. EVIL EYES
16. EASTER EGG
17. SPY AGARIC
18. JOYFUL BUNDLE
19. HYPNO LOLLIPOPS
20. WINTER WREATH
21. STAR NOTEPAD
22. JACK-IN-THE-BOX
23. BIG YEAR
24. SAKURA FLOWERS
25. BUNNY MUFFIN
26. BOW TIE
27. WITCH HATS
28. HEX POT
29. BERRY BOX
30. SANTA HAT
31. ETERNAL CANDLES
32. VALENTINE BOX
33. JINGLE BELL
34. SKY STILETTOS
35. HANGING STAR
36. LOVE POTIONS
37. ETERNAL ROSES
38. SNOW GLOBE
39. CRYSTAL BALLS
40. DIAMOND RING
41. TOP HATS
42. CUPID CHARMS
43. TRAPPED HEARTS
44. RARE BIRDS
45. SKULL FLOWERS
46. SNOOP DOGG
47. VINTAGE CIGAR
48. UFC STRIKE
49. SWISS WATCH
50. MINI OSCAR
51. VOODOO DOLLS
52. GEM SIGNET
53. ION GEMS
54. WESTSIDE SIGNS
55. NAIL BRACELET
56. ASTRAL SHARD
57. HEROIC HELMET
58. MIGHTY ARM
59. HEART LOCKETS
60. SCARED CAT
61. PRECIOUS PEACHES
62. DUROV CAPS
63. ПАПАХА ХАБИБА
64. ELECTRIC SKULL
65. SHARP TONGUE
66. BONDED RING
67. MAGIC POTION
68. ARTISAN BRICKS
69. TOY BEARS
70. SIGNET RING
71. MAD PUMPKIN
72. NEKO HELMETS
73. KISSED FROGS
74. LOVE CANDLE
75. RECORD PLAYERS
76. SNOW MITTENS
77. LOW RIDERS
78. FLYING BROOM

Подтверждённое соответствие:

- `ПАПАХА ХАБИБА` → `Khabib's Papakhas`

Из скриншотов MarketApp были замечены/подтверждены варианты названий:

- Durov's Caps
- Magic Potions
- Berry Boxes
- Electric Skulls
- Snow Globes
- Hex Pots
- Flying Brooms
- Santa Hats
- Jingle Bells
- Valentine Boxes
- Mighty Arms
- Big Years
- Bonded Rings
- Signet Rings
- Sharp Tongues
- Khabib's Papakhas
- Hanging Stars
- Gem Signets
- Bunny Muffins
- Mad Pumpkins
- Snoop Doggs
- Artisan Bricks
- Light Swords

Нужны aliases: singular/plural, `'`/`’`, FunPay vs MarketApp naming. Но желательно хранить каноническое MarketApp collection name.

## 6. Созданные файлы и история версий

Все перечисленные файлы лежат в архиве переноса.

### Ранний read-only прототип

- `marketapp_floor.py`
- `marketapp_floor_README.md`

### Версия с 78 лотами

- `marketapp_floor_78.py`
- `marketapp_floor_78.json`
- `marketapp_floor_78_README.md`

### Smart Rent v0.3.1

- `marketapp_smart_rent_v0_3_1.py`
- `marketapp_smart_rent_v0_3_1.json`
- `marketapp_smart_rent_v0_3_1_README.md`

Это была первая основная версия для Cardinal.

Metadata:

```python
NAME = "MarketApp Smart Rent"
VERSION = "0.3.1"
UUID = "a9912d45-31d8-42a1-92aa-b40e01202581"
BIND_TO_NEW_ORDER = [on_new_order]
```

v0.3.1:

- содержала карту 78 лотов;
- auto-bind `lot_id`;
- читала `order.amount`;
- 24h/unit, BIG YEAR 96h/unit;
- получала offers MarketApp;
- пыталась универсально нормализовать Pydantic/dict ответы;
- поддерживала fixed duration / daily price / min/max duration;
- выбирала по `(total_price, actual_days, nft_address)`;
- повторно запрашивала MarketApp перед реальной арендой;
- имела защитные настройки;
- НЕ выполняла Fragment/Telegram OAuth transfer.

Default safety:

```json
"auto_rent": false,
"dry_run": true,
"max_total_ton": 10.0,
"max_requested_days": 30,
"recheck_before_rent": true
```

Файл проходил `python -m py_compile` и synthetic self-test. В тесте для заказа на 1 день между offers 1d=0.02, 2d=0.01, 3d=0.03 корректно выбирался 2d=0.01.

### Ветка v0.4

В рабочем каталоге сохранились несколько вариантов:

- `marketapp_smart_rent.py`
- `marketapp_smart_rent_v0_4_0.py`
- `marketapp_smart_rent_v0_4_0-2.py`
- `marketapp_smart_rent_v0_4_0_3.py`
- `marketapp_smart_rent_v0_4_README.md`
- `marketapp_smart_rent_v0_4_0_README.md`

Самый новый по версии/времени файл: **`marketapp_smart_rent_v0_4_0_3.py`**, VERSION=`0.4.0.3`.

Это нужно считать текущим кандидатом для дальнейшей проверки, но НЕ считать гарантированно production-ready до теста на конкретной установленной версии Cardinal.

v0.4.x уже содержит `SETTINGS_PAGE = True` и Telegram UI на `telebot.types.InlineKeyboardMarkup / InlineKeyboardButton`, обработчики настроек, тест API, status/bind и Cardinal hooks. В разных v0.4-вариантах архитектура немного менялась, поэтому при продолжении следует сравнить их и взять лучший/самый новый вариант, а не случайно откатиться на v0.3.1.

## 7. Почему появился вопрос про настройки

Пользователь установил v0.3.1 в Cardinal. Плагин загрузился и появился в Telegram-интерфейсе Cardinal, но в карточке были только стандартные кнопки:

- Деактивировать
- Закрепить
- Удалить
- Назад

Пользователь спросил: почему нет нормальных настроек, нужно добавить функций и настроек, и зачем одновременно 78 лотов в плагине и отдельный конфиг.

После этого началась ветка v0.4 с `SETTINGS_PAGE=True`.

## 8. Желаемая нормальная страница настроек Cardinal

Нужно иметь полноценное управление из Telegram:

- MarketApp API token
- проверка MarketApp API
- Dry Run
- Auto Rent ON/OFF
- Auto Pay ON/OFF
- Recheck before rent
- `max_total_ton`
- `max_requested_days`
- часы за unit
- отдельное правило BIG YEAR
- уведомлять покупателя ON/OFF
- шаблоны сообщений
- показывать найденный NFT
- показывать цену
- показывать фактически выданный срок
- журнал последних заказов
- состояние текущих заказов
- тест MarketApp API
- тест кошелька без транзакции
- баланс hot wallet
- статус Fragment
- статус MarketApp
- просмотр lot_id → collection
- сброс auto-binding
- ручное изменение binding
- повторная обработка заказа
- pause new orders
- emergency stop Auto Pay
- verbose logging / log level

Seed phrase нельзя показывать в Telegram UI в открытом виде.

Если секрет вводится через Telegram, входящее сообщение желательно удалять сразу, но более безопасно рекомендовать server-side secret/env. Любое хранение seed в JSON должно быть отдельно оценено по рискам.

## 9. Архитектура config/state, которую пользователь хочет

Пользователь не хочет бессмысленного дублирования 78 лотов одновременно в Python и отдельном JSON.

Желаемая логика:

### Python plugin

Только программная логика + возможно `DEFAULT_CONFIG`, используемый **только для первичного создания** пользовательского файла.

### Config

`storage/.../marketapp_smart_rent.json`

Хранить:

- пользовательские настройки;
- mapping collections;
- aliases;
- canonical MarketApp names;
- hours_per_unit;
- special rules.

После первого создания JSON должен стать рабочим источником конфигурации, чтобы не было двух независимых изменяемых списков 78 лотов.

### State

`marketapp_smart_rent_state.json`

Только автоматически меняющиеся данные:

- lot_id bindings;
- processed order IDs;
- in-flight operations;
- timestamps;
- recent orders/statistics;
- retry state.

### Secrets

Отдельно от обычного config. Предпочтительно env/server secret. Если файл — permissions 600 и не показывать содержимое в UI/logs.

## 10. Что ещё НЕ реализовано как законченный production flow

Полная выдача через Fragment пока не завершена.

Нужно реализовать:

1. Telegram OAuth через Fragment.
2. Получение `https://t.me/oauth?startapp=...`.
3. Автоматическую отправку покупателю FunPay.
4. `!новаяссылка`.
5. Ожидание/проверку OAuth confirmation.
6. Получение Fragment TON Connect.
7. `MarketApp connect_tonconnect()` / Assign to Telegram.
8. Fragment Display in Telegram → Personal account.
9. Logout/disconnect/cleanup.
10. State machine заказа.
11. Idempotency — защита от повторного события Cardinal и двойной аренды.
12. Retry/error handling.
13. Безопасный server-side Auto-Pay.

Ранее был найден пакет `fragment-api-py`, который заявлял session storage, Telegram OAuth, `assign_to_telegram()`, `get_assign_accounts()` и т. п. Перед реальным использованием нужно заново проверить актуальную документацию/исходники и не доверять старым предположениям.

## 11. Важные требования безопасности

- Не просить seed phrase в чат.
- Не логировать API token/seed/private keys.
- Автооплату первоначально держать выключенной.
- `dry_run=true` до проверки реального response schema MarketApp и поведения Cardinal.
- Перед списанием повторно получать offers.
- Нужна idempotency по FunPay order ID.
- Нужен emergency stop.
- Желателен отдельный low-balance TON wallet для сервиса.

## 12. Что нужно сделать в новом чате

Не начинать с нуля.

1. Прочитать этот файл.
2. Изучить все приложенные `.py`, `.json`, `.md`.
3. Считать `marketapp_smart_rent_v0_4_0_3.py` самым новым кандидатом, но сравнить его с `v0_4_0-2.py` и другими v0.4, чтобы не потерять функции.
4. Проверить актуальный FunPay Cardinal plugin API / SETTINGS_PAGE по официальному репозиторию перед изменением Telegram UI.
5. Довести нормальную страницу настроек.
6. Убрать ненужное дублирование 78 лотов между code/config.
7. Сохранить всю уже согласованную rental selection logic.
8. Реальные TON transactions пока не включать по умолчанию.
9. После dry-run теста на реальном заказе попросить только безопасные логи без секретов и адаптировать parser к фактическому MarketApp response schema.

## 13. Текущий скриншот

В архив включён исходный скриншот `image-1789228822449.jpg`, на котором видно, что v0.3.1 был успешно загружен Cardinal и отображался в карточке плагина, но без собственной страницы настроек.

## 14. Ключевая фраза для продолжения

**Продолжай MarketApp Smart Rent с текущей ветки v0.4. Не переписывай бизнес-логику заново. Сначала проверь файлы и API FunPay Cardinal, затем доведи Settings Page и config/state architecture.**
