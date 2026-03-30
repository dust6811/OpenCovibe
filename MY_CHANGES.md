# Мои изменения от оригинала (AnyiWang/OpenCovibe)

Этот документ отслеживает все изменения, внесённые в форк [dust6811/OpenCovibe](https://github.com/dust6811/OpenCovibe).

---

## 📊 Сводка изменений

| Файл | Изменения | Строк добавлено |
|------|-----------|-----------------|
| `src-tauri/src/model_context.rs` | **НОВЫЙ** — таблица контекстных окон для 30+ моделей | +157 |
| `src-tauri/src/agent/claude_protocol.rs` | Fallback для context_window + тесты | +81 |
| `src-tauri/src/lib.rs` | Подключение модуля model_context | +1 |
| `src/routes/chat/+page.svelte` | Split-view (закомментирован) + resize логика | +51 |
| `src/lib/components/ChatToolbar.svelte` | Кнопка Split-view | +22 |
| `src/lib/components/SplitViewPanel.svelte` | **НОВЫЙ** — панель просмотра файлов | +592 |
| `src/lib/components/FileTreeNode.svelte` | **НОВЫЙ** — рекурсивное дерево файлов | +85 |
| `src/routes/settings/+page.svelte` | Настройка Permission Mode | +30 |
| `messages/en.json` | Переводы (permission + split-view) | +13 |
| `messages/zh-CN.json` | Переводы (permission + split-view) | +13 |
| `SPLIT_VIEW_CHANGES.md` | **НОВЫЙ** — документация split-view | +50 |
| **Итого** | **13 файлов** | **+1095 строк** |

---

## 🔧 Детали по файлам

### 1. `src-tauri/src/model_context.rs` (НОВЫЙ ФАЙЛ)
**Назначение:** Таблица контекстных окон для 30+ моделей

**Что делает:**
- Возвращает 1M токенов для Claude Opus 4.6 / Sonnet 4.6
- Возвращает 200K для Claude Opus/Sonnet 4.5, 4.1, 3.7, 3.5, Haiku 3.5
- Возвращает 128K-256K для DeepSeek, Kimi, Zhipu GLM, Bailian, и др.
- Используется как fallback, когда CLI не передаёт context_window

**Источники:**
- Официальная документация Anthropic
- API спецификации провайдеров

---

### 2. `src-tauri/src/agent/claude_protocol.rs`
**Изменения:**
- Строки 1017-1024: Использование `model_context::get_context_window()` вместо значения от CLI
- Строки 2114-2190: Добавлены тесты `test_result_context_window_fallback`

**Зачем:** CLI часто передаёт устаревшие значения context_window. Наша таблица всегда актуальна.

---

### 3. `src-tauri/src/lib.rs`
**Изменения:**
- Строка ~200: `mod model_context;` — подключение нового модуля

---

### 4. `src/routes/chat/+page.svelte`
**Изменения:**
- Строка 87: Закомментирован import SplitViewPanel (временное решение)
- Строки 146-147: Состояние split-view (открыт/закрыт, ширина)
- Строки 1292-1296: Обработчик события `ocv:toggle-split-view`
- Строки 3357-3395: Логика resize для split-view панели

**Статус:** Split-view временно отключён (компонент требует доработки)

---

### 4.1. `src/lib/components/SplitViewPanel.svelte` (НОВЫЙ ФАЙЛ)
**Назначение:** Панель для просмотра файлов проекта

**Функционал:**
- Древовидное отображение файлов с неограниченной вложенностью
- Просмотр кода с подсветкой синтаксиса (CodeMirror)
- Preview для Markdown-файлов
- Просмотр изображений
- Git diff viewer
- Редактирование файлов с сохранением
- Изменение ширины панели перетаскиванием (200–600px)
- Сохранение состояния в localStorage

**Статус:** ⚠️ Требует починки (импорт закомментирован в `chat/+page.svelte`)

---

### 4.2. `src/lib/components/FileTreeNode.svelte` (НОВЫЙ ФАЙЛ)
**Назначение:** Рекурсивный компонент для дерева файлов

**Функционал:**
- Отображение папок и файлов с иконками
- Выделение выбранного файла
- Поддержка неограниченной вложенности

---

### 4.3. `SPLIT_VIEW_CHANGES.md` (НОВЫЙ ФАЙЛ)
**Назначение:** Документация по split-view изменениям (создано в этом чате)

---

### 5. `src/lib/components/ChatToolbar.svelte`
**Изменения:**
- Строки 246-267: Новая кнопка "Split View" с иконкой

**Функционал:** Переключение видимости split-view панели

---

### 6. `src/routes/settings/+page.svelte`
**Изменения:**
- Строки 1417-1445: Новая карточка "Default Permission Mode"

**Функционал:**
- Глобальная настройка режима разрешений для всех новых сессий
- 5 режимов: Ask, Auto Edit, Full Auto (Bypass), Plan, Don't Ask
- Сохранение в `~/.opencovibe/settings.json`

---

### 7. `messages/en.json` и `messages/zh-CN.json`
**Добавленные ключи:**

```json
// Permission Mode
"settings_general_permissionMode": "Default Permission Mode",
"settings_general_permissionModeDesc": "Default permission mode for new chat sessions (applies to all sessions)",
"settings_general_permissionModeAsk": "Ask (Default)",
"settings_general_permissionModeAutoEdit": "Auto Edit",
"settings_general_permissionModeFullAuto": "Full Auto (Bypass)",
"settings_general_permissionModePlan": "Plan (Read-only)",
"settings_general_permissionModeDontAsk": "Don't Ask (Deny)",

// Split View
"splitView_files": "Files",
"splitView_refresh": "Refresh file tree",
"splitView_selectFile": "Select a file to view",
"splitView_toggle": "Toggle split view",
"splitView_close": "Close split view",
```

---

## 🌿 Ветки Git

```
origin (dust6811/OpenCovibe)
├── master              ← основная ветка (отслеживает upstream)
└── custom-1m-context   ← ветка с изменениями (1M контекст + permission mode + split-view)

upstream (AnyiWang/OpenCovibe)
└── master              ← оригинальный репозиторий
```

---

## 📦 Коммиты

### Ветка `custom-1m-context`:
```
2ddfee3 feat: 1M context window for Opus 4.6/Sonnet 4.6
```

### Планируемые коммиты:
```
feat: Add global Default Permission Mode setting in General tab
feat: Add Split View panel for file browsing (WIP)
```

---

## 🔄 Стратегия обновлений

### При выходе новой версии upstream:

1. **Обновить master:**
   ```bash
   git checkout master
   git fetch upstream
   git rebase upstream/master
   git push origin master
   ```

2. **Обновить свою ветку:**
   ```bash
   git checkout custom-1m-context
   git rebase master
   # Разрешить конфликты слияния
   git push --force-with-lease origin custom-1m-context
   ```

3. **Пересобрать приложение:**
   ```bash
   npm run tauri build
   ```

---

## ✅ Тесты

### Пройденные тесты:

- ✅ 6 Rust тестов (model_context + claude_protocol)
- ✅ 261 frontend тестов (Vitest)
- ✅ Реальный тест API подтвердил 1M токенов работает
- ✅ Permission Mode переключается и сохраняется
- ✅ Split-view кнопка отображается (компонент требует доработки)

---

## 📝 Следующие шаги

### Приоритет 1 (критично):
- [ ] Починить SplitViewPanel.svelte (сейчас закомментирован)
- [ ] Создать PR для Permission Mode в upstream

### Приоритет 2 (желательно):
- [ ] Добавить сохранение режима для каждой сессии (не только глобально)
- [ ] Добавить tooltip с описанием режимов в настройках
- [ ] Обновить README с описанием изменений

### Приоритет 3 (опционально):
- [ ] Добавить больше моделей в model_context.rs
- [ ] Автоматическое обновление таблицы из API провайдеров

---

## 📞 Контакты

- **Fork:** https://github.com/dust6811/OpenCovibe
- **Оригинал:** https://github.com/AnyiWang/OpenCovibe
- **Автор изменений:** dust6811

---

*Последнее обновление: 2026-03-29*
