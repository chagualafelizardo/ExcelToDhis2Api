from flask import Flask, render_template, request, redirect, flash
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Diretório onde os arquivos serão salvos (mesmo que seu script DHIS2)
UPLOAD_FOLDER = "/app/data"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'xls', 'xlsx', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'file' not in request.files:
            flash("Nenhum arquivo selecionado")
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash("Nenhum arquivo selecionado")
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            flash(f"Arquivo {file.filename} carregado com sucesso!")
            return redirect(request.url)
        else:
            flash("Formato de arquivo não permitido!")
            return redirect(request.url)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
