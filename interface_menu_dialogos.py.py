import tkinter as tk
from tkinter import messagebox, simpledialog

# Importa as classes do modelo_abstrato.py
from modelo_abstrato import ClienteConcreto, ProcessoConcreto, PagamentoConcreto, AudienciaConcreta

# --- CLASSE BaseDialog E SUAS SUBCLASSES (INSERIDAS DIRETAMENTE AQUI) ---
class BaseDialog(tk.Toplevel):
    def __init__(self, parent, title, fields):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set() # Torna o diálogo modal
        self.title(title)
        self.result = None
        self.entries = {} # Dicionário para armazenar as Entry widgets

        self.body_frame = tk.Frame(self)
        self.body_frame.pack(padx=10, pady=10)

        self.setup_fields(fields)
        self.setup_buttons()

        self.parent = parent
        self.bind("<Return>", self._on_ok) # Permite usar Enter para OK
        self.protocol("WM_DELETE_WINDOW", self._on_cancel) # Fecha corretamente ao clicar X

        self.geometry(f"+{parent.winfo_x() + 50}+{parent.winfo_y() + 50}") # Posiciona o diálogo perto da janela pai

    def setup_fields(self, fields):
        # 'fields' é uma lista de tuplas (label_text, key_name, default_value, input_type)
        # Adicionei entries_labels aqui para mensagens de erro mais claras
        self.entries_labels = {f[1]: f[0] for f in fields}
        for i, (label_text, key_name, default_value, input_type) in enumerate(fields):
            tk.Label(self.body_frame, text=label_text + ":").grid(row=i, column=0, sticky="w", pady=2, padx=5)
            entry = tk.Entry(self.body_frame, width=40)
            entry.grid(row=i, column=1, pady=2, padx=5)
            entry.insert(0, default_value) # Preenche valor padrão

            self.entries[key_name] = {"widget": entry, "type": input_type}
        
        if self.entries:
            self.entries[fields[0][1]]["widget"].focus_set() # Foco no primeiro campo

    def setup_buttons(self):
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="OK", command=self._on_ok, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancelar", command=self._on_cancel, width=10).pack(side=tk.LEFT, padx=5)

    def _on_ok(self, event=None):
        values = {}
        for key_name, data in self.entries.items():
            value_str = data["widget"].get()
            input_type = data["type"]

            if not value_str and input_type != "optional": # Considera 'optional' como permitido ser vazio
                messagebox.showwarning("Erro de Entrada", f"O campo '{self.entries_labels.get(key_name, key_name)}' é obrigatório.")
                return

            if input_type == "int":
                try:
                    values[key_name] = int(value_str)
                    if values[key_name] <= 0:
                         messagebox.showwarning("Erro de Entrada", f"'{self.entries_labels.get(key_name, key_name)}' deve ser um número inteiro positivo.")
                         return
                except ValueError:
                    messagebox.showwarning("Erro de Entrada", f"O campo '{self.entries_labels.get(key_name, key_name)}' deve ser um número inteiro.")
                    return
            elif input_type == "float":
                try:
                    values[key_name] = float(value_str)
                    if values[key_name] <= 0:
                         messagebox.showwarning("Erro de Entrada", f"'{self.entries_labels.get(key_name, key_name)}' deve ser um número positivo.")
                         return
                except ValueError:
                    messagebox.showwarning("Erro de Entrada", f"O campo '{self.entries_labels.get(key_name, key_name)}' deve ser um número decimal válido.")
                    return
            else: # String
                values[key_name] = value_str
        
        self.result = values
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()

    def show(self):
        self.parent.wait_window(self)
        return self.result

class ClienteDialog(BaseDialog):
    def __init__(self, parent):
        fields = [
            ("Nome", "nome", "", "str"),
            ("CPF", "cpf", "", "str"),
            ("Idade", "idade", "", "int"),
            ("Telefone", "telefone", "", "str"),
            ("Endereço", "endereco", "", "str"),
            ("Email", "email", "", "str")
        ]
        self.entries_labels = {f[1]: f[0] for f in fields}
        super().__init__(parent, "Adicionar Cliente", fields)

class ProcessoDialog(BaseDialog):
    def __init__(self, parent):
        fields = [
            ("Número do Processo", "numero", "", "str"),
            ("Descrição", "descricao", "", "str"),
            ("CPF do Cliente", "cliente_cpf", "", "str")
        ]
        self.entries_labels = {f[1]: f[0] for f in fields}
        super().__init__(parent, "Adicionar Processo", fields)

class PagamentoDialog(BaseDialog):
    def __init__(self, parent):
        fields = [
            ("CPF do Cliente", "cliente_cpf", "", "str"),
            ("Valor", "valor", "", "float"),
            ("Descrição", "descricao", "", "str")
        ]
        self.entries_labels = {f[1]: f[0] for f in fields}
        super().__init__(parent, "Registrar Pagamento", fields)

