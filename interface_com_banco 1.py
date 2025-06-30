# =====================================================================
# INTERFACE E BANCO DE DADOS DO SISTEMA JURÍDICO
# Este arquivo contém a interface gráfica (Tkinter) e as funções
# de acesso ao banco de dados (MySQL).
#
# PRÉ-REQUISITO:
# Este arquivo DEVE estar na mesma pasta que o seu arquivo 'modelo_abstrato.py'
# para que a importação das classes funcione corretamente.
# =====================================================================

import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
import mysql.connector
from mysql.connector import errorcode

# --- PASSO 1: IMPORTAÇÃO DO SEU ARQUIVO DE MODELO ---
# O Python vai procurar por 'modelo_abstrato.py' na mesma pasta.
try:
    from modelo_abstrato import ClienteConcreto, ProcessoConcreto, PagamentoConcreto, AudienciaConcreta
except ImportError:
    print("ERRO CRÍTICO: O arquivo 'modelo_abstrato.py' não foi encontrado.")
    print("Certifique-se de que ele está na mesma pasta que este script.")
    exit()


# --- PASSO 2: CONFIGURAÇÃO DO BANCO DE DADOS ---
# !!! IMPORTANTE: Altere estes valores para os da sua configuração do MySQL !!!
DB_CONFIG = {
    'user': 'root',
    'password': 'root', # Coloque a senha do seu usuário root aqui
    'host': '127.0.0.1',             # ou 'localhost'
    'database': 'advocacia_db',      # O nome do banco de dados que criamos
    'raise_on_warnings': True
}


# --- PASSO 3: FUNÇÕES DE BANCO DE DADOS ---

