# modelo_abstrato.py

from abc import ABC, abstractmethod

# --- Suas Classes Abstratas Originais ---
class Cliente(ABC):
    def __init__(self, nome, cpf, idade, telefone, endereco, email):
        self.nome = nome
        self.cpf = cpf
        self.idade = idade
        self.telefone = telefone
        self.endereco = endereco
        self.email = email

    @abstractmethod
    def obter_identificacao(self):
        """Método abstrato para obter uma identificação do cliente."""
        pass

class Processo(ABC):
    def __init__(self, numero, descricao, cliente_cpf):
        self.numero = numero
        self.descricao = descricao
        self.cliente_cpf = cliente_cpf

    @abstractmethod
    def obter_resumo(self):
        """Método abstrato para obter um resumo do processo."""
        pass

class Pagamento(ABC):
    def __init__(self, cliente_cpf, valor, descricao):
        self.cliente_cpf = cliente_cpf
        self.valor = valor
        self.descricao = descricao

    @abstractmethod
    def confirmar_pagamento(self):
        """Método abstrato para confirmar o pagamento."""
        pass

class Audiencia(ABC):
    def __init__(self, processo_numero, data_hora, local, tipo, cliente_cpf):
        self.processo_numero = processo_numero
        self.data_hora = data_hora # Formato string 'DD/MM/AAAA HH:MM'
        self.local = local
        self.tipo = tipo
        self.cliente_cpf = cliente_cpf

    @abstractmethod
    def informar_status_audiencia(self):
        """Método abstrato para informar o status da audiência."""
        pass

# --- Classes Concretas Mínimas (necessárias para instanciar objetos) ---
class ClienteConcreto(Cliente):
    def obter_identificacao(self):
        return f"Cliente: {self.nome} (CPF: {self.cpf})"

    # ESTE MÉTODO ESTAVA FALTANDO OU INCORRETO
    def obter_detalhes_completos(self):
        return (f"Nome: {self.nome}\n"
                f"CPF: {self.cpf}\n"
                f"Idade: {self.idade}\n"
                f"Telefone: {self.telefone}\n"
                f"Endereço: {self.endereco}\n"
                f"Email: {self.email}")

class ProcessoConcreto(Processo):
    def obter_resumo(self):
        return f"Processo #{self.numero}: {self.descricao} (Cliente CPF: {self.cliente_cpf})"

    # ESTE MÉTODO ESTAVA FALTANDO OU INCORRETO
    def obter_detalhes_completos(self):
        return (f"Número: {self.numero}\n"
                f"Descrição: {self.descricao}\n"
                f"CPF do Cliente: {self.cliente_cpf}")

class PagamentoConcreto(Pagamento):
    def confirmar_pagamento(self):
        return f"Pagamento de R${self.valor:.2f} (Cliente CPF: {self.cliente_cpf}) confirmado. Descrição: {self.descricao}"

    # ESTE MÉTODO ESTAVA FALTANDO OU INCORRETO
    def obter_detalhes_completos(self):
        return (f"Cliente CPF: {self.cliente_cpf}\n"
                f"Valor: R${self.valor:.2f}\n"
                f"Descrição: {self.descricao}")

class AudienciaConcreta(Audiencia):
    def informar_status_audiencia(self):
        return (f"Audiência do Processo #{self.processo_numero} ({self.tipo}) em {self.local} "
                f"às {self.data_hora} (Cliente: {self.cliente_cpf}).")

    # ESTE MÉTODO ESTAVA FALTANDO OU INCORRETO
    def obter_detalhes_completos(self):
        return (f"Processo: {self.processo_numero}\n"
                f"Cliente CPF: {self.cliente_cpf}\n"
                f"Data/Hora: {self.data_hora}\n"
                f"Local: {self.local}\n"
                f"Tipo: {self.tipo}")