class AudienciaDialog(BaseDialog):
    def __init__(self, parent):
        fields = [
            ("Número do Processo", "processo_numero", "", "str"),
            ("CPF do Cliente", "cliente_cpf", "", "str"),
            ("Data e Hora (DD/MM/AAAA HH:MM)", "data_hora", "", "str"),
            ("Local", "local", "", "str"),
            ("Tipo", "tipo", "", "str")
        ]
        self.entries_labels = {f[1]: f[0] for f in fields}
        super().__init__(parent, "Agendar Audiência", fields)

# --- FIM DAS CLASSES DE DIÁLOGO ---

class SistemaJuridicoAcaoGUI:
    def __init__(self, master):
        self.master = master
        master.title("Sistema Jurídico - Ação Rápida")
        master.geometry("450x300") 

        # ESTES SÃO OS ARMAZENAMENTOS DE DADOS ONDE OS OBJETOS SÃO SALVOS.
        # Eles precisam ser acessados corretamente para que a busca funcione.
        self.data_stores = {
            "clientes": {},  # CPF como chave
            "processos": {}, # Numero como chave
            "pagamentos": [],
            "audiencias": []
        }

        self.setup_ui()

    def setup_ui(self):
        self.main_frame = tk.Frame(self.master, padx=20, pady=20)
        self.main_frame.pack(expand=True, fill="both")

        tk.Label(self.main_frame, text="Selecione uma ação:", font=("Arial", 14, "bold")).pack(pady=10)

        # Botões de Adição
        tk.Button(self.main_frame, text="1. Adicionar Cliente", command=self.adicionar_cliente_gui, width=30).pack(pady=3)
        tk.Button(self.main_frame, text="2. Adicionar Processo", command=self.adicionar_processo_gui, width=30).pack(pady=3)
        tk.Button(self.main_frame, text="3. Registrar Pagamento", command=self.registrar_pagamento_gui, width=30).pack(pady=3)
        tk.Button(self.main_frame, text="4. Agendar Audiência", command=self.agendar_audiencia_gui, width=30).pack(pady=3)
        
        tk.Label(self.main_frame, text="--- Busca ---", font=("Arial", 12, "bold")).pack(pady=5)

        # Botões de Busca
        tk.Button(self.main_frame, text="5. Buscar Cliente", command=self.buscar_cliente_dialog, width=30).pack(pady=3)
        tk.Button(self.main_frame, text="6. Buscar Processo", command=self.buscar_processo_dialog, width=30).pack(pady=3)
        tk.Button(self.main_frame, text="7. Buscar Pagamento", command=self.buscar_pagamento_dialog, width=30).pack(pady=3)
        tk.Button(self.main_frame, text="8. Buscar Audiência", command=self.buscar_audiencia_dialog, width=30).pack(pady=3)

    # --- Métodos para Adicionar ---
    def adicionar_cliente_gui(self):
        dialog = ClienteDialog(self.master)
        data = dialog.show()
        
        if data:
            if data["cpf"] in self.data_stores["clientes"]:
                messagebox.showwarning("Erro", f"Cliente com CPF '{data['cpf']}' já existe.")
                return

            try:
                cliente = ClienteConcreto(data["nome"], data["cpf"], data["idade"], 
                                         data["telefone"], data["endereco"], data["email"])
                # CORREÇÃO AQUI: Adiciona o objeto cliente ao data_stores
                self.data_stores["clientes"][data["cpf"]] = cliente
                messagebox.showinfo("Sucesso", f"Cliente '{data['nome']}' adicionado!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar cliente: {e}")

    def adicionar_processo_gui(self):
        dialog = ProcessoDialog(self.master)
        data = dialog.show()

        if data:
            if data["numero"] in self.data_stores["processos"]:
                messagebox.showwarning("Erro", f"Processo com número '{data['numero']}' já existe.")
                return
            if data["cliente_cpf"] not in self.data_stores["clientes"]:
                messagebox.showwarning("Erro", f"Cliente com CPF '{data['cliente_cpf']}' não encontrado. Adicione-o primeiro.")
                return

            try:
                processo = ProcessoConcreto(data["numero"], data["descricao"], data["cliente_cpf"])
                # CORREÇÃO AQUI: Adiciona o objeto processo ao data_stores
                self.data_stores["processos"][data["numero"]] = processo
                messagebox.showinfo("Sucesso", f"Processo '{data['numero']}' adicionado!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar processo: {e}")

    def registrar_pagamento_gui(self):
        dialog = PagamentoDialog(self.master)
        data = dialog.show()

        if data:
            if data["cliente_cpf"] not in self.data_stores["clientes"]:
                messagebox.showwarning("Erro", f"Cliente com CPF '{data['cliente_cpf']}' não encontrado.")
                return
            
            try:
                pagamento = PagamentoConcreto(data["cliente_cpf"], data["valor"], data["descricao"])
                # CORREÇÃO AQUI: Adiciona o objeto pagamento ao data_stores
                self.data_stores["pagamentos"].append(pagamento)
                messagebox.showinfo("Sucesso", "Pagamento registrado!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao registrar pagamento: {e}")

    def agendar_audiencia_gui(self):
        dialog = AudienciaDialog(self.master)
        data = dialog.show()

        if data:
            if data["processo_numero"] not in self.data_stores["processos"]:
                messagebox.showwarning("Erro", f"Processo com número '{data['processo_numero']}' não encontrado.")
                return
            if data["cliente_cpf"] not in self.data_stores["clientes"]:
                messagebox.showwarning("Erro", f"Cliente com CPF '{data['cliente_cpf']}' não encontrado.")
                return

            try:
                audiencia = AudienciaConcreta(data["processo_numero"], data["data_hora"], 
                                             data["local"], data["tipo"], data["cliente_cpf"])
                # CORREÇÃO AQUI: Adiciona o objeto audiencia ao data_stores
                self.data_stores["audiencias"].append(audiencia)
                messagebox.showinfo("Sucesso", "Audiência agendada!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao agendar audiência: {e}")

    # --- Métodos de Busca (acessam os data_stores agora populados) ---
    def buscar_cliente_dialog(self):
        cpf_busca = simpledialog.askstring("Buscar Cliente", "Digite o CPF do cliente a buscar:")
        if not cpf_busca: return

        # Acessa o dicionário clientes em data_stores
        cliente = self.data_stores["clientes"].get(cpf_busca)
        if cliente:
            messagebox.showinfo("Cliente Encontrado", cliente.obter_detalhes_completos())
        else:
            messagebox.showinfo("Cliente Não Encontrado", f"Cliente com CPF '{cpf_busca}' não encontrado.")

    def buscar_processo_dialog(self):
        numero_busca = simpledialog.askstring("Buscar Processo", "Digite o número do processo a buscar:")
        if not numero_busca: return

        # Acessa o dicionário processos em data_stores
        processo = self.data_stores["processos"].get(numero_busca)
        if processo:
            messagebox.showinfo("Processo Encontrado", processo.obter_detalhes_completos())
        else:
            messagebox.showinfo("Processo Não Encontrado", f"Processo com número '{numero_busca}' não encontrado.")

    def buscar_pagamento_dialog(self):
        cliente_cpf_busca = simpledialog.askstring("Buscar Pagamento", "Digite o CPF do cliente para buscar pagamentos:")
        if not cliente_cpf_busca: return

        # Itera sobre a lista de pagamentos em data_stores
        pagamentos_encontrados = [p for p in self.data_stores["pagamentos"] if p.cliente_cpf == cliente_cpf_busca]

        if pagamentos_encontrados:
            list_str = f"--- Pagamentos para CPF: {cliente_cpf_busca} ---\n\n"
            for i, pagamento in enumerate(pagamentos_encontrados):
                list_str += f"Pagamento #{i+1}:\n{pagamento.obter_detalhes_completos()}\n"
                list_str += "-" * 40 + "\n"
            messagebox.showinfo("Pagamentos Encontrados", list_str)
        else:
            messagebox.showinfo("Pagamento Não Encontrado", f"Nenhum pagamento encontrado para o CPF '{cliente_cpf_busca}'.")

    def buscar_audiencia_dialog(self):
        processo_numero_busca = simpledialog.askstring("Buscar Audiência", "Digite o número do processo para buscar audiências:")
        if not processo_numero_busca: return

        # Itera sobre a lista de audiencias em data_stores
        audiencias_encontradas = [a for a in self.data_stores["audiencias"] if a.processo_numero == processo_numero_busca]

        if audiencias_encontradas:
            list_str = f"--- Audiências para Processo: {processo_numero_busca} ---\n\n"
            for i, audiencia in enumerate(audiencias_encontradas):
                list_str += f"Audiência #{i+1}:\n{audiencia.obter_detalhes_completos()}\n"
                list_str += "-" * 40 + "\n"
            messagebox.showinfo("Audiências Encontradas", list_str)
        else:
            messagebox.showinfo("Audiência Não Encontrada", f"Nenhuma audiência encontrada para o Processo '{processo_numero_busca}'.")

# --- Execução da Aplicação Tkinter ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaJuridicoAcaoGUI(root)
    root.mainloop()