def get_db_connection():
    """Cria e retorna um objeto de conexão com o banco de dados."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Erro de Conexão: Usuário ou senha do banco de dados incorretos.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"Erro de Conexão: O banco de dados '{DB_CONFIG['database']}' não existe.")
        else:
            print(f"Erro ao conectar ao banco de dados: {err}")
        return None

def add_cliente(cliente: ClienteConcreto):
    """Adiciona um novo cliente ao banco de dados."""
    conn = get_db_connection()
    if not conn: return False
    sql = "INSERT INTO clientes (cpf, nome, idade, telefone, endereco, email) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (cliente.cpf, cliente.nome, cliente.idade, cliente.telefone, cliente.endereco, cliente.email)
    try:
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Erro ao adicionar cliente: {err}"); conn.rollback(); return False
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

def add_processo(processo: ProcessoConcreto):
    """Adiciona um novo processo ao banco de dados."""
    conn = get_db_connection()
    if not conn: return False
    sql = "INSERT INTO processos (numero_processo, cliente_cpf, descricao) VALUES (%s, %s, %s)"
    values = (processo.numero, processo.cliente_cpf, processo.descricao)
    try:
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Erro ao adicionar processo: {err}"); conn.rollback(); return False
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

def add_pagamento(pagamento: PagamentoConcreto):
    """Adiciona um novo pagamento ao banco de dados."""
    conn = get_db_connection()
    if not conn: return False
    sql = "INSERT INTO pagamentos (cliente_cpf, valor, descricao) VALUES (%s, %s, %s)"
    values = (pagamento.cliente_cpf, pagamento.valor, pagamento.descricao)
    try:
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Erro ao adicionar pagamento: {err}"); conn.rollback(); return False
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

def add_audiencia(audiencia: AudienciaConcreta):
    """Adiciona uma nova audiência ao banco de dados."""
    conn = get_db_connection()
    if not conn: return False
    try:
        data_hora_mysql = datetime.strptime(audiencia.data_hora, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        messagebox.showwarning("Formato Inválido", "Formato de data/hora inválido. Use DD/MM/AAAA HH:MM"); return False
    sql = "INSERT INTO audiencias (numero_processo, data_hora, local, tipo) VALUES (%s, %s, %s, %s)"
    values = (audiencia.processo_numero, data_hora_mysql, audiencia.local, audiencia.tipo)
    try:
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Erro ao adicionar audiência: {err}"); conn.rollback(); return False
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

def find_cliente_by_cpf(cpf: str):
    """Busca um cliente pelo CPF e retorna um objeto ClienteConcreto ou None."""
    conn = get_db_connection()
    if not conn: return None
    cliente = None
    sql = "SELECT cpf, nome, idade, telefone, endereco, email FROM clientes WHERE cpf = %s"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (cpf,))
        result = cursor.fetchone()
        if result:
            cliente = ClienteConcreto(nome=result[1], cpf=result[0], idade=result[2], telefone=result[3], endereco=result[4], email=result[5])
    except mysql.connector.Error as err: print(f"Erro ao buscar cliente: {err}")
    finally:
        if conn.is_connected(): cursor.close(); conn.close()
    return cliente

def find_processo_by_numero(numero: str):
    """Busca um processo pelo número e retorna um objeto ProcessoConcreto ou None."""
    conn = get_db_connection()
    if not conn: return None
    processo = None
    sql = "SELECT numero_processo, descricao, cliente_cpf FROM processos WHERE numero_processo = %s"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (numero,))
        result = cursor.fetchone()
        if result:
            processo = ProcessoConcreto(numero=result[0], descricao=result[1], cliente_cpf=result[2])
    except mysql.connector.Error as err: print(f"Erro ao buscar processo: {err}")
    finally:
        if conn.is_connected(): cursor.close(); conn.close()
    return processo

def find_pagamentos_by_cpf(cpf: str):
    """Busca todos os pagamentos de um cliente e retorna uma lista de objetos PagamentoConcreto."""
    conn = get_db_connection()
    if not conn: return []
    pagamentos = []
    sql = "SELECT cliente_cpf, valor, descricao FROM pagamentos WHERE cliente_cpf = %s"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (cpf,))
        results = cursor.fetchall()
        for row in results:
            pagamentos.append(PagamentoConcreto(cliente_cpf=row[0], valor=row[1], descricao=row[2]))
    except mysql.connector.Error as err: print(f"Erro ao buscar pagamentos: {err}")
    finally:
        if conn.is_connected(): cursor.close(); conn.close()
    return pagamentos

def find_audiencias_by_processo(numero_processo: str):
    """Busca todas as audiências de um processo e retorna uma lista de objetos AudienciaConcreta."""
    conn = get_db_connection()
    if not conn: return []
    audiencias = []
    sql = """SELECT a.numero_processo, p.cliente_cpf, a.data_hora, a.local, a.tipo 
             FROM audiencias a JOIN processos p ON a.numero_processo = p.numero_processo
             WHERE a.numero_processo = %s"""
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (numero_processo,))
        results = cursor.fetchall()
        for row in results:
            data_hora_display = row[2].strftime('%d/%m/%Y %H:%M')
            audiencias.append(AudienciaConcreta(processo_numero=row[0], cliente_cpf=row[1], data_hora=data_hora_display, local=row[3], tipo=row[4]))
    except mysql.connector.Error as err: print(f"Erro ao buscar audiências: {err}")
    finally:
        if conn.is_connected(): cursor.close(); conn.close()
    return audiencias


# --- PASSO 4: INTERFACE GRÁFICA (TKINTER) ---

class BaseDialog(tk.Toplevel):
    """Classe base para as janelas de diálogo de entrada de dados."""
    def __init__(self, parent, title, fields):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title(title)
        self.result = None
        self.entries = {}
        self.body_frame = tk.Frame(self)
        self.body_frame.pack(padx=10, pady=10)
        self.setup_fields(fields)
        self.setup_buttons()
        self.parent = parent
        self.bind("<Return>", self._on_ok)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.geometry(f"+{parent.winfo_x() + 50}+{parent.winfo_y() + 50}")

    def setup_fields(self, fields):
        self.entries_labels = {f[1]: f[0] for f in fields}
        for i, (label_text, key_name, default_value, input_type) in enumerate(fields):
            tk.Label(self.body_frame, text=label_text + ":").grid(row=i, column=0, sticky="w", pady=2, padx=5)
            entry = tk.Entry(self.body_frame, width=40)
            entry.grid(row=i, column=1, pady=2, padx=5)
            entry.insert(0, default_value)
            self.entries[key_name] = {"widget": entry, "type": input_type}
        if self.entries: self.entries[fields[0][1]]["widget"].focus_set()

    def setup_buttons(self):
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="OK", command=self._on_ok, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancelar", command=self._on_cancel, width=10).pack(side=tk.LEFT, padx=5)

    def _on_ok(self, event=None):
        values = {}
        for key_name, data in self.entries.items():
            value_str, input_type = data["widget"].get(), data["type"]
            if not value_str and input_type != "optional":
                messagebox.showwarning("Erro de Entrada", f"O campo '{self.entries_labels.get(key_name, key_name)}' é obrigatório."); return
            try:
                if value_str: # Só tenta converter se não for vazio
                    if input_type == "int": values[key_name] = int(value_str)
                    elif input_type == "float": values[key_name] = float(value_str)
                    else: values[key_name] = value_str
                else:
                    values[key_name] = None # Se for opcional e vazio, o valor é None
            except ValueError:
                messagebox.showwarning("Erro de Entrada", f"O campo '{self.entries_labels.get(key_name, key_name)}' deve ser um número válido."); return
        self.result = values; self.destroy()

    def _on_cancel(self): self.result = None; self.destroy()
    def show(self): self.parent.wait_window(self); return self.result

class ClienteDialog(BaseDialog):
    def __init__(self, parent):
        fields = [("Nome", "nome", "", "str"), ("CPF", "cpf", "", "str"), ("Idade", "idade", "", "int"),
                  ("Telefone", "telefone", "", "str"), ("Endereço", "endereco", "", "str"), ("Email", "email", "", "str")]
        super().__init__(parent, "Adicionar Cliente", fields)

class ProcessoDialog(BaseDialog):
    def __init__(self, parent):
        fields = [("Número do Processo", "numero", "", "str"), ("Descrição", "descricao", "", "str"), ("CPF do Cliente", "cliente_cpf", "", "str")]
        super().__init__(parent, "Adicionar Processo", fields)

class PagamentoDialog(BaseDialog):
    def __init__(self, parent):
        fields = [("CPF do Cliente", "cliente_cpf", "", "str"), ("Valor", "valor", "", "float"), ("Descrição", "descricao", "", "str")]
        super().__init__(parent, "Registrar Pagamento", fields)

class AudienciaDialog(BaseDialog):
    def __init__(self, parent):
        fields = [("Número do Processo", "processo_numero", "", "str"), ("Data e Hora (DD/MM/AAAA HH:MM)", "data_hora", "", "str"),
                  ("Local", "local", "", "str"), ("Tipo", "tipo", "", "str")]
        super().__init__(parent, "Agendar Audiência", fields)

class SistemaJuridicoAcaoGUI:
    """Classe principal que monta e gerencia a interface gráfica."""
    def __init__(self, master):
        self.master = master
        master.title("Sistema Jurídico (Interface + BD)")
        master.geometry("450x350")
        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.master, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")
        tk.Label(main_frame, text="Selecione uma ação:", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Button(main_frame, text="1. Adicionar Cliente", command=self.adicionar_cliente_gui, width=30).pack(pady=3)
        tk.Button(main_frame, text="2. Adicionar Processo", command=self.adicionar_processo_gui, width=30).pack(pady=3)
        tk.Button(main_frame, text="3. Registrar Pagamento", command=self.registrar_pagamento_gui, width=30).pack(pady=3)
        tk.Button(main_frame, text="4. Agendar Audiência", command=self.agendar_audiencia_gui, width=30).pack(pady=3)
        tk.Label(main_frame, text="--- Busca ---", font=("Arial", 12, "bold")).pack(pady=(15, 5))
        tk.Button(main_frame, text="5. Buscar Cliente", command=self.buscar_cliente_dialog, width=30).pack(pady=3)
        tk.Button(main_frame, text="6. Buscar Processo", command=self.buscar_processo_dialog, width=30).pack(pady=3)
        tk.Button(main_frame, text="7. Buscar Pagamentos", command=self.buscar_pagamento_dialog, width=30).pack(pady=3)
        tk.Button(main_frame, text="8. Buscar Audiências", command=self.buscar_audiencia_dialog, width=30).pack(pady=3)

    def adicionar_cliente_gui(self):
        data = ClienteDialog(self.master).show()
        if data:
            if find_cliente_by_cpf(data["cpf"]):
                messagebox.showwarning("Erro", f"Cliente com CPF '{data['cpf']}' já existe."); return
            if add_cliente(ClienteConcreto(**data)):
                messagebox.showinfo("Sucesso", f"Cliente '{data['nome']}' adicionado!")
            else:
                messagebox.showerror("Erro de BD", "Não foi possível adicionar o cliente. Verifique o console.")

    def adicionar_processo_gui(self):
        data = ProcessoDialog(self.master).show()
        if data:
            if find_processo_by_numero(data["numero"]):
                messagebox.showwarning("Erro", f"Processo com número '{data['numero']}' já existe."); return
            if not find_cliente_by_cpf(data["cliente_cpf"]):
                messagebox.showwarning("Erro", f"Cliente com CPF '{data['cliente_cpf']}' não encontrado."); return
            if add_processo(ProcessoConcreto(**data)):
                messagebox.showinfo("Sucesso", f"Processo '{data['numero']}' adicionado!")
            else:
                messagebox.showerror("Erro de BD", "Não foi possível adicionar o processo. Verifique o console.")

    def registrar_pagamento_gui(self):
        data = PagamentoDialog(self.master).show()
        if data:
            if not find_cliente_by_cpf(data["cliente_cpf"]):
                messagebox.showwarning("Erro", f"Cliente com CPF '{data['cliente_cpf']}' não encontrado."); return
            if add_pagamento(PagamentoConcreto(**data)):
                messagebox.showinfo("Sucesso", "Pagamento registrado!")
            else:
                messagebox.showerror("Erro de BD", "Não foi possível registrar o pagamento. Verifique o console.")

    def agendar_audiencia_gui(self):
        data = AudienciaDialog(self.master).show()
        if data:
            processo = find_processo_by_numero(data["processo_numero"])
            if not processo:
                messagebox.showwarning("Erro", f"Processo '{data['processo_numero']}' não encontrado."); return
            data['cliente_cpf'] = processo.cliente_cpf
            if add_audiencia(AudienciaConcreta(**data)):
                messagebox.showinfo("Sucesso", "Audiência agendada!")
            else:
                messagebox.showerror("Erro de BD", "Não foi possível agendar a audiência. Verifique o console.")

    def buscar_cliente_dialog(self):
        cpf_busca = simpledialog.askstring("Buscar Cliente", "Digite o CPF do cliente:")
        if not cpf_busca: return
        cliente = find_cliente_by_cpf(cpf_busca)
        if cliente: messagebox.showinfo("Cliente Encontrado", cliente.obter_detalhes_completos())
        else: messagebox.showinfo("Não Encontrado", f"Cliente com CPF '{cpf_busca}' não foi encontrado.")

    def buscar_processo_dialog(self):
        numero_busca = simpledialog.askstring("Buscar Processo", "Digite o número do processo:")
        if not numero_busca: return
        processo = find_processo_by_numero(numero_busca)
        if processo: messagebox.showinfo("Processo Encontrado", processo.obter_detalhes_completos())
        else: messagebox.showinfo("Não Encontrado", f"Processo com número '{numero_busca}' não encontrado.")

    def buscar_pagamento_dialog(self):
        cpf_busca = simpledialog.askstring("Buscar Pagamentos", "Digite o CPF do cliente:")
        if not cpf_busca: return
        pagamentos = find_pagamentos_by_cpf(cpf_busca)
        if pagamentos:
            list_str = f"--- Pagamentos para CPF: {cpf_busca} ---\n\n"
            for i, p in enumerate(pagamentos):
                list_str += f"Pagamento #{i+1}:\n{p.obter_detalhes_completos()}\n{'-'*40}\n"
            messagebox.showinfo("Pagamentos Encontrados", list_str)
        else: messagebox.showinfo("Não Encontrado", f"Nenhum pagamento encontrado para o CPF '{cpf_busca}'.")

    def buscar_audiencia_dialog(self):
        numero_busca = simpledialog.askstring("Buscar Audiências", "Digite o número do processo:")
        if not numero_busca: return
        audiencias = find_audiencias_by_processo(numero_busca)
        if audiencias:
            list_str = f"--- Audiências para Processo: {numero_busca} ---\n\n"
            for i, a in enumerate(audiencias):
                list_str += f"Audiência #{i+1}:\n{a.obter_detalhes_completos()}\n{'-'*40}\n"
            messagebox.showinfo("Audiências Encontradas", list_str)
        else: messagebox.showinfo("Não Encontrado", f"Nenhuma audiência para o Processo '{numero_busca}'.")


# --- PASSO 5: EXECUÇÃO DA APLICAÇÃO ---
if __name__ == "__main__":
    # Testa a conexão com o banco de dados antes de iniciar a GUI
    conn = get_db_connection()
    if conn:
        conn.close()
        print("Conexão com o banco de dados bem-sucedida. Iniciando aplicação...")
        root = tk.Tk()
        app = SistemaJuridicoAcaoGUI(root)
        root.mainloop()
    else:
        print("Falha ao conectar ao banco de dados. A aplicação não será iniciada.")
        messagebox.showerror("Erro Crítico de Banco de Dados", 
                             "Não foi possível conectar ao banco de dados MySQL.\n"
                             "Verifique se o servidor está rodando e se as credenciais neste arquivo estão corretas.")
