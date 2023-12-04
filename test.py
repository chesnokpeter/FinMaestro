import openai

openai.api_key = "sk-or-vv-3677b56a5e03615c1b664481c9c37b42d8c101df676d6d11a509620d15fa1e7f" # ваш ключ в VseGPT после регистрации

openai.base_url = "https://api.vsegpt.ru:6070/v1/"

prompt = "привет"

messages = []
#messages.append({"role": "system", "content": system_text})
messages.append({"role": "user", "content": prompt})

response_big = openai.chat.completions.create(
    model="openai/gpt-3.5-turbo",
    messages=messages,
)

#print("Response BIG:",response_big)
response = response_big.choices[0].message.content
print("Response:",response)