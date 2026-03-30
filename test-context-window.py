#!/usr/bin/env python3
"""
Тест реального размера контекстного окна Claude API.
Отправляет запросы с постепенно увеличивающимся контекстом,
пока не получит ошибку "prompt is too long" или "context window".

Использование:
    # Через pip
    pip install httpx
    export ANTHROPIC_API_KEY="your-key"
    python test-context-window.py

    # Или через uv (быстрее)
    uv run test-context-window.py
"""

import os
import httpx
import sys
from typing import Optional

# Конфигурация
API_BASE = os.environ.get("ANTHROPIC_API_BASE", "https://api.kiro.cheap/v1")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Модели для теста с ожидаемыми размерами
MODELS = {
    "claude-opus-4-6": 1_048_576,      # 1M (новый)
    "claude-sonnet-4-6": 1_048_576,    # 1M (новый)
    "claude-opus-4-5": 200_000,        # 200K
    "claude-sonnet-4-5": 200_000,      # 200K
}

def generate_text_tokens(n: int) -> str:
    """Генерирует текст длиной ~N токенов (1 токен ≈ 4 символа)."""
    base = "The quick brown fox jumps over the lazy dog. "
    chars_needed = n * 4
    repeats = chars_needed // len(base) + 1
    return (base * repeats)[:chars_needed]


def test_model_context(
    model: str,
    expected: int,
    start_tokens: int = 50000,
    step: int = 100000,
    fast_mode: bool = False
) -> Optional[int]:
    """
    Тестирует модель, увеличивая контекст пока не будет ошибка.

    Args:
        model: Название модели
        expected: Ожидаемый размер контекста (для информации)
        start_tokens: Начальный размер теста
        step: Шаг увеличения
        fast_mode: Если True, тестировать только до expected + 1 шаг

    Returns:
        Максимальный успешный размер контекста или None при ошибке
    """
    print(f"\n{'='*60}")
    print(f"Тестируем: {model}")
    print(f"Ожидаемый контекст: {expected:,} токенов")
    print(f"{'='*60}")

    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    tokens = start_tokens
    max_successful = 0
    last_input_tokens = 0

    # Определяем максимальный лимит теста
    max_limit = expected + step if fast_mode else 2_000_000

    while tokens <= max_limit:
        context_text = generate_text_tokens(tokens)

        payload = {
            "model": model,
            "max_tokens": 100,
            "messages": [
                {
                    "role": "user",
                    "content": f"Reply with exactly: OK\n\n{context_text}"
                }
            ]
        }

        try:
            response = httpx.post(
                f"{API_BASE}/messages",
                headers=headers,
                json=payload,
                timeout=180
            )

            if response.status_code == 200:
                data = response.json()
                input_tokens = data.get("usage", {}).get("input_tokens", tokens)
                last_input_tokens = input_tokens
                print(f"✓ {tokens:,} токенов — УСПЕХ (фактически input: {input_tokens:,})")
                max_successful = tokens
                tokens += step
            else:
                error = response.json()
                error_msg = str(error.get("error", {}).get("message", ""))
                print(f"✗ {tokens:,} токенов — ОШИБКА {response.status_code}: {error_msg[:150]}")

                if "too long" in error_msg.lower() or "context" in error_msg.lower() or "max_tokens" in error_msg.lower():
                    print(f"\n>>> Максимальный контекст для {model}: ~{max_successful:,} токенов")
                    if last_input_tokens:
                        print(f">>> Последний успешный input_tokens: {last_input_tokens:,}")
                    return max_successful
                else:
                    # Другая ошибка (auth, rate limit, model not found)
                    print(f"  Не контекстная ошибка — возможно модель недоступна")
                    return None

        except httpx.ReadTimeout:
            print(f"⏱ {tokens:,} токенов — Таймаут ответа (>180с)")
            # При больших контекстах это нормально — пробуем дальше
            max_successful = tokens
            tokens += step
        except Exception as e:
            print(f"✗ {tokens:,} токенов — ИСКЛЮЧЕНИЕ: {e}")
            return None

    print(f"\n>>> Тест завершён. Максимум: {max_successful:,} токенов")
    if last_input_tokens:
        print(f">>> Последний успешный input_tokens: {last_input_tokens:,}")
    return max_successful


