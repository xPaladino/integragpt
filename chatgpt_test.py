from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('chatgpt_token')

client = OpenAI(api_key=api_key)

def pergunta_chatgpt(pergunta):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um assistente especializado em desenvolvimento Python e "
                                          "integrações com a API do GPT-4. Responda a perguntas sobre desenvolvimento de chatbots, "
                                          "APIs e automação, fornecendo respostas detalhadas e exemplos práticos."},
            {"role": "user", "content": pergunta}
        ],
        max_tokens=100,
        temperature=0.5
    )


    return response.choices[0].message.content.strip()

