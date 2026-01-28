import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from datetime import datetime, timedelta
import uuid

class Plaza:
    def __init__(self, numero, tipo):
        self.numero = numero
        self.tipo = tipo
        self.estado = "libre"

    def reservar(self):
        if self.estado == "libre":
            self.estado = "reservada"
            return True
        return False

    def liberar(self):
        self.estado = "libre"

    def ocupar(self):
        if self.estado in ["libre", "reservada"]:
            self.estado = "ocupada"
            return True
        return False

class Vehiculo:
    def __init__(self, matricula, tipo):
        self.matricula = matricula.upper()
        self.tipo = tipo

class Ticket:
    def __init__(self, vehiculo):
        self.codigo = str(uuid.uuid4())[:8]
        self.vehiculo = vehiculo
        self.hora_entrada = datetime.now()
        self.hora_salida = None

    def registrar_salida(self):
        self.hora_salida = datetime.now()

    def calcular_tiempo(self):
        fin = self.hora_salida if self.hora_salida else datetime.now()
        return fin - self.hora_entrada

class Parking:
    def __init__(self):
        self.plazas = []
        self.tarifas = {"coche": 2.50, "moto": 1.50}

    def agregar_plaza(self, plaza):
        self.plazas.append(plaza)

    def reservar_y_generar_ticket(self, vehiculo):
        for plaza in self.plazas:
            if plaza.tipo == vehiculo.tipo and plaza.estado == "libre":
                plaza.ocupar()
                ticket = Ticket(vehiculo)
                return ticket, plaza
        return None, None

    def procesar_salida(self, ticket, plaza):
        ticket.hora_entrada -= timedelta(minutes=90)  # Simulación
        ticket.registrar_salida()

        tiempo = ticket.calcular_tiempo()
        horas = tiempo.total_seconds() / 3600
        total = round(horas * self.tarifas.get(ticket.vehiculo.tipo, 2.0), 2)

        return {
            "codigo": ticket.codigo,
            "matricula": ticket.vehiculo.matricula,
            "tiempo_horas": int(horas),
            "tiempo_minutos": int((horas % 1) * 60),
            "total": total
        }

