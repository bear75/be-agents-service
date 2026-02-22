#!/bin/bash
# Wrapper to run ollama serve with OLLAMA_LLM_LIBRARY=cpu_avx2
# Fixes MLX dynamic library error on macOS 26+
export OLLAMA_LLM_LIBRARY=cpu_avx2
exec /opt/homebrew/bin/ollama serve "$@"
