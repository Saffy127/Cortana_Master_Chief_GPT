import threading
import os
import openai
from openai import OpenAI
from flask import Flask, request, jsonify, send_from_directory
import time

app = Flask(__name__, static_folder='static')
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

assistant_1_params = {
    'name': "Master Chief",
    'instructions':
    "You are Master Chief from the Halo series. Speak in his manner.",
    'tools': [{
        "type": "code_interpreter"
    }],
    'model': "gpt-3.5-turbo-1106"
}

assistant_2_params = {
    'name': "Cortana",
    'instructions':
    "You are the AI Cortana from the Halo series. Speak in her manner.",
    'tools': [{
        "type": "code_interpreter"
    }],
    'model': "gpt-3.5-turbo-1106"
}


@app.route('/')
def index():
  return send_from_directory('static', 'index.html')


@app.route('/start_conversation', methods=['POST'])
def start_conversation():
  data = request.json
  topic = data.get('topic', 'Default Topic')
  message_count = data.get('message_count', 5)
  conversation_output = []

  conversation_thread = threading.Thread(
      target=converse,
      args=(assistant_1_params, assistant_2_params, topic, message_count,
            conversation_output))
  conversation_thread.start()
  conversation_thread.join()

  return jsonify({"conversation": conversation_output})


def get_last_assistant_message(thread_id):
  messages_response = client.beta.threads.messages.list(thread_id=thread_id)
  messages = messages_response.data

  for message in messages:
    if message.role == 'assistant':
      assistant_message_content = " ".join(content.text.value
                                           for content in message.content
                                           if hasattr(content, 'text'))
      return assistant_message_content.strip()
  return ""


def converse(assistant_1_params, assistant_2_params, topic, message_count,
             conversation_output):
  assistant_1 = client.beta.assistants.create(**assistant_1_params)
  assistant_2 = client.beta.assistants.create(**assistant_2_params)
  thread_1 = client.beta.threads.create()
  thread_2 = client.beta.threads.create()

  def assistant_conversation(start_message, assistant_a, thread_a, assistant_b,
                             thread_b, msg_limit):
    message_content = start_message

    for i in range(msg_limit):
      user_message = client.beta.threads.messages.create(
          thread_id=thread_a.id, role="user", content=message_content)
      run = client.beta.threads.runs.create(thread_id=thread_a.id,
                                            assistant_id=assistant_a.id)

      while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_a.id,
                                                       run_id=run.id)
        if run_status.status == 'completed':
          break
        time.sleep(1)

      message_content = get_last_assistant_message(thread_a.id)
      conversation_output.append(message_content)

      assistant_a, assistant_b = assistant_b, assistant_a
      thread_a, thread_b = thread_b, thread_a

  start_message = f"Respond with a starting line to discuss {topic}?"
  conversation_thread = threading.Thread(target=assistant_conversation,
                                         args=(start_message, assistant_1,
                                               thread_1, assistant_2, thread_2,
                                               message_count))
  conversation_thread.start()
  conversation_thread.join()


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
