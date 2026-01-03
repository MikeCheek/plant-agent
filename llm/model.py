from smolagents import ChatMessage
from llama_cpp import Llama
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR.endswith("llm"):
  path_prefix = ""
else:
  path_prefix = "llm/"

model_path = os.path.join(CURRENT_DIR, path_prefix, "qwen2.5-7b-instruct-q2_k.gguf")

llm = Llama(
    model_path=model_path, 
    n_ctx=4096,           # 1. Reduced context = much less RAM
    n_gpu_layers=-1,      # Offload everything to GPU if available
    n_batch=512,          # Standard batch size for prompt processing
    n_threads=max(1, os.cpu_count() // 2), # 2. Use physical cores only
    use_mmap=True,        # 3. Use memory mapping to load faster
    logits_all=False,     # 4. Set to False unless you're doing logit analysis
    verbose=False,         # 5. Disable logs to keep console clean
    n_keep=200,
    flash_attn=True,      # Add this
    f16_kv=True           # Add this
)

class LocalGGUFModel:
    def __init__(self, llama_instance):
        self.llm = llama_instance

    def __call__(self, messages, stop_sequences=None):
        return self.generate(messages, stop_sequences)

    def generate(self, messages, stop_sequences=None):
        prompt = ""
        for msg in messages:
            role = msg.role.upper()
            if isinstance(msg.content, list):
                content = "".join([item.get("text", "") if isinstance(item, dict) else str(item) for item in msg.content])
            else:
                content = msg.content
            prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"
        
        prompt += "<|im_start|>ASSISTANT\n"

        stops = ["<|im_end|>", "Observation:", "<|im_start|>", "```\n"]
        if stop_sequences:
            stops.extend(stop_sequences)

        response = self.llm(
            prompt,
            max_tokens=1024,
            stop=stops,
            echo=False,
            temperature=0.7
        )
        
        result = response["choices"][0]["text"]
        return ChatMessage(role="assistant", content=result)

      