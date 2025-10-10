class Funcion:
    def __init__(self, nombre, hora, precio, id):
        self.nombre = nombre
        self.hora = hora
        self.precio = precio
        self.id = id

class plataforma:
    def __init__(self):
        self.usuarios = []
        self.funciones = []
        self.ids = {"usuarios": 1, "funciones": 1}
        

class Usuario:
    def __init__(self, id, nombre, tipo):
        self.id = id
        self.nombre = nombre
        self.tipo = tipo
        self.activo = True

    def registrar(self, nombre, tipo):
        usuario = Usuario(self.ids["usuarios"], nombre, tipo)
        self.usuarios.append(usuario)
        self.ids["usuarios"] += 1
        print(f"{nombre} registrado como {tipo}")
        print(f"Tu ID de usuario es: {usuario.id}")
        print("Contraseña por defecto: 123")
        return usuario
    
    def autenticar(self, id):
        for u in self.usuarios:
            if u.id == id and u.activo:
                return u
        return None

        

   
    def registrar_funcion(self, nombre, hora, precio, id):
        creador = self.autenticar(id)
        if creador and creador.tipo in ["admin"]:
            Funcion = Funcion(self.ids["Funcion"], nombre, hora, precio, id)
            self.funcion.append(Funcion)
            self.ids["Funciones"] += 1
            print(f"Funcion {nombre} creado")
            return Funcion
        print("Sin permisos")
        return None
    
    def buscar_funciones(self, tipo, valor):
        resultados = []
        for c in self.cursos:
            if c.activo:
                if tipo == "nombre" and valor.lower() in c.nombre.lower():
                    resultados.append(c)
            
        return resultados

    def main():
        plataforma = plataforma()
    
    
    plataforma.registrar_funcion("avengers", "Lun 3pm-7pm", "10.000", 3)

    
    while True:
        print("\n" + "="*50)
        print("Funciones")
        print("1. Ver funciones")
        print("2. Buscar funciones")
        print("3. Registrarse (nuevo usuario)")
        print("4. Salir")
        
        op = input("Opcion: ")
        
        if op == "1":
            plataforma.ver_funciones()
        elif op == "2":
            plataforma.ver_funciones()
            id_e = int(input("ID admin: "))
            id_c = int(input("ID funcion: "))
            plataforma.inscribir(id_e, id_c)
        
        elif op == "3":
            print("\nREGISTRO NUEVO USUARIO")
            nombre = input("Nombre: ")
            print("Tipo: 1. Admin")
            tipo_op = input("Opcion: ")
            tipo = {"1": "admin"}.get(tipo_op, "admin")
            nuevo_usuario = plataforma.registrar(nombre, tipo)
            print(f"Recuerda tu ID: {nuevo_usuario.id}")
        elif op == "4":
            print("Hasta luego!")
            break
        else:
            print("Opcion invalida")

    if __name__ == "__main__":
        main()

    