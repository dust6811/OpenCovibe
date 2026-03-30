/// Model context window sizes (in tokens).
///
/// This provides fallback values when the CLI doesn't transmit context_window
/// in usage_update events.
///
/// Sources: Anthropic documentation, API specifications.

/// Get the context window size for a model.
/// Returns None if the model is unknown.
pub fn get_context_window(model: &str) -> Option<u64> {
    // ── Claude Opus 4.6 / Sonnet 4.6 — 1M context ──
    if model.contains("opus-4-6")
        || model.contains("opus-4.6")
        || model.contains("sonnet-4-6")
        || model.contains("sonnet-4.6")
    {
        return Some(1_048_576); // 1 million tokens
    }

    // ── Claude Opus 4.5 / Sonnet 4.5 — 200K context ──
    if model.contains("opus-4-5")
        || model.contains("opus-4.5")
        || model.contains("sonnet-4-5")
        || model.contains("sonnet-4.5")
    {
        return Some(200_000);
    }

    // ── Legacy Claude models ──
    if model.contains("opus-4-1") || model.contains("opus-4.1") {
        return Some(200_000);
    }
    if model.contains("opus-4") {
        return Some(200_000);
    }
    if model.contains("sonnet-3-7") || model.contains("sonnet-3.7") {
        return Some(200_000);
    }
    if model.contains("sonnet-3-5") || model.contains("sonnet-3.5") {
        return Some(200_000);
    }
    if model.contains("sonnet-3") {
        return Some(200_000);
    }
    if model.contains("haiku-3-5") || model.contains("haiku-3.5") {
        return Some(200_000);
    }
    if model.contains("haiku-3") {
        return Some(200_000);
    }

    // ── Third-party provider models ──
    // DeepSeek V3 / V3.2
    if model.contains("deepseek-chat") || model.contains("deepseek-v3") {
        return Some(128_000);
    }
    // DeepSeek V3.2 (some variants have 256K)
    if model.contains("deepseek-v3.2") || model.contains("deepseek-v3-2") {
        return Some(256_000);
    }

    // Kimi / Moonshot
    if model.contains("kimi-k2.5") || model.contains("kimi-k25") {
        return Some(256_000);
    }
    if model.contains("kimi") {
        return Some(128_000);
    }

    // Zhipu GLM
    if model.contains("glm-4.5") || model.contains("glm-4-5") {
        return Some(128_000);
    }
    if model.contains("glm-4.7") || model.contains("glm-4-7") {
        return Some(256_000);
    }
    if model.contains("glm") {
        return Some(128_000);
    }

    // Qwen / Bailian
    if model.contains("qwen3-max") || model.contains("qwen-3-max") {
        return Some(256_000);
    }
    if model.contains("qwen3.5") || model.contains("qwen-3.5") {
        return Some(256_000);
    }
    if model.contains("qwen") {
        return Some(128_000);
    }

    // DouBao / Volcengine
    if model.contains("doubao") {
        return Some(128_000);
    }

    // MiniMax
    if model.contains("minimax-m2.5") || model.contains("minimax-m2-5") {
        return Some(256_000);
    }
    if model.contains("minimax") {
        return Some(128_000);
    }

    // MiMo / Xiaomi
    if model.contains("mimo") {
        return Some(256_000);
    }

    // ── OpenAI models ──
    if model.contains("gpt-4o") {
        return Some(128_000);
    }
    if model.contains("gpt-4-turbo") || model.contains("gpt-4-turbo-preview") {
        return Some(128_000);
    }
    if model.contains("gpt-4") {
        return Some(128_000);
    }
    if model.contains("o1") {
        return Some(200_000);
    }
    if model.contains("o3") {
        return Some(200_000);
    }

    // Unknown model
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_opus_4_6_context() {
        assert_eq!(get_context_window("claude-opus-4-6"), Some(1_048_576));
        assert_eq!(get_context_window("claude-opus-4.6"), Some(1_048_576));
    }

    #[test]
    fn test_sonnet_4_6_context() {
        assert_eq!(get_context_window("claude-sonnet-4-6"), Some(1_048_576));
        assert_eq!(get_context_window("claude-sonnet-4.6"), Some(1_048_576));
    }

    #[test]
    fn test_opus_4_5_context() {
        assert_eq!(get_context_window("claude-opus-4-5"), Some(200_000));
        assert_eq!(get_context_window("claude-opus-4.5"), Some(200_000));
    }

    #[test]
    fn test_unknown_model() {
        assert_eq!(get_context_window("unknown-model"), None);
    }
}
