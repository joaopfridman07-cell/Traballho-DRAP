import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3


def configurar_banco():
    conexao = sqlite3.connect("sistema_provas.db")
    cursor = conexao.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pergunta TEXT,
            op_a TEXT, op_b TEXT, op_c TEXT, op_d TEXT,
            resposta_correta TEXT
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_aluno TEXT,
            nota INTEGER
        )
    """)


    cursor.execute("SELECT COUNT(*) FROM questoes")
    if cursor.fetchone()[0] == 0:
        questoes_exemplo = [
            ("Qual é a capital do Brasil?", "São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "C"),
            ("Quanto é 2 + 2?", "3", "4", "5", "22", "B"),
            ("Qual a cor do céu limpo?", "Verde", "Vermelho", "Azul", "Amarelo", "C"),
            ("Quem descobriu o Brasil?", "Pedro Álvares Cabral", "Cristóvão Colombo", "Vasco da Gama", "Dom Pedro I", "A"),
            ("Qual é o maior planeta do sistema solar?", "Terra", "Marte", "Júpiter", "Saturno", "C")
        ]
        cursor.executemany("INSERT INTO questoes (pergunta, op_a, op_b, op_c, op_d, resposta_correta) VALUES (?, ?, ?, ?, ?, ?)", questoes_exemplo)
        conexao.commit()

    conexao.close()


respostas_aluno = []
gabarito = []

def iniciar_prova():
    nome = entry_nome.get().strip()
    if not nome:
        messagebox.showwarning("Aviso", "Digite o nome do aluno primeiro!")
        return


    for widget in frame_questoes.winfo_children():
        widget.destroy()

    respostas_aluno.clear()
    gabarito.clear()


    conexao = sqlite3.connect("sistema_provas.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM questoes ORDER BY RANDOM() LIMIT 3")
    questoes_sorteadas = cursor.fetchall()
    conexao.close()


    for i, q in enumerate(questoes_sorteadas):

        tk.Label(frame_questoes, text=f"{i+1}) {q[1]}", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))

        var_resposta = tk.StringVar(value="X")
        respostas_aluno.append(var_resposta)
        gabarito.append(q[6])

        tk.Radiobutton(frame_questoes, text=q[2], variable=var_resposta, value="A").pack(anchor="w")
        tk.Radiobutton(frame_questoes, text=q[3], variable=var_resposta, value="B").pack(anchor="w")
        tk.Radiobutton(frame_questoes, text=q[4], variable=var_resposta, value="C").pack(anchor="w")
        tk.Radiobutton(frame_questoes, text=q[5], variable=var_resposta, value="D").pack(anchor="w")

    btn_finalizar.pack(pady=10)

def finalizar_prova():
    nome = entry_nome.get().strip()
    nota = 0


    for i in range(3):
        if respostas_aluno[i].get() == gabarito[i]:
            nota += 1

    conexao = sqlite3.connect("sistema_provas.db")
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO notas (nome_aluno, nota) VALUES (?, ?)", (nome, nota))
    conexao.commit()
    conexao.close()

    messagebox.showinfo("Resultado", f"Prova finalizada!\nAluno: {nome}\nNota: {nota} de 3")

    entry_nome.delete(0, tk.END)
    for widget in frame_questoes.winfo_children():
        widget.destroy()
    btn_finalizar.pack_forget()

def exportar_txt():

    conexao = sqlite3.connect("sistema_provas.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT nome_aluno, nota FROM notas")
    todas_notas = cursor.fetchall()
    conexao.close()

    if not todas_notas:
        messagebox.showinfo("Aviso", "Nenhum aluno fez a prova ainda.")
        return

    caminho_arquivo = filedialog.asksaveasfilename(
        defaultextension=".txt",
        initialfile="notas_alunos.txt",
        title="Salvar Relatório de Notas",
        filetypes=[("Arquivo de Texto", "*.txt")]
    )

    if not caminho_arquivo:
        return

    try:
        with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write("--- RELATÓRIO DE NOTAS ---\n")
            for linha in todas_notas:
                arquivo.write(f"Aluno: {linha[0]} | Nota: {linha[1]}/3\n")

        messagebox.showinfo("Sucesso", f"Arquivo salvo com sucesso em:\n{caminho_arquivo}")
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível salvar o arquivo:\n{e}")


configurar_banco()

janela = tk.Tk()
janela.title("Sistema de Provas")
janela.geometry("500x650")


frame_topo = tk.Frame(janela)
frame_topo.pack(pady=10)

tk.Label(frame_topo, text="Nome do Aluno:").pack(side="left")
entry_nome = tk.Entry(frame_topo)
entry_nome.pack(side="left", padx=5)

tk.Button(frame_topo, text="Gerar Prova", command=iniciar_prova).pack(side="left")


frame_questoes = tk.Frame(janela)
frame_questoes.pack(fill="both", expand=True, padx=20)


btn_finalizar = tk.Button(janela, text="Finalizar Prova e Corrigir", command=finalizar_prova, bg="lightgreen")

tk.Button(janela, text="Exportar Notas para TXT", command=exportar_txt, bg="lightblue").pack(side="bottom", pady=20)

botao_sair = tk.Button(janela,text="Sair",bg="red",fg="white",width=10,command=janela.destroy)
botao_sair.pack(pady=20)

janela.mainloop()

