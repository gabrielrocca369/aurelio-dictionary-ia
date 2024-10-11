# interface/interface_gui.py

import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, simpledialog, filedialog
import logging
import threading

class QAInterface:
    """Interface gráfica para o A.U.R.E.L.I.O."""

    def __init__(self, root, task_manager):
        """
        Inicializa a interface gráfica com os módulos necessários.

        Parâmetros:
        - root (tk.Tk): A janela principal do Tkinter.
        - task_manager (TaskManager): Instância do gerenciador de tarefas.
        """
        self.root = root
        self.task_manager = task_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        self.create_widgets()

    def create_widgets(self):
        """Cria os componentes da interface gráfica."""

        self.root.configure(bg='#1e1e1e')  # Define a cor de fundo da janela principal
        self.root.geometry("800x600")  # Define o tamanho inicial da janela
        self.root.resizable(False, False)  # Impede o redimensionamento da janela

        # Título
        self.title_label = tk.Label(
            self.root, 
            text="A.U.R.E.L.I.O. - Dicionário Multilíngue", 
            font=("Helvetica", 24, "bold"), 
            fg="#FFEB3B", 
            bg='#1e1e1e'
        )
        self.title_label.pack(pady=10)

        # Instrução
        self.instruction_label = tk.Label(
            self.root, 
            text="Digite uma palavra para obter sua definição e um exemplo de uso.", 
            font=("Helvetica", 14), 
            fg="white", 
            bg='#1e1e1e'
        )
        self.instruction_label.pack(pady=5)

        # Campo de entrada da palavra
        self.word_entry = tk.Entry(
            self.root, 
            font=("Helvetica", 14), 
            width=50, 
            bg="#333", 
            fg="white", 
            insertbackground="white"
        )
        self.word_entry.pack(pady=10)
        self.word_entry.bind('<Return>', lambda event: self.process_question())

        # Botões de ação
        self.buttons_frame = tk.Frame(self.root, bg='#1e1e1e')
        self.buttons_frame.pack(pady=10)

        # Botão para buscar definição
        self.ask_button = tk.Button(
            self.buttons_frame, 
            text="Buscar Definição", 
            font=("Helvetica", 14, "bold"), 
            bg="#4CAF50", 
            fg="white", 
            command=self.process_question
        )
        self.ask_button.grid(row=0, column=0, padx=10, pady=5)

        # Botão para ativar fala
        self.voice_button = tk.Button(
            self.buttons_frame, 
            text="🎤 Falar", 
            font=("Helvetica", 14), 
            bg="#FF5722", 
            fg="white", 
            command=self.start_voice_query
        )
        self.voice_button.grid(row=0, column=1, padx=10, pady=5)

        # Botão para adicionar nova palavra
        self.add_word_button = tk.Button(
            self.buttons_frame, 
            text="➕ Adicionar Palavra", 
            font=("Helvetica", 14), 
            bg="#2196F3", 
            fg="white", 
            command=self.add_new_word
        )
        self.add_word_button.grid(row=0, column=2, padx=10, pady=5)

        # Botão para exportar dicionário
        self.export_button = tk.Button(
            self.buttons_frame, 
            text="📤 Exportar Dicionário", 
            font=("Helvetica", 14), 
            bg="#9C27B0", 
            fg="white", 
            command=self.export_dictionary
        )
        self.export_button.grid(row=0, column=3, padx=10, pady=5)

        # Botão para importar dicionário
        self.import_button = tk.Button(
            self.buttons_frame, 
            text="📥 Importar Dicionário", 
            font=("Helvetica", 14), 
            bg="#FFC107", 
            fg="white", 
            command=self.import_dictionary
        )
        self.import_button.grid(row=0, column=4, padx=10, pady=5)

        # Dropdown para seleção de idioma
        self.language_label = tk.Label(
            self.root, 
            text="Idioma:", 
            font=("Helvetica", 14), 
            fg="white", 
            bg='#1e1e1e'
        )
        self.language_label.pack(pady=5)

        self.language_options = ["en", "pt", "es", "fr"]
        self.language_var = tk.StringVar(value="en")
        self.language_dropdown = ttk.Combobox(
            self.root, 
            textvariable=self.language_var, 
            values=self.language_options, 
            state="readonly",
            font=("Helvetica", 12)
        )
        self.language_dropdown.pack(pady=5)
        self.language_dropdown.bind("<<ComboboxSelected>>", self.change_language)

        # Área de resultados
        self.result_label = tk.Label(
            self.root, 
            text="Resultado:", 
            font=("Helvetica", 14), 
            fg="white", 
            bg='#1e1e1e'
        )
        self.result_label.pack(pady=5)

        self.result_text = scrolledtext.ScrolledText(
            self.root, 
            width=80, 
            height=15, 
            font=("Helvetica", 12), 
            bg="#333", 
            fg="white",
            wrap=tk.WORD,
            state='disabled'  # Inicialmente desativado para evitar edição
        )
        self.result_text.pack(pady=10)

        # Confiança
        self.confidence_label = tk.Label(
            self.root, 
            text="Confiança: N/A", 
            font=("Helvetica", 12, "bold"), 
            fg="#FFEB3B", 
            bg='#1e1e1e'
        )
        self.confidence_label.pack(pady=5)

    def process_question(self):
        """Processa a palavra inserida pelo usuário."""
        word = self.word_entry.get().strip()
        if not word:
            messagebox.showwarning("Aviso", "Por favor, insira uma palavra.")
            return

        language = self.language_var.get()
        self.logger.info(f"Buscando definição para a palavra: '{word}' no idioma: '{language}'")
        self.display_loading()

        # Iniciar processamento em uma thread separada para manter a interface responsiva
        threading.Thread(target=self.fetch_and_display, args=(word,), daemon=True).start()

    def fetch_and_display(self, word):
        """Busca a definição e atualiza a interface com o resultado."""
        language = self.language_var.get()
        try:
            result = self.task_manager.process_question(word)
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            if "error" in result:
                self.result_text.insert(tk.END, result['error'])
                self.confidence_label.config(text="Confiança: N/A")
            else:
                definition = result['definition']
                part_of_speech = result['part_of_speech']
                example = result['example']
                confidence = result['confidence']

                output = (
                    f"Definição: {definition}\n"
                    f"Classe Gramatical: {part_of_speech}\n"
                    f"Exemplo: {example}\n"
                )
                self.result_text.insert(tk.END, output)
                self.confidence_label.config(text=f"Confiança: {confidence:.2f}%")
                self.logger.info(f"Definição e exemplo exibidos para '{word}'.")
            self.result_text.config(state='disabled')
        except Exception as e:
            self.logger.error(f"Erro ao processar a palavra '{word}': {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro ao processar a palavra '{word}'. Por favor, tente novamente.")
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Ocorreu um erro ao processar a solicitação.")
            self.result_text.config(state='disabled')
            self.confidence_label.config(text="Confiança: N/A")
        finally:
            self.remove_loading()

    def display_loading(self):
        """Exibe uma mensagem de carregamento."""
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Buscando definição, por favor aguarde...")
        self.result_text.config(state='disabled')
        self.confidence_label.config(text="Confiança: N/A")

    def remove_loading(self):
        """Remove a mensagem de carregamento."""
        pass  # Pode ser implementado se necessário

    def add_new_word(self):
        """Abre uma janela para adicionar uma nova palavra."""
        language = self.language_var.get()
        word = simpledialog.askstring("Adicionar Palavra", "Digite a nova palavra:", parent=self.root)
        if not word:
            return

        word = word.strip().lower()
        if not word:
            messagebox.showwarning("Aviso", "A palavra não pode estar vazia.")
            return

        # Verifica se a palavra já existe
        existing = self.task_manager.dictionary_manager.get_definition(word, language)
        if existing:
            messagebox.showwarning("Aviso", f"A palavra '{word}' já existe no dicionário.")
            return

        # Tenta buscar definição automática
        confirm = messagebox.askyesno("Buscar Definição", f"Deseja buscar a definição de '{word}' automaticamente?")
        if confirm:
            self.logger.info(f"Buscando definição automática para '{word}'.")
            self.display_loading()

            # Iniciar busca em uma thread separada
            threading.Thread(target=self.fetch_and_add_word, args=(word, language), daemon=True).start()
        else:
            # Solicita definição manual
            self.open_manual_add_window(word, language)

    def fetch_and_add_word(self, word, language):
        """Busca a definição via API e adiciona a palavra ao dicionário."""
        try:
            success, message = self.task_manager.dictionary_manager.add_word(word, language)
            if success:
                messagebox.showinfo("Sucesso", message)
                self.logger.info(f"Palavra '{word}' adicionada com sucesso via API.")
            else:
                if "manualmente" in message:
                    # Solicita definição manual
                    self.logger.info(f"Definição automática não disponível para '{word}'. Solicitando entrada manual.")
                    self.open_manual_add_window(word, language)
                else:
                    messagebox.showerror("Erro", message)
                    self.logger.error(f"Erro ao adicionar palavra '{word}': {message}")
        except Exception as e:
            self.logger.error(f"Erro ao adicionar palavra '{word}': {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro ao adicionar a palavra '{word}'. Por favor, tente novamente.")
        finally:
            self.remove_loading()

    def open_manual_add_window(self, word, language):
        """Abre uma janela para entrada manual de definição, classe gramatical e exemplo."""
        add_window = tk.Toplevel(self.root)
        add_window.title(f"Adicionar Palavra: {word}")
        add_window.geometry("500x500")
        add_window.configure(bg='#1e1e1e')

        # Título da Janela
        tk.Label(
            add_window, 
            text=f"Adicionar '{word}' Manualmente", 
            font=("Helvetica", 16, "bold"), 
            fg="#FFEB3B", 
            bg='#1e1e1e'
        ).pack(pady=10)

        # Definição
        tk.Label(add_window, text="Definição:", font=("Helvetica", 12), fg="white", bg='#1e1e1e').pack(pady=5)
        definition_text = scrolledtext.ScrolledText(add_window, width=60, height=5, font=("Helvetica", 12))
        definition_text.pack(pady=5)

        # Classe Gramatical
        tk.Label(add_window, text="Classe Gramatical:", font=("Helvetica", 12), fg="white", bg='#1e1e1e').pack(pady=5)
        pos_entry = tk.Entry(add_window, width=30, font=("Helvetica", 12))
        pos_entry.pack(pady=5)

        # Exemplo
        tk.Label(add_window, text="Exemplo de Uso:", font=("Helvetica", 12), fg="white", bg='#1e1e1e').pack(pady=5)
        example_text = scrolledtext.ScrolledText(add_window, width=60, height=5, font=("Helvetica", 12))
        example_text.pack(pady=5)

        # Botão de Confirmação
        def confirm_add():
            definition = definition_text.get("1.0", tk.END).strip()
            part_of_speech = pos_entry.get().strip()
            example = example_text.get("1.0", tk.END).strip()

            if not (definition and part_of_speech and example):
                messagebox.showwarning("Aviso", "Todos os campos são obrigatórios.")
                return

            self.logger.info(f"Adicionando palavra '{word}' manualmente.")
            success, message = self.task_manager.dictionary_manager.manual_add_word(
                word=word,
                language=language,
                definition=definition,
                part_of_speech=part_of_speech,
                example=example
            )

            if success:
                messagebox.showinfo("Sucesso", message)
                self.logger.info(f"Palavra '{word}' adicionada com sucesso manualmente.")
                add_window.destroy()
                # Atualiza a interface para refletir a nova palavra
                self.process_question()
            else:
                messagebox.showerror("Erro", message)
                self.logger.error(f"Erro ao adicionar palavra '{word}' manualmente: {message}")

        confirm_button = tk.Button(
            add_window, 
            text="Confirmar Adição", 
            font=("Helvetica", 12, "bold"), 
            bg="#4CAF50", 
            fg="white", 
            command=confirm_add
        )
        confirm_button.pack(pady=20)

    def start_voice_query(self):
        """Inicia a consulta por voz em uma thread separada."""
        self.logger.info("Iniciando consulta por voz.")
        threading.Thread(target=self.voice_query, daemon=True).start()

    def voice_query(self):
        """Processa a consulta por voz."""
        try:
            self.logger.info("Esperando reconhecimento de fala...")
            self.task_manager.listen_and_respond()
            self.logger.info("Consulta por voz concluída.")
            # Opcional: Atualizar a interface após a resposta de voz
            # Dependendo da implementação de listen_and_respond, pode ser necessário obter o último resultado
        except Exception as e:
            self.logger.error(f"Erro na consulta por voz: {e}")
            messagebox.showerror("Erro", "Ocorreu um erro durante a consulta por voz.")

    def change_language(self, event):
        """Altera o idioma do sistema baseado na seleção do usuário."""
        selected_language = self.language_var.get()
        success = self.task_manager.set_language(selected_language)
        if success:
            self.logger.info(f"Idioma alterado para '{selected_language}'.")
            messagebox.showinfo("Idioma Alterado", f"Idioma alterado para '{selected_language.upper()}'.")
            # Limpa os campos após a alteração de idioma
            self.word_entry.delete(0, tk.END)
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            self.result_text.config(state='disabled')
            self.confidence_label.config(text="Confiança: N/A")
        else:
            self.logger.warning(f"Tentativa de alterar para idioma inexistente '{selected_language}'.")
            messagebox.showerror("Erro", f"O idioma '{selected_language}' não está disponível.")

    def export_dictionary(self):
        """Exporta o dicionário para um arquivo CSV."""
        language = self.language_var.get()
        # Abrir uma caixa de diálogo para selecionar o local e nome do arquivo CSV
        csv_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Exportar Dicionário para CSV"
        )
        if not csv_path:
            return  # O usuário cancelou a operação

        self.logger.info(f"Exportando dicionário para '{csv_path}' no idioma '{language}'.")
        success, message = self.task_manager.export_dictionary(language, csv_path)
        if success:
            messagebox.showinfo("Sucesso", message)
            self.logger.info(f"Dicionário exportado com sucesso para '{csv_path}'.")
        else:
            messagebox.showerror("Erro", message)
            self.logger.error("Falha ao exportar o dicionário.")

    def import_dictionary(self):
        """Importa palavras de um arquivo CSV para o dicionário."""
        language = self.language_var.get()
        # Abrir uma caixa de diálogo para selecionar o arquivo CSV
        csv_path = filedialog.askopenfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Importar Dicionário a partir de CSV"
        )
        if not csv_path:
            return  # O usuário cancelou a operação

        self.logger.info(f"Importando dicionário a partir de '{csv_path}' para o idioma '{language}'.")
        success, message = self.task_manager.import_dictionary(csv_path, language)
        if success:
            messagebox.showinfo("Sucesso", message)
            self.logger.info(f"Dicionário importado com sucesso a partir de '{csv_path}'.")
            # Atualiza a interface para refletir as novas palavras
            self.process_question()
        else:
            messagebox.showerror("Erro", message)
            self.logger.error(f"Falha ao importar dicionário a partir de '{csv_path}': {message}")

    def run(self):
        """Inicia a interface gráfica."""
        self.root.mainloop()
