from flask import Flask, render_template, request, jsonify
import json
import ollama

app = Flask(__name__)

with open("knowledge.json", "r", encoding="utf-8") as archivo:
    base_conocimiento = json.load(archivo)


def buscar_juego(pregunta):
    pregunta = pregunta.lower()

    for juego in base_conocimiento:
        nombre_juego = juego["juego"].lower()

        if nombre_juego in pregunta:
            return juego

        alternativas = juego.get("Alternativas_nombre", "")

        if isinstance(alternativas, list):
            for alias in alternativas:
                if alias.lower() in pregunta:
                    return juego

        elif isinstance(alternativas, str):
            alias_lista = alternativas.split(",")

            for alias in alias_lista:
                if alias.strip().lower() in pregunta:
                    return juego

    return None


def generar_respuesta(pregunta):
    juego_encontrado = buscar_juego(pregunta)

    if juego_encontrado is None:
        return "Esa información no está dentro de mi conocimiento, preguntame por otro juego o corrige tu pregunta."

    prompt = f"""
Eres un asistente experto en logros de videojuegos de Steam.

Tu objetivo es ayudar al usuario a saber:
- Que tan dificiles son los logros del juego
- Tiempo de completacion promedio para conseguir todos los logros
- Cuantos logros perdibles tiene
- Cantidad de partidas que se deben jugar para conseguir todos los logros
- Cuantos logros requieren farmeo
- Cuantos logros requieren jugar multijugador
- Cual es el logro mas raro
- y la ruta recomendada para conseguir todos los logros

Reglas importantes:

- Responde solamente usando la informacion entregada
- No copies la informacion del JSON
- No menciones nombres de campos del JSON
- No respondas como ficha tecnica
- No uses formatos como: "Logros perdibles: ", "Farmeo: ", "Tiempo: "
- No enumeres categorias
- Responde solo lo que te preguntan, a menos que te pregunten por el juego en general
- Asume que el usuario tiene conocimientos sobre gerga gamer
- No inventes datos
- Responde en español
- Se amigable con el usuario
- usa lenguaje gamer


Base de conocimiento del juego:
{json.dumps(juego_encontrado, indent=2, ensure_ascii=False)}

Pregunta del usuario:
{pregunta}
"""

    respuesta = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return respuesta["message"]["content"]


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    datos = request.get_json()
    pregunta = datos.get("pregunta", "")

    if pregunta.strip() == "":
        return jsonify({"respuesta": "Por favor, escribe una pregunta."})

    respuesta = generar_respuesta(pregunta)
    return jsonify({"respuesta": respuesta})


if __name__ == "__main__":
    app.run(debug=True)