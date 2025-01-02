import openai
import pyperclip
import sys

# Set your API key
openai.api_key = 'sk-jlfEUEj_tr1lpYN3W5ZJcV4Ei1kLy8o4SGQo1HBZuAT3BlbkFJexbZEnhwyFFroFZmVAzM0SeGLWNx5xTXo35SySZSwA'

def fix_grammar(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Correct the grammar of the following text:\n\n{text}"}
            ],
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        error_message = f"Error in fix_grammar function: {str(e)}\n"
        with open("error_log.txt", "w") as f:
            f.write(error_message)
        print(error_message)
        return None

def improve_text(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Improve the following text to sound more professional and maintain a natural flow, without making it sound robotic:\n\n{text}"}
            ],
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        error_message = f"Error in improve_text function: {str(e)}\n"
        with open("error_log.txt", "w") as f:
            f.write(error_message)
        print(error_message)
        return None

def main(action):
    try:
        text = pyperclip.paste()
        if action == "fix_grammar":
            result_text = fix_grammar(text)
        elif action == "improve_text":
            result_text = improve_text(text)

        if result_text is not None:
            pyperclip.copy(result_text)
    except Exception as e:
        error_message = f"Error in main function: {str(e)}\n"
        with open("error_log.txt", "w") as f:
            f.write(error_message)
        print(error_message)

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "fix_grammar"
    main(action)
