# Руководство по обновлению из upstream (AnyiWang/OpenCovibe)

Это руководство описывает процесс получения обновлений от оригинального разработчика и применения своих изменений.

---

## 📋 Предварительные требования

Убедись, что настроены remote-репозитории:

```bash
cd C:\Users\user\Projects\OpenCovibe

# Проверка текущих remote
git remote -v

# Должно быть:
# origin    https://github.com/dust6811/OpenCovibe.git (fetch)
# origin    https://github.com/dust6811/OpenCovibe.git (push)
# upstream  https://github.com/AnyiWang/OpenCovibe.git (fetch)
# upstream  https://github.com/AnyiWang/OpenCovibe.git (push)
```

Если `upstream` нет — добавь:

```bash
git remote add upstream https://github.com/AnyiWang/OpenCovibe.git
```

---

## 🔄 Процесс обновления (по шагам)

### Шаг 1: Проверить наличие обновлений

```bash
git fetch upstream
git log HEAD..upstream/master --oneline
```

Если вывод пустой — обновлений нет.

---

### Шаг 2: Обновить master

```bash
# Переключись на master
git checkout master

# Влей изменения из upstream
git merge upstream/master

# Или через rebase (чище история, но требует force push)
# git rebase upstream/master

# Отправь в свой fork
git push origin master
```

---

### Шаг 3: Обновить свою ветку с изменениями

```bash
# Переключись на свою ветку
git checkout custom-1m-context

# Обнови из master
git rebase master
```

**Если возникли конфликты:**

1. Git покажет conflicted файлы
2. Открой каждый файл, найди маркеры конфликтов:
   ```
   <<<<<<< HEAD
   (твои изменения)
   =======
   (изменения из upstream)
   >>>>>>> master
   ```
3. Выбери нужные строки, удали маркеры
4. Добавь исправленные файлы:
   ```bash
   git add <файл>
   ```
5. Продолжи rebase:
   ```bash
   git rebase --continue
   ```
6. Повторяй, пока не закончатся конфликты

---

### Шаг 4: Проверка после rebase

```bash
# Проверь статус
git status

# Посмотри историю
git log --oneline -5

# Запусти тесты
npm test

# Попробуй собрать
npm run tauri build
```

---

### Шаг 5: Отправь обновления в fork

```bash
# После успешного rebase
git push --force-with-lease origin custom-1m-context
```

**Важно:** `--force-with-lease` безопаснее, чем `--force` — он отменит операцию, если кто-то ещё пушил в ветку.

---

## 🚨 Решение проблем

### Конфликт в `src-tauri/src/agent/claude_protocol.rs`

Этот файл часто меняется в upstream. Если конфликт в области `context_window`:

**Решение:** Сохрани нашу логику с `model_context::get_context_window()`, но обнови номера строк.

---

### Конфликт в `src/routes/settings/+page.svelte`

Если upstream добавил новые настройки в General tab:

**Решение:** Перемести нашу карточку "Permission Mode" ниже новых элементов, сохранив структуру.

---

### Ошибка компиляции Rust

После rebase может потребоваться обновить зависимости:

```bash
cd src-tauri
cargo update
cargo check
```

---

### Сломался frontend

Очисти кэш и пересобери:

```bash
rm -rf .svelte-kit
npm run build
```

---

## 📅 Рекомендуемый график обновлений

| Тип обновления | Когда обновляться |
|----------------|-------------------|
| **Patch** (v0.1.46 → v0.1.47) | В течение недели |
| **Minor** (v0.1.46 → v0.2.0) | После чтения release notes |
| **Major** (v0.1.46 → v1.0.0) | Через 1-2 недели (пусть другие протестируют) |

---

## 🔍 Мониторинг обновлений

### Вариант 1: GitHub Watch

1. Зайди на https://github.com/AnyiWang/OpenCovibe
2. Кнопка "Watch" → "Releases only"
3. Получай email при новых релизах

### Вариант 2: Скрипт проверки

Создай `check-updates.sh`:

```bash
#!/bin/bash
cd /c/Users/user/Projects/OpenCovibe
git fetch upstream
LOCAL=$(git rev-parse master)
REMOTE=$(git rev-parse upstream/master)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "⚠️  Доступны обновления!"
    git log --oneline HEAD..upstream/master
else
    echo "✅ Актуальная версия"
fi
```

Запускай раз в неделю.

---

## 📊 Стратегия слияния изменений

### Что мерджить сразу:

- ✅ Исправления безопасности
- ✅ Критические багфиксы
- ✅ Совместимость с новыми версиями CLI

### Что тестировать перед слиянием:

- ⚠️ Новые функции UI
- ⚠️ Изменения архитектуры
- ⚠️ Обновления зависимостей

### Что можно отложить:

- ⏸️ Косметические изменения
- ⏸️ Рефакторинг без функциональных изменений

---

## 🧪 Тестирование после обновления

### Быстрый чеклист:

1. **Сборка:**
   ```bash
   npm run tauri build
   ```

2. **Запуск:**
   - Приложение запускается
   - Нет ошибок в консоли

3. **Наши функции:**
   - Settings → General → Permission Mode (виден и работает)
   - Чат создаётся без ошибок
   - Split-view кнопка на тулбаре (даже если не работает)

4. **Основные функции:**
   - Отправка сообщений работает
   - Файлы читаются/создаются
   - Настройки сохраняются

---

## 📞 Если всё сломалось

### Откат к рабочей версии:

```bash
# Найди последний рабочий коммит
git log --oneline

# Откатись на него
git checkout <commit-hash>

# Или создай новую ветку от рабочей точки
git checkout -b backup-working <commit-hash>
```

### Запрос помощи:

1. Открой issue в upstream репозитории
2. Приложи вывод:
   ```bash
   git status
   git log --oneline -5
   npm run tauri build 2>&1 | tail -50
   ```

---

## 📚 Дополнительные ресурсы

- [Git Rebase vs Merge](https://www.atlassian.com/git/tutorials/merging-vs-rebasing)
- [Resolving Merge Conflicts](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts)
- [Tauri Build Documentation](https://v2.tauri.app/start/prerequisites/)

---

*Последнее обновление: 2026-03-29*
