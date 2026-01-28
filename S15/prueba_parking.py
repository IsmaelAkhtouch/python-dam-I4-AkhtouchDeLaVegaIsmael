from datetime import datetime, timedelta
import uuid

class Plaza:
    def __init__(self, numero, tipo):
        self.numero = numero
        self.tipo = tipo
        self.estado = "libre"  # libre, ocupada, reservada

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

    def __str__(self):
        return f"Plaza {self.numero} ({self.tipo}) - {self.estado}"

class Vehiculo:
    def __init__(self, matricula, tipo):
        self.matricula = matricula
        self.tipo = tipo

    def obtener_tipo(self):
        return self.tipo

class Reserva:
    def __init__(self, vehiculo, plaza):
        self.vehiculo = vehiculo
        self.plaza = plaza
        self.hora_reserva = datetime.now()
        self.confirmada = False

    def confirmar_reserva(self):
        if self.plaza.reservar():
            self.confirmada = True
            return True
        return False

    def cancelar_reserva(self):
        if self.confirmada:
            self.plaza.liberar()
            self.confirmada = False

class Ticket:
    def __init__(self, vehiculo):
        self.codigo = str(uuid.uuid4())
        self.vehiculo = vehiculo
        self.hora_entrada = datetime.now()
        self.hora_salida = None

    def validar(self):
        return self.hora_salida is None

    def registrar_salida(self):
        if self.hora_salida is None:
            self.hora_salida = datetime.now()

    def calcular_tiempo(self):
        if self.hora_salida:
            return self.hora_salida - self.hora_entrada
        return datetime.now() - self.hora_entrada

class Pago:
    def __init__(self, ticket, importe, metodo_pago):
        self.ticket = ticket
        self.importe = importe
        self.metodo_pago = metodo_pago
        self.fecha_hora = datetime.now()

    def procesar_pago(self):
        # Aquí podríamos simular procesamiento real
        print(f"Pago de {self.importe}€ procesado con {self.metodo_pago}")

    def emitir_recibo(self):
        return (f"Recibo:\nTicket: {self.ticket.codigo}\nImporte: {self.importe}€\n"
                f"Método: {self.metodo_pago}\nFecha: {self.fecha_hora}")

class Parking:
    def __init__(self):
        self.plazas = []
        self.reservas = []
        self.tickets = []
        self.pagos = []
        self.tarifas = {"coche": 2.5, "moto": 1.5}  # €/hora

    def agregar_plaza(self, plaza):
        self.plazas.append(plaza)

    def mostrar_plazas_libres(self):
        libres = [p for p in self.plazas if p.estado == "libre"]
        for plaza in libres:
            print(plaza)

    def reservar_plaza(self, vehiculo):
        for plaza in self.plazas:
            if plaza.tipo == vehiculo.obtener_tipo() and plaza.estado == "libre":
                reserva = Reserva(vehiculo, plaza)
                if reserva.confirmar_reserva():
                    self.reservas.append(reserva)
                    print(f"Reserva confirmada para {vehiculo.matricula} en plaza {plaza.numero}")
                    return reserva
        print("No hay plazas libres disponibles para este tipo de vehículo.")
        return None

    def liberar_plaza(self, plaza_numero):
        for plaza in self.plazas:
            if plaza.numero == plaza_numero:
                plaza.liberar()
                print(f"Plaza {plaza_numero} liberada.")
                return True
        print(f"No se encontró la plaza {plaza_numero}.")
        return False

    def calcular_tarifa(self, vehiculo, tiempo):
        tarifa_hora = self.tarifas.get(vehiculo.obtener_tipo(), 2)
        horas = tiempo.total_seconds() / 3600
        return round(tarifa_hora * horas, 2)

    def generar_ticket(self, vehiculo):
        ticket = Ticket(vehiculo)
        self.tickets.append(ticket)
        print(f"Ticket generado para vehículo {vehiculo.matricula}, código {ticket.codigo}")
        return ticket

    def registrar_pago(self, ticket, importe, metodo_pago):
        pago = Pago(ticket, importe, metodo_pago)
        pago.procesar_pago()
        self.pagos.append(pago)
        print(pago.emitir_recibo())
        return pago

# Ejemplo de uso:
if __name__ == "__main__":
    parking = Parking()
    # Agregar plazas
    parking.agregar_plaza(Plaza(1, "coche"))
    parking.agregar_plaza(Plaza(2, "moto"))
    parking.agregar_plaza(Plaza(3, "coche"))

    parking.mostrar_plazas_libres()

    # Crear vehículo
    v1 = Vehiculo("ABC123", "coche")
    reserva = parking.reservar_plaza(v1)

    # Simular entrada y salida
    ticket = parking.generar_ticket(v1)
    # Simular espera de 90 minutos
    ticket.hora_entrada -= timedelta(minutes=90)
    ticket.registrar_salida()

    tiempo = ticket.calcular_tiempo()
    tarifa = parking.calcular_tarifa(v1, tiempo)
    parking.registrar_pago(ticket, tarifa, "tarjeta")

    parking.liberar_plaza(1)
    parking.mostrar_plazas_libres()