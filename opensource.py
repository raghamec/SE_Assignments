
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Local model location
MODEL_PATH = "./models/qwen-0.5b"

print("Loading Qwen model...")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH,
    local_files_only=True
)

# Load model on CPU
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float32,
    low_cpu_mem_usage=True,
    local_files_only=True
)

model.eval()

print("Qwen model loaded successfully!")

# Chat loop
while True:
    user_input = input("\nYou: Hi Hoe! How can I assist you today?\n> ")

    if user_input.lower() in ["exit", "quit", "stop"]:
        print("Exiting...")
        break

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": user_input}
    ]

    # Format conversation
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(prompt, return_tensors="pt")

    # Generate response
    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )

    # Extract only generated response
    generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]

    response = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    )

    print("\nQwen:", response)
