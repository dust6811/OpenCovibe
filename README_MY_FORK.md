# Мой форк OpenCovibe

**Оригинал:** https://github.com/AnyiWang/OpenCovibe
**Мой форк:** https://github.com/dust6811/OpenCovibe

---

## 🚀 Уникальные функции

### 1. 1M контекст для Claude Opus 4.6 / Sonnet 4.6

Автоматическое определение контекстного окна 1M токенов для новейших моделей Anthropic.

**Файлы:** `src-tauri/src/model_context.rs`, `src-tauri/src/agent/claude_protocol.rs`

---

### 2. Глобальная настройка Permission Mode

Настройка режима разрешений в **Settings → General** вместо ручного редактирования файлов.

**Файлы:** `src/routes/settings/+page.svelte`, `messages/*.json`

**Режимы:**
- **Ask** — спрашивать каждое действие
- **Auto Edit** — авто-редактирование файлов
- **Full Auto (Bypass)** — никаких вопросов
- **Plan** — только чтение
- **Don't Ask** — отклонять всё

---

### 3. Split-view панель (WIP)

Кнопка для переключения панели с файлами (требуется доработка компонента).

**Файлы:** `src/lib/components/ChatToolbar.svelte`, `src/routes/chat/+page.svelte`

---

## 📦 Установка

### Вариант 1: Сборка из исходников

```bash
git clone https://github.com/dust6811/OpenCovibe.git
cd OpenCovibe
git checkout custom-1m-context
npm install
npm run tauri build
```

### Вариант 2: Скачать билд

См. [Releases](https://github.com/dust6811/OpenCovibe/releases) (если настроены CI-билды)

---

## 🔄 Обновление из upstream

См. [UPDATE_GUIDE.md](UPDATE_GUIDE.md)

**Кратко:**

```bash
# Обновить master
git checkout master
git fetch upstream
git merge upstream/master
git push origin master

# Обновить свою ветку
git checkout custom-1m-context
git rebase master
git push --force-with-lease origin custom-1m-context
```

---

## 📚 Документация

| Файл | Описание |
|------|----------|
| [MY_CHANGES.md](MY_CHANGES.md) | Полный список всех изменений от оригинала |
| [UPDATE_GUIDE.md](UPDATE_GUIDE.md) | Руководство по обновлению из upstream |
| [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) | План развития на 2026 год |

---

## 🛠️ Разработка

### Создать новую функцию

```bash
git checkout master
git checkout -b feature/my-feature
# Пиши код, тестируй
git commit -m "feat: my feature"
git push origin feature/my-feature
```

### Запустить тесты

```bash
npm test              # Frontend тесты
cd src-tauri && cargo test  # Rust тесты
npm run verify        # Всё + линтеры
```

---

## 📊 Статус

| Функция | Статус | Ветка |
|---------|--------|-------|
| 1M контекст | ✅ Готово | `custom-1m-context` |
| Permission Mode UI | ✅ Готово | `custom-1m-context` |
| Split-view кнопка | ✅ Готово | `custom-1m-context` |
| Split-view панель | ⚠️ Требует починки | `custom-1m-context` |
| Always Allow UI | 📋 Запланировано | — |
| Профили разрешений | 📋 Запланировано | — |

---

## 🤝 Контрибьюция

PR приветствуются! Пожалуйста:

1. Создай issue с описанием
2. Создай ветку `feature/...`
3. Напиши код + тесты
4. Отправь PR

---

## 📝 Коммиты

Основная ветка с изменениями: `custom-1m-context`

```
2ddfee3 feat: 1M context window for Opus 4.6/Sonnet 4.6
```

Планируемые:
```
feat: Add global Default Permission Mode setting
feat: Fix SplitViewPanel component
```

---

## 📞 Контакты

- **GitHub:** https://github.com/dust6811/OpenCovibe
- **Issues:** https://github.com/dust6811/OpenCovibe/issues

---

## 📄 Лицензия

Apache License 2.0 (как в оригинальном репозитории)

---

*Последнее обновление: 2026-03-29*
