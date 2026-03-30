/// Provides context window sizes for known models.
/// Returns 1M tokens for Claude Opus 4.6/Sonnet 4.6.
/// Used as fallback when CLI doesn't provide context_window.

/// Get context window size for a model name.
/// Uses pattern matching for universal coverage of Claude models.
pub fn get_context_window(model_name: &str) -> Option<u64> {
    let model_lower = model_name.to_lowercase();

    // ── Pattern-based matching for Claude models (universal coverage) ──

    // Claude 4.6 models - 1M context
    if model_lower.contains("opus-4-6") || model_lower.contains("opus-4.6") ||
       model_lower.contains("sonnet-4-6") || model_lower.contains("sonnet-4.6") {
        return Some(1_048_576);
    }

    // Claude 4.5 models - 200K context
    if model_lower.contains("opus-4-5") || model_lower.contains("opus-4.5") ||
       model_lower.contains("sonnet-4-5") || model_lower.contains("sonnet-4.5") ||
       model_lower.contains("haiku-4-5") || model_lower.contains("haiku-4.5") {
        return Some(200_000);
    }

    // Claude 4.x models (generic fallback) - 200K context
    if model_lower.contains("claude") && model_lower.contains("opus-4") {
        return Some(200_000);
    }
    if model_lower.contains("claude") && model_lower.contains("sonnet-4") {
        return Some(200_000);
    }

    // Claude 3.7 models - 200K context
    if model_lower.contains("claude") && model_lower.contains("3-7") {
        return Some(200_000);
    }

    // Claude 3.5 models - 200K context
    if model_lower.contains("claude") && model_lower.contains("3-5") {
        return Some(200_000);
    }

    // Claude 3.x models - 200K context
    if model_lower.contains("claude-3-opus") ||
       model_lower.contains("claude-3-sonnet") ||
       model_lower.contains("claude-3-haiku") {
        return Some(200_000);
    }

    // Legacy Claude (opus/sonnet/haiku without version) - 200K context
    if model_lower.contains("claude-opus") ||
       model_lower.contains("claude-sonnet") ||
       model_lower.contains("claude-haiku") {
        return Some(200_000);
    }

    // ── Third-party models (pattern matching) ──

    // DeepSeek
    if model_lower.contains("deepseek-v3.2") || model_lower.contains("deepseek-v3-2") {
        return Some(256_000);
    }
    if model_lower.contains("deepseek") {
        return Some(128_000);
    }

    // Kimi / Moonshot
    if model_lower.contains("kimi-k2") || model_lower.contains("kimi-k2.5") {
        return Some(256_000);
    }
    if model_lower.contains("kimi") {
        return Some(128_000);
    }

    // Qwen
    if model_lower.contains("qwen-max") || model_lower.contains("qwen2.5") {
        return Some(256_000);
    }
    if model_lower.contains("qwen") {
        return Some(128_000);
    }

    // GLM / Zhipu
    if model_lower.contains("glm-4.5") || model_lower.contains("glm-4-5") {
        return Some(256_000);
    }
    if model_lower.contains("glm") {
        return Some(128_000);
    }

    // MiniMax
    if model_lower.contains("minimax-m2") || model_lower.contains("minimax-m2.5") {
        return Some(256_000);
    }
    if model_lower.contains("minimax") {
        return Some(128_000);
    }

    // MiMo / Xiaomi
    if model_lower.contains("mimo") {
        return Some(256_000);
    }

    // OpenAI
    if model_lower.contains("o1") || model_lower.contains("o3") {
        return Some(200_000);
    }
    if model_lower.contains("gpt-4") {
        return Some(128_000);
    }

    // Unknown model - return None
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    // ── Claude 4.6 models (1M) ──

    #[test]
    fn test_opus_4_6_context() {
        assert_eq!(get_context_window("claude-opus-4-6"), Some(1_048_576));
        assert_eq!(get_context_window("claude-opus-4-6-20250601"), Some(1_048_576));
        assert_eq!(get_context_window("claude-opus-4.6"), Some(1_048_576));
    }

    #[test]
    fn test_sonnet_4_6_context() {
        assert_eq!(get_context_window("claude-sonnet-4-6"), Some(1_048_576));
        assert_eq!(get_context_window("claude-sonnet-4-6-20250601"), Some(1_048_576));
        assert_eq!(get_context_window("claude-sonnet-4.6"), Some(1_048_576));
    }

    // ── Claude 4.5 models (200K) ──

    #[test]
    fn test_opus_4_5_context() {
        assert_eq!(get_context_window("claude-opus-4-5"), Some(200_000));
        assert_eq!(get_context_window("claude-opus-4.5"), Some(200_000));
    }

    #[test]
    fn test_sonnet_4_5_context() {
        assert_eq!(get_context_window("claude-sonnet-4-5"), Some(200_000));
        assert_eq!(get_context_window("claude-sonnet-4.5"), Some(200_000));
    }

    #[test]
    fn test_haiku_4_5_context() {
        assert_eq!(get_context_window("claude-haiku-4-5"), Some(200_000));
    }

    // ── Claude 3.x models (200K) ──

    #[test]
    fn test_3_7_sonnet_context() {
        assert_eq!(get_context_window("claude-3-7-sonnet-20250219"), Some(200_000));
        assert_eq!(get_context_window("claude-3-7-sonnet"), Some(200_000));
    }

    #[test]
    fn test_3_5_sonnet_context() {
        assert_eq!(get_context_window("claude-3-5-sonnet-20241022"), Some(200_000));
        assert_eq!(get_context_window("claude-3-5-sonnet"), Some(200_000));
    }

    #[test]
    fn test_3_opus_context() {
        assert_eq!(get_context_window("claude-3-opus-20240229"), Some(200_000));
        assert_eq!(get_context_window("claude-3-opus"), Some(200_000));
    }

    // ── Third-party models ──

    #[test]
    fn test_deepseek_context() {
        assert_eq!(get_context_window("deepseek-chat"), Some(128_000));
        assert_eq!(get_context_window("deepseek-v3"), Some(128_000));
        assert_eq!(get_context_window("deepseek-v3.2"), Some(256_000));
    }

    #[test]
    fn test_openai_context() {
        assert_eq!(get_context_window("gpt-4o"), Some(128_000));
        assert_eq!(get_context_window("o1"), Some(200_000));
    }

    // ── Unknown models ──

    #[test]
    fn test_unknown_model() {
        assert_eq!(get_context_window("unknown-model"), None);
    }

    // ── Integration tests ──

    #[test]
    fn test_all_claude_4_6_models_have_1m() {
        let models_1m = vec![
            "claude-opus-4-6",
            "claude-opus-4-6-20250601",
            "claude-opus-4.6",
            "claude-sonnet-4-6",
            "claude-sonnet-4-6-20250601",
            "claude-sonnet-4.6",
        ];
        for model in models_1m {
            assert_eq!(get_context_window(model), Some(1_048_576), "{} should have 1M", model);
        }
    }

    #[test]
    fn test_all_claude_4_5_models_have_200k() {
        let models_200k = vec![
            "claude-opus-4-5",
            "claude-opus-4.5",
            "claude-sonnet-4-5",
            "claude-sonnet-4.5",
            "claude-haiku-4-5",
            "claude-3-5-sonnet",
            "claude-3-opus",
        ];
        for model in models_200k {
            assert_eq!(get_context_window(model), Some(200_000), "{} should have 200K", model);
        }
    }

    #[test]
    fn test_universal_claude_pattern_matching() {
        // Test that any Claude model with version gets 200K by default
        assert_eq!(get_context_window("claude-opus-4-1"), Some(200_000));
        assert_eq!(get_context_window("claude-sonnet-4-2"), Some(200_000));
        assert_eq!(get_context_window("claude-3-haiku-20240307"), Some(200_000));
    }
}
