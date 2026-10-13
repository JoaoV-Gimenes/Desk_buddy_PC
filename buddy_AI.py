import tkinter as tk
from tkinter import ttk


class BuddyApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Buddy AI")
        self.geometry("620x460")
        self.minsize(540, 400)

        # Estado simulado: a conexão serial real será adicionada depois.
        self.serial_conectada = False
        self.ia_ativa = False

        self._criar_widgets()
        self._atualizar_status()

    def _criar_widgets(self):
        container = ttk.Frame(self, padding=16)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container, text="Buddy AI", font=("Segoe UI", 20, "bold")
        ).pack(anchor="w")

        ttk.Label(
            container, text="Painel de controle do robô"
        ).pack(anchor="w", pady=(0, 16))

        conexao = ttk.LabelFrame(
            container, text="Conexão com a ESP32", padding=12
        )
        conexao.pack(fill="x", pady=(0, 12))

        linha_porta = ttk.Frame(conexao)
        linha_porta.pack(fill="x")

        ttk.Label(linha_porta, text="Porta serial:").pack(side="left")

        self.porta_var = tk.StringVar(value="COM5")
        self.porta_combo = ttk.Combobox(
            linha_porta,
            textvariable=self.porta_var,
            values=("COM3", "COM4", "COM5", "COM6"),
            state="readonly",
            width=12,
        )
        self.porta_combo.pack(side="left", padx=(8, 12))

        self.botao_conectar = ttk.Button(
            linha_porta, text="Conectar", command=self._alternar_conexao
        )
        self.botao_conectar.pack(side="left")

        self.status_serial_var = tk.StringVar()
        ttk.Label(
            conexao, textvariable=self.status_serial_var
        ).pack(anchor="w", pady=(10, 0))

        ia = ttk.LabelFrame(
            container, text="Inteligência artificial", padding=12
        )
        ia.pack(fill="x", pady=(0, 12))

        self.botao_ia = ttk.Button(
            ia, text="Ativar IA", command=self._alternar_ia
        )
        self.botao_ia.pack(side="left")

        self.status_ia_var = tk.StringVar()
        ttk.Label(
            ia, textvariable=self.status_ia_var
        ).pack(side="left", padx=12)

        mensagens = ttk.LabelFrame(
            container, text="Mensagens do Buddy", padding=8
        )
        mensagens.pack(fill="both", expand=True)

        self.log = tk.Text(
            mensagens,
            height=8,
            wrap="word",
            state="disabled",
            font=("Consolas", 10),
        )
        self.log.pack(fill="both", expand=True)

        self._registrar("Aplicativo iniciado.")
        self._registrar("A conexão serial ainda é simulada.")

    def _registrar(self, mensagem: str):
        self.log.configure(state="normal")
        self.log.insert("end", mensagem + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _alternar_conexao(self):
        # Simulação temporária; depois será substituída por pyserial.
        self.serial_conectada = not self.serial_conectada
        self._atualizar_status()

        if self.serial_conectada:
            self._registrar(f"Conexão simulada com {self.porta_var.get()}.")
        else:
            self.ia_ativa = False
            self._registrar("Conexão simulada encerrada.")
            self._atualizar_status()

    def _alternar_ia(self):
        if not self.serial_conectada:
            self._registrar("Conecte a ESP32 antes de ativar a IA.")
            return

        self.ia_ativa = not self.ia_ativa
        self._atualizar_status()
        self._registrar(
            "IA ativada." if self.ia_ativa else "IA desativada."
        )

    def _atualizar_status(self):
        if self.serial_conectada:
            self.status_serial_var.set(
                f"Status: conectada (simulação) — {self.porta_var.get()}"
            )
            self.botao_conectar.configure(text="Desconectar")
            self.porta_combo.configure(state="disabled")
        else:
            self.status_serial_var.set("Status: desconectada")
            self.botao_conectar.configure(text="Conectar")
            self.porta_combo.configure(state="readonly")

        if self.ia_ativa:
            self.status_ia_var.set("IA ativa")
            self.botao_ia.configure(text="Desativar IA")
        else:
            self.status_ia_var.set("IA desativada")
            self.botao_ia.configure(text="Ativar IA")


if __name__ == "__main__":
    app = BuddyApp()
    app.mainloop()