class ParkingApp(tb.Window):
    def __init__(self, parking):
        super().__init__(themename="flatly")
        self.title("Dashboard - Gestión Parking")
        self.geometry("750x900")
        self.parking = parking
        self.tickets_activos = {}

        self.create_widgets()
        self.actualizar_dashboard()

    def create_widgets(self):
        # Panel Resumen
        resumen_frame = tb.Labelframe(self, text="Resumen General", padding=15)
        resumen_frame.pack(fill="x", padx=15, pady=10)

        self.lbl_total = tb.Label(resumen_frame, text="Total Plazas: 0", font=("Helvetica", 12, "bold"))
        self.lbl_libres = tb.Label(resumen_frame, text="Plazas Libres: 0", foreground="#28a745", font=("Helvetica", 12))
        self.lbl_ocupadas = tb.Label(resumen_frame, text="Plazas Ocupadas: 0", foreground="#dc3545", font=("Helvetica", 12))
        self.lbl_reservadas = tb.Label(resumen_frame, text="Plazas Reservadas: 0", foreground="#ffc107", font=("Helvetica", 12))

        self.lbl_total.grid(row=0, column=0, padx=20, pady=5)
        self.lbl_libres.grid(row=0, column=1, padx=20, pady=5)
        self.lbl_ocupadas.grid(row=0, column=2, padx=20, pady=5)
        self.lbl_reservadas.grid(row=0, column=3, padx=20, pady=5)

        # Panel Plazas
        plazas_frame = tb.Labelframe(self, text="Estado de Plazas", padding=10)
        plazas_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.plaza_buttons = []
        filas = 2
        cols = (len(self.parking.plazas) + 1)//2
        for i, plaza in enumerate(self.parking.plazas):
            btn = tb.Button(plazas_frame, text=f"P{plaza.numero}\n{plaza.tipo.capitalize()}",
                            state="disabled", bootstyle="secondary")
            btn.grid(row=i // cols, column=i % cols, padx=8, pady=8, sticky="nsew")
            self.plaza_buttons.append((btn, plaza))

        # Configurar pesos para que los botones se expandan
        for r in range(filas):
            plazas_frame.rowconfigure(r, weight=1)
        for c in range(cols):
            plazas_frame.columnconfigure(c, weight=1)

        # Panel Entrada
        entrada_frame = tb.Labelframe(self, text="Registrar Entrada", padding=15)
        entrada_frame.pack(fill="x", padx=15, pady=10)

        tb.Label(entrada_frame, text="Matrícula:", font=("Helvetica", 11)).grid(row=0, column=0, sticky="e", padx=10, pady=6)
        self.entry_matricula = tb.Entry(entrada_frame, bootstyle="info")
        self.entry_matricula.grid(row=0, column=1, sticky="w", padx=10, pady=6)

        tb.Label(entrada_frame, text="Tipo vehículo:", font=("Helvetica", 11)).grid(row=1, column=0, sticky="e", padx=10, pady=6)
        self.combo_tipo = tb.Combobox(entrada_frame, values=["coche", "moto"], state="readonly", bootstyle="info")
        self.combo_tipo.current(0)
        self.combo_tipo.grid(row=1, column=1, sticky="w", padx=10, pady=6)

        btn_entrada = tb.Button(entrada_frame, text="Registrar Entrada", bootstyle="success", command=self.registrar_entrada)
        btn_entrada.grid(row=2, column=0, columnspan=2, pady=12, ipadx=10)

        # Panel Salida
        salida_frame = tb.Labelframe(self, text="Procesar Salida", padding=15)
        salida_frame.pack(fill="x", padx=15, pady=10)

        tb.Label(salida_frame, text="Código Ticket:", font=("Helvetica", 11)).grid(row=0, column=0, sticky="e", padx=10, pady=6)
        self.entry_codigo = tb.Entry(salida_frame, bootstyle="warning")
        self.entry_codigo.grid(row=0, column=1, sticky="w", padx=10, pady=6)

        btn_salida = tb.Button(salida_frame, text="Procesar Salida y Pago", bootstyle="danger", command=self.procesar_salida)
        btn_salida.grid(row=1, column=0, columnspan=2, pady=12, ipadx=10)

        # Área Recibo
        recibo_frame = tb.Labelframe(self, text="Ticket / Recibo", padding=10)
        recibo_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.text_recibo = tb.Text(recibo_frame, height=9, font=("Courier New", 11), state="disabled",)
        self.text_recibo.pack(fill="both", expand=True)

    def actualizar_dashboard(self):
        total = len(self.parking.plazas)
        libres = sum(1 for p in self.parking.plazas if p.estado == "libre")
        ocupadas = sum(1 for p in self.parking.plazas if p.estado == "ocupada")
        reservadas = sum(1 for p in self.parking.plazas if p.estado == "reservada")

        self.lbl_total.config(text=f"Total Plazas: {total}")
        self.lbl_libres.config(text=f"Plazas Libres: {libres}")
        self.lbl_ocupadas.config(text=f"Plazas Ocupadas: {ocupadas}")
        self.lbl_reservadas.config(text=f"Plazas Reservadas: {reservadas}")

        color_map = {
            "libre": "success",
            "ocupada": "danger",
            "reservada": "warning"
        }

        for btn, plaza in self.plaza_buttons:
            btn.configure(bootstyle=f"{color_map.get(plaza.estado, 'secondary')} disabled")

    def registrar_entrada(self):
        matricula = self.entry_matricula.get().strip()
        tipo = self.combo_tipo.get()

        if not matricula:
            messagebox.showwarning("Entrada inválida", "Debe ingresar la matrícula del vehículo.")
            return

        vehiculo = Vehiculo(matricula, tipo)
        ticket, plaza = self.parking.reservar_y_generar_ticket(vehiculo)

        if ticket is None:
            messagebox.showerror("Sin plazas", f"No hay plazas disponibles para {tipo}.")
            return

        self.tickets_activos[ticket.codigo] = (ticket, plaza)
        self.actualizar_dashboard()

        self.text_recibo.configure(state="normal")
        self.text_recibo.delete("1.0", "end")
        self.text_recibo.insert("end", f"✔ Entrada registrada.\nPlaza asignada: {plaza.numero}\n")
        self.text_recibo.insert("end", f"Código Ticket: {ticket.codigo}\nMatrícula: {matricula}\nTipo: {tipo}\nHora Entrada: {ticket.hora_entrada.strftime('%Y-%m-%d %H:%M:%S')}")
        self.text_recibo.configure(state="disabled")

        self.entry_matricula.delete(0, "end")

    def procesar_salida(self):
        codigo = self.entry_codigo.get().strip()
        if codigo not in self.tickets_activos:
            messagebox.showerror("Código inválido", "No se encontró ningún ticket activo con ese código.")
            return

        ticket, plaza = self.tickets_activos.pop(codigo)
        recibo = self.parking.procesar_salida(ticket, plaza)
        plaza.liberar()
        self.actualizar_dashboard()

        texto = (
            f"RECIBO DE PAGO\n"
            f"Ticket ID: {recibo['codigo']}\n"
            f"Matrícula: {recibo['matricula']}\n"
            f"Tiempo: {recibo['tiempo_horas']}h {recibo['tiempo_minutos']}min\n"
            f"TOTAL: {recibo['total']} €\n"
            f"Plaza {plaza.numero} ahora está LIBRE.\n"
        )
        self.text_recibo.configure(state="normal")
        self.text_recibo.delete("1.0", "end")
        self.text_recibo.insert("end", texto)
        self.text_recibo.configure(state="disabled")

        self.entry_codigo.delete(0, "end")

if __name__ == "__main__":
    parking = Parking()
    for i in range(1, 6):
        parking.agregar_plaza(Plaza(i, "coche"))
    for i in range(6, 9):
        parking.agregar_plaza(Plaza(i, "moto"))

    app = ParkingApp(parking)
    app.mainloop()