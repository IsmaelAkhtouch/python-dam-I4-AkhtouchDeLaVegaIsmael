import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from datetime import datetime, timedelta
import uuid

# ===================== MODELOS =====================
class Plaza:
    def __init__(self, numero, tipo):
        self.numero = numero
        self.tipo = tipo
        self.estado = "libre"      # libre | reservada | ocupada
        self.reserved_for = None
    def reservar(self, matricula):
        if self.estado == "libre":
            self.estado = "reservada"
            self.reserved_for = matricula
            return True
        return False
    def ocupar(self):
        if self.estado in ("libre", "reservada"):
            self.estado = "ocupada"
            return True
        return False
    def cancelar_reserva(self):
        if self.estado == "reservada":
            self.estado = "libre"
            self.reserved_for = None
            return True
        return False
    def liberar(self):
        self.estado = "libre"
        self.reserved_for = None

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
        fin = self.hora_salida or datetime.now()
        return fin - self.hora_entrada

class Parking:
    def __init__(self):
        self.plazas = []
        self.tarifas = {"coche": 2.5, "moto": 1.5}
    def agregar_plaza(self, plaza):
        self.plazas.append(plaza)
    def procesar_salida(self, ticket):
        ticket.hora_entrada -= timedelta(minutes=90)  # simulación
        ticket.registrar_salida()
        tiempo = ticket.calcular_tiempo()
        horas = tiempo.total_seconds() / 3600
        total = round(horas * self.tarifas.get(ticket.vehiculo.tipo, 2.0), 2)
        return horas, total

