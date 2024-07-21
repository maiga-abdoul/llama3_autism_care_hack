

client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))

response = client.chat.completions.create(
    model="meta-llama/Llama-3-8b-chat-hf",
    messages=[],
    max_tokens=512,
    temperature=0.7,
    top_p=0.7,
    top_k=50,
    repetition_penalty=1,
    stop=["<|eot_id|>"],
    stream=True
)
print(response.choices[0].message.content)