def quick_check(model: str, expected: int) -> bool:
    """
    Быстрая проверка: отправляет запрос на ~80% от ожидаемого контекста.
    Возвращает True если успешно.
    """
    print(f"\n{'='*60}")
    print(f"Быстрая проверка: {model}")
    print(f"Ожидаемый контекст: {expected:,} токенов")
    print(f"Тестируем на: {int(expected * 0.8):,} токенов")
    print(f"{'='*60}")

    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    tokens = int(expected * 0.8)
    context_text = generate_text_tokens(tokens)

    payload = {
        "model": model,
        "max_tokens": 50,
        "messages": [
            {
                "role": "user",
                "content": f"Reply with exactly: OK\n\n{context_text}"
            }
        ]
    }

    try:
        response = httpx.post(
            f"{API_BASE}/messages",
            headers=headers,
            json=payload,
            timeout=300  # 5 минут для большого контекста
        )

        if response.status_code == 200:
            data = response.json()
            input_tokens = data.get("usage", {}).get("input_tokens", 0)
            print(f"✓ УСПЕХ: {tokens:,} токенов отправлено")
            print(f"  Фактически input_tokens: {input_tokens:,}")
            return True
        else:
            error = response.json()
            error_msg = str(error.get("error", {}).get("message", ""))
            print(f"✗ ОШИБКА: {error_msg[:150]}")
            return False

    except httpx.ReadTimeout:
        print(f"⏱ Таймаут (>5 мин) — возможно модель очень медленная")
        return None
    except Exception as e:
        print(f"✗ ИСКЛЮЧЕНИЕ: {e}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Тест контекстного окна Claude API")
    parser.add_argument(
        "--model", "-m",
        action="append",
        help="Тестировать только указанную модель (можно несколько)"
    )
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Быстрый режим: только 80% от ожидаемого контекста"
    )
    parser.add_argument(
        "--full", "-f",
        action="store_true",
        help="Полный режим: тестировать до 2M токенов"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Только показать список моделей для теста"
    )

    args = parser.parse_args()

    if not API_KEY:
        print("❌ Ошибка: не установлен ANTHROPIC_API_KEY")
        print("\nУстановите переменную окружения:")
        print("  export ANTHROPIC_API_KEY='your-api-key'")
        print("  # Или для Windows:")
        print("  set ANTHROPIC_API_KEY=your-api-key")
        sys.exit(1)

    if args.list:
        print("Модели для тестирования:")
        for model, expected in MODELS.items():
            print(f"  {model}: {expected:,} токенов (ожидаемый)")
        return

    # Фильтрация моделей
    if args.model:
        test_models = {m: MODELS[m] for m in args.model if m in MODELS}
        if not test_models:
            print(f"❌ Модель не найдена. Доступные: {list(MODELS.keys())}")
            sys.exit(1)
    else:
        test_models = MODELS

    print("Тест размера контекстного окна Claude API")
    print(f"API: {API_BASE}")
    print(f"Режим: {'быстрый' if args.quick else 'полный' if args.full else 'стандартный'}")

    results = {}

    for model, expected in test_models.items():
        if args.quick:
            success = quick_check(model, expected)
            results[model] = "✓" if success else "✗" if success is False else "⏱"
        else:
            max_ctx = test_model_context(
                model,
                expected,
                fast_mode=not args.full
            )
            if max_ctx:
                ratio = max_ctx / expected
                if ratio >= 0.95:
                    results[model] = f"✓ {max_ctx:,}"
                elif ratio >= 0.8:
                    results[model] = f"~ {max_ctx:,}"
                else:
                    results[model] = f"✗ {max_ctx:,}"
            else:
                results[model] = "✗ ошибка"

    # Итоговая таблица
    print(f"\n{'='*60}")
    print("РЕЗУЛЬТАТЫ")
    print(f"{'='*60}")
    for model, result in results.items():
        print(f"  {model}: {result}")


if __name__ == "__main__":
    main()
