import tkinter as tk
from tkinter import ttk, messagebox
import serial
from serial.tools import list_ports


class BuddyApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Buddy AI")
        self.geometry("650x480")
        self.minsize(560, 420)

        self.conexao_serial = None
        self.ia_ativa = False
        self.status_var = tk.StringVar(
            master=self,
            value="Aguardando: diga Hi ESP"
        )
        self.status_label = ttk.Label(
            self,
            textvariable=self.status_var,
            font=("Arial", 14, "bold")
        )

        self.status_label.pack(pady=10)

        self._criar_widgets()
        self._listar_portas()
        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)
        self.after(100, self._ler_serial)

    def _criar_widgets(self):
        container = ttk.Frame(self, padding=16)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Buddy AI", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(container, text="Painel de controle do robô").pack(anchor="w", pady=(0, 16))

        conexao = ttk.LabelFrame(container, text="Conexão com a ESP32", padding=12)
        conexao.pack(fill="x", pady=(0, 12))

        linha_porta = ttk.Frame(conexao)
        linha_porta.pack(fill="x")
        ttk.Label(linha_porta, text="Porta serial:").pack(side="left")

        self.porta_var = tk.StringVar(value="COM5")
        self.porta_combo = ttk.Combobox(linha_porta, textvariable=self.porta_var, state="readonly", width=14)
        self.porta_combo.pack(side="left", padx=(8, 8))
        ttk.Button(linha_porta, text="Atualizar portas", command=self._listar_portas).pack(side="left", padx=(0, 8))

        self.botao_conectar = ttk.Button(linha_porta, text="Conectar", command=self._alternar_conexao)
        self.botao_conectar.pack(side="left")

        self.status_serial_var = tk.StringVar(value="Status: desconectada")
        ttk.Label(conexao, textvariable=self.status_serial_var).pack(anchor="w", pady=(10, 0))

        ia = ttk.LabelFrame(container, text="Inteligência artificial", padding=12)
        ia.pack(fill="x", pady=(0, 12))
        self.botao_ia = ttk.Button(ia, text="Ativar IA", command=self._alternar_ia)
        self.botao_ia.pack(side="left")
        self.status_ia_var = tk.StringVar(value="IA desativada")
        ttk.Label(ia, textvariable=self.status_ia_var).pack(side="left", padx=12)

        mensagens = ttk.LabelFrame(container, text="Mensagens do Buddy", padding=8)
        mensagens.pack(fill="both", expand=True)
        self.log = tk.Text(mensagens, height=9, wrap="word", state="disabled", font=("Consolas", 10))
        self.log.pack(fill="both", expand=True)

        self._registrar("Aplicativo iniciado.")
        self._registrar("Selecione COM5 e clique em Conectar.")

    def _listar_portas(self):
        portas = [porta.device for porta in list_ports.comports()]
        if "COM5" in portas:
            self.porta_var.set("COM5")
        elif portas:
            self.porta_var.set(portas[0])
        else:
            self.porta_var.set("COM5")
        self.porta_combo["values"] = portas if portas else ["COM5"]
        if portas:
            self._registrar("Portas encontradas: " + ", ".join(portas))
        else:
            self._registrar("Nenhuma porta detectada. Confira o cabo USB e o ESP32.")

    def _registrar(self, mensagem):
        self.log.configure(state="normal")
        self.log.insert("end", mensagem + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _alternar_conexao(self):
        if self.conexao_serial and self.conexao_serial.is_open:
            self.conexao_serial.close()
            self.conexao_serial = None
            self.ia_ativa = False
            self._registrar("Conexão serial encerrada.")
            self._atualizar_status()
            return

        porta = self.porta_var.get().strip()
        try:
            # O ESP32 está configurado para usar 115200 baud.
            self.conexao_serial = serial.Serial(port=porta, baudrate=115200, timeout=0)
            self._registrar(f"Conectado à {porta} a 115200 baud.")
            self._registrar("Aguardando mensagens do ESP32...")
            self._atualizar_status()
        except serial.SerialException as erro:
            self.conexao_serial = None
            self._atualizar_status()
            self._registrar(f"Não foi possível abrir {porta}: {erro}")
            messagebox.showerror(
                "Erro de conexão",
                f"Não foi possível abrir {porta}.\n\nFeche o Monitor Serial da Arduino IDE e tente novamente.\n\nDetalhes: {erro}",
            )

    def processar_mensagem(self, linha):
        print("MENSAGEM RECEBIDA:", repr(linha))

        if "WakeWord Detected!" in linha:
            self.status_var.set("Buddy está ouvindo!")
            self._registrar("STATUS: Buddy está ouvindo!")


        if "Command ID" in linha and "Detected!" in linha:

            self.status_var.set("Comando reconhecido!")

            self._registrar("STATUS: Comando reconhecido!")


        if "Light On" in linha:

            self.status_var.set("Comando: ligar luz")


        if "Light Off" in linha:

            self.status_var.set("Comando: desligar luz")

    def _ler_serial(self):
        if self.conexao_serial and self.conexao_serial.is_open:
            try:
                while self.conexao_serial.in_waiting:
                    linha = self.conexao_serial.readline().decode("utf-8", errors="replace").strip()
                    if linha:
                        self._registrar(linha)
                        self.processar_mensagem(linha)

            except (serial.SerialException, OSError) as erro:
                self._registrar(f"Erro ao ler a porta serial: {erro}")
                try:
                    self.conexao_serial.close()
                except Exception:
                    pass
                self.conexao_serial = None
                self.ia_ativa = False
                self._atualizar_status()
        self.after(100, self._ler_serial)

    def _alternar_ia(self):
        if not (self.conexao_serial and self.conexao_serial.is_open):
            self._registrar("Conecte a ESP32 antes de ativar a IA.")
            return
        self.ia_ativa = not self.ia_ativa
        self._atualizar_status()
        self._registrar("IA ativada (a integração com a API será feita depois)." if self.ia_ativa else "IA desativada.")

    def _atualizar_status(self):
        conectada = bool(self.conexao_serial and self.conexao_serial.is_open)
        if conectada:
            self.status_serial_var.set(f"Status: conectada — {self.porta_var.get()}")
            self.botao_conectar.configure(text="Desconectar")
            self.porta_combo.configure(state="disabled")
        else:
            self.status_serial_var.set("Status: desconectada")
            self.botao_conectar.configure(text="Conectar")
            self.porta_combo.configure(state="readonly")
        self.botao_ia.configure(text="Desativar IA" if self.ia_ativa else "Ativar IA")
        self.status_ia_var.set("IA ativa (simulação)" if self.ia_ativa else "IA desativada")

    def _ao_fechar(self):
        if self.conexao_serial and self.conexao_serial.is_open:
            self.conexao_serial.close()
        self.destroy()


if __name__ == "__main__":
    app = BuddyApp()
    app.mainloop()