# ===================== APLICACIÓN =====================
class ParkingApp(tb.Window):
    def __init__(self, parking):
        super().__init__(themename="flatly")
        self.title("Gestión de Parking")
        self.geometry("780x900")
        self.parking = parking
        self.tickets_activos = {}   # codigo -&gt; (plaza, ticket)
        self.pending_vehicle = None
        self.pending_reservation = None
        self.create_widgets()
        self.actualizar_dashboard()

    # ---------- UI ----------
    def create_widgets(self):
        resumen = tb.Labelframe(self, text="Resumen", padding=15)
        resumen.pack(fill="x", padx=15, pady=10)
        self.lbl_total = tb.Label(resumen)
        self.lbl_libres = tb.Label(resumen, foreground="green")
        self.lbl_ocupadas = tb.Label(resumen, foreground="red")
        self.lbl_reservadas = tb.Label(resumen, foreground="orange")
        self.lbl_total.grid(row=0, column=0, padx=15)
        self.lbl_libres.grid(row=0, column=1, padx=15)
        self.lbl_ocupadas.grid(row=0, column=2, padx=15)
        self.lbl_reservadas.grid(row=0, column=3, padx=15)

        frame_plazas = tb.Labelframe(self, text="Plazas", padding=10)
        frame_plazas.pack(fill="both", expand=True, padx=15, pady=10)
        self.plaza_buttons = []
        cols = 4
        for i, plaza in enumerate(self.parking.plazas):
            btn = tb.Button(
                frame_plazas,
                command=lambda p=plaza: self.handle_plaza_click(p)
            )
            btn.grid(row=i // cols, column=i % cols, padx=8, pady=8, sticky="nsew")
            self.plaza_buttons.append((btn, plaza))
        for i in range(cols):
            frame_plazas.columnconfigure(i, weight=1)

        # Entrada
        entrada = tb.Labelframe(self, text="Registrar Entrada", padding=15)
        entrada.pack(fill="x", padx=15, pady=10)
        tb.Label(entrada, text="Matrícula").grid(row=0, column=0)
        self.entry_matricula = tb.Entry(entrada)
        self.entry_matricula.grid(row=0, column=1)
        tb.Label(entrada, text="Tipo").grid(row=1, column=0)
        self.combo_tipo = tb.Combobox(entrada, values=["coche", "moto"], state="readonly")
        self.combo_tipo.current(0)
        self.combo_tipo.grid(row=1, column=1)
        tb.Button(
            entrada,
            text="Iniciar Entrada",
            bootstyle="success",
            command=self.registrar_entrada
        ).grid(row=2, columnspan=2, pady=10)

        # Reserva
        reserva = tb.Labelframe(self, text="Reservar Plaza", padding=15)
        reserva.pack(fill="x", padx=15, pady=10)
        tb.Label(reserva, text="Matrícula").grid(row=0, column=0)
        self.entry_reserva = tb.Entry(reserva)
        self.entry_reserva.grid(row=0, column=1)
        tb.Label(reserva, text="Tipo").grid(row=1, column=0)
        self.combo_reserva = tb.Combobox(reserva, values=["coche", "moto"], state="readonly")
        self.combo_reserva.current(0)
        self.combo_reserva.grid(row=1, column=1)
        tb.Button(
            reserva,
            text="Iniciar Reserva",
            bootstyle="primary",
            command=self.iniciar_reserva
        ).grid(row=2, columnspan=2, pady=10)

        tb.Button(
            self,
            text="Cancelar acción",
            bootstyle="secondary",
            command=self.cancelar_pendientes
        ).pack(pady=5)

        salida = tb.Labelframe(self, text="Salida", padding=15)
        salida.pack(fill="x", padx=15, pady=10)
        tb.Label(salida, text="Código Ticket").grid(row=0, column=0)
        self.entry_codigo = tb.Entry(salida)
        self.entry_codigo.grid(row=0, column=1)
        tb.Button(
            salida,
            text="Procesar Salida",
            bootstyle="danger",
            command=self.procesar_salida
        ).grid(row=1, columnspan=2, pady=10)

        self.text_recibo = tb.Text(self, height=10, state="disabled")
        self.text_recibo.pack(fill="both", expand=True, padx=15, pady=10)

    # ---------- LÓGICA ----------
    def actualizar_dashboard(self):
        total = len(self.parking.plazas)
        libres = sum(p.estado == "libre" for p in self.parking.plazas)
        ocupadas = sum(p.estado == "ocupada" for p in self.parking.plazas)
        reservadas = sum(p.estado == "reservada" for p in self.parking.plazas)
        self.lbl_total.config(text=f"Total: {total}")
        self.lbl_libres.config(text=f"Libres: {libres}")
        self.lbl_ocupadas.config(text=f"Ocupadas: {ocupadas}")
        self.lbl_reservadas.config(text=f"Reservadas: {reservadas}")
        colores = {"libre": "success", "ocupada": "danger", "reservada": "warning"}
        for btn, plaza in self.plaza_buttons:
            texto = f"P{plaza.numero}\n{plaza.tipo}"
            if plaza.estado == "reservada":
                texto += f"\n{plaza.reserved_for}"
            elif plaza.estado == "ocupada":
                # Buscar ticket y matrícula
                matricula = "N/A"
                codigo_ticket = "N/A"
                for codigo, (p, ticket) in self.tickets_activos.items():
                    if p == plaza:
                        matricula = ticket.vehiculo.matricula
                        codigo_ticket = ticket.codigo
                        break
                texto += f"\n{matricula}\n{codigo_ticket}"
            btn.config(text=texto, bootstyle=colores[plaza.estado])

    def escribir_recibo(self, texto):
        self.text_recibo.config(state="normal")
        self.text_recibo.delete("1.0", "end")
        self.text_recibo.insert("end", texto)
        self.text_recibo.config(state="disabled")

    # ---------- EVENTOS ----------
    def handle_plaza_click(self, plaza):
        # NUEVO COMPORTAMIENTO: plaza reservada sin pedir matrícula
        if plaza.estado == "reservada" and not self.pending_vehicle and not self.pending_reservation:
            opcion = messagebox.askyesno(
                "Plaza reservada",
                f"Plaza {plaza.numero} reservada para {plaza.reserved_for}.\n\n"
                "¿Desea OCUPAR la plaza?\n"
                "(Seleccione NO para cancelar la reserva)"
            )
            if opcion:
                vehiculo = Vehiculo(plaza.reserved_for, plaza.tipo)
                plaza.ocupar()
                ticket = Ticket(vehiculo)
                self.tickets_activos[ticket.codigo] = (plaza, ticket)
                self.escribir_recibo(
                    f"ENTRADA OK\n"
                    f"Plaza: {plaza.numero}\n"
                    f"Matrícula: {vehiculo.matricula}\n"
                    f"Ticket: {ticket.codigo}"
                )
            else:
                plaza.cancelar_reserva()
                self.escribir_recibo(f"Reserva cancelada en plaza {plaza.numero}")
            self.actualizar_dashboard()
            return

        # Procesar salida si la plaza está ocupada
        if plaza.estado == "ocupada":
            # Buscar el ticket activo asociado a esta plaza
            codigo_ticket = None
            for codigo, (p, ticket) in self.tickets_activos.items():
                if p == plaza:
                    codigo_ticket = codigo
                    break
            if codigo_ticket:
                opcion = messagebox.askyesno(
                    "Procesar Salida",
                    f"Plaza {plaza.numero} está ocupada.\n"
                    f"¿Desea procesar la salida del ticket {codigo_ticket}?"
                )
                if opcion:
                    # Procesar salida: liberar plaza y eliminar ticket
                    plaza.liberar()
                    self.tickets_activos.pop(codigo_ticket)
                    self.actualizar_dashboard()
                    self.escribir_recibo(f"Salida procesada\nPlaza {plaza.numero} liberada\nTicket: {codigo_ticket}")
                return
            else:
                messagebox.showerror("Error", "No se encontró ticket activo para esta plaza")
                return

        # Reserva en curso
        if self.pending_reservation:
            mat, tipo = self.pending_reservation
            if plaza.estado == "libre" and plaza.tipo == tipo:
                plaza.reservar(mat)
                self.escribir_recibo(f"Plaza {plaza.numero} reservada para {mat}")
                self.pending_reservation = None
                self.actualizar_dashboard()
            else:
                messagebox.showwarning("Error", "Plaza no válida")
            return

        # Entrada en curso
        if self.pending_vehicle:
            v = self.pending_vehicle
            if plaza.tipo == v.tipo and (plaza.estado == "libre" or plaza.reserved_for == v.matricula):
                plaza.ocupar()
                ticket = Ticket(v)
                self.tickets_activos[ticket.codigo] = (plaza, ticket)
                self.escribir_recibo(
                    f"ENTRADA OK\n"
                    f"Plaza: {plaza.numero}\n"
                    f"Matrícula: {v.matricula}\n"
                    f"Ticket: {ticket.codigo}"
                )
                self.pending_vehicle = None
                self.actualizar_dashboard()
            else:
                messagebox.showwarning("Error", "No se puede ocupar esta plaza")
            return

        messagebox.showinfo("Información", f"Plaza {plaza.numero}\nEstado: {plaza.estado}")

    def registrar_entrada(self):
        mat = self.entry_matricula.get().strip()
        if not mat:
            return
        self.pending_vehicle = Vehiculo(mat, self.combo_tipo.get())
        self.escribir_recibo("Seleccione una plaza para ocupar")
        self.entry_matricula.delete(0, "end")

    def iniciar_reserva(self):
        mat = self.entry_reserva.get().strip()
        if not mat:
            return
        self.pending_reservation = (mat.upper(), self.combo_reserva.get())
        self.escribir_recibo("Seleccione una plaza para reservar")
        self.entry_reserva.delete(0, "end")

    def cancelar_pendientes(self):
        self.pending_vehicle = None
        self.pending_reservation = None
        self.escribir_recibo("Acción cancelada")

    def procesar_salida(self):
        codigo = self.entry_codigo.get().strip()
        if codigo not in self.tickets_activos:
            messagebox.showerror("Error", "Ticket no válido")
            return
        plaza, _ = self.tickets_activos.pop(codigo)
        plaza.liberar()
        self.actualizar_dashboard()
        self.escribir_recibo("Salida procesada\nPlaza liberada")
        self.entry_codigo.delete(0, "end")

# ===================== MAIN =====================
if __name__ == "__main__":
    parking = Parking()
    for i in range(1, 6):
        parking.agregar_plaza(Plaza(i, "coche"))
    for i in range(6, 9):
        parking.agregar_plaza(Plaza(i, "moto"))
    app = ParkingApp(parking)
    app.mainloop()