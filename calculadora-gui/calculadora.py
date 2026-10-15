#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculadora GUI - hecha con tkinter 🇳🇮
Autor: OpenCode para Gonzalo (nica edition)

Segura: usa `ast` para evaluar expresiones, nunca `eval()` pelado.
"""

import ast
import math
import operator
import tkinter as tk
from tkinter import font as tkfont


# ---------------------------------------------------------------------------
# Motor de cálculo seguro (AST)
# ---------------------------------------------------------------------------

class ErrorCalculo(Exception):
    """Excepción propia para errores de la calculadora."""
    pass


# Operadores binarios soportados -> función de `operator`
_BINARIOS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

# Operadores unarios -> función de `operator`
_UNARIOS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _evaluar_nodo(nodo):
    """Evalúa recursivamente un nodo del AST. Solo operaciones aritméticas."""
    if isinstance(nodo, ast.Expression):
        return _evaluar_nodo(nodo.body)

    if isinstance(nodo, ast.Constant):  # números literales
        if isinstance(nodo.value, (int, float)):
            return nodo.value
        raise ErrorCalculo("solo se permiten números")

    if isinstance(nodo, ast.BinOp):
        tipo = type(nodo.op)
        if tipo not in _BINARIOS:
            raise ErrorCalculo("operador no soportado")
        izq = _evaluar_nodo(nodo.left)
        der = _evaluar_nodo(nodo.right)
        try:
            return _BINARIOS[tipo](izq, der)
        except ZeroDivisionError:
            raise ErrorCalculo("División entre cero")

    if isinstance(nodo, ast.UnaryOp):
        tipo = type(nodo.op)
        if tipo not in _UNARIOS:
            raise ErrorCalculo("operador no soportado")
        return _UNARIOS[tipo](_evaluar_nodo(nodo.operand))

    raise ErrorCalculo("expresión no válida")


def calcular(expresion: str) -> float:
    """
    Evalúa una expresión aritmética de forma segura.
    Ej: "2 + 3 * (4 - 1)" -> 11
    """
    if not expresion or not expresion.strip():
        raise ErrorCalculo("expresión vacía")

    try:
        arbol = ast.parse(expresion, mode="eval")
    except SyntaxError:
        raise ErrorCalculo("sintaxis inválida")

    resultado = _evaluar_nodo(arbol)

    if isinstance(resultado, complex):
        raise ErrorCalculo("resultado complejo no soportado")

    return float(resultado)


def formatear(numero: float) -> str:
    """Formatea el número para mostrarlo lindo en la pantalla."""
    if numero == int(numero) and abs(numero) < 1e15:
        return str(int(numero))
    # Usa notación científica solo para números muy grandes/chiquitos
    if abs(numero) >= 1e12 or (numero != 0 and abs(numero) < 1e-9):
        return f"{numero:.8g}"
    return f"{numero:.10g}"


# ---------------------------------------------------------------------------
# Interfaz gráfica
# ---------------------------------------------------------------------------

class Calculadora(tk.Tk):
    # Paleta de colores
    FONDO = "#1c1c1e"        # casi negro, estilo oscuro
    PANTALLA_BG = "#2c2c2e"  # gris oscuro
    TEXTO = "#ffffff"
    NUM_BG = "#505052"       # botones numéricos
    NUM_ACTIVO = "#707074"
    OP_BG = "#ff9f0a"        # operadores naranja estilo iOS
    OP_ACTIVO = "#ffc46b"
    UTIL_BG = "#3a3a3c"      # utilidades (C, ⌫, etc.)
    UTIL_ACTIVO = "#5a5a5e"

    def __init__(self):
        super().__init__()
        self.title("Calculadora 🇳🇮")
        self.configure(bg=self.FONDO)
        self.resizable(False, False)
        self.minsize(320, 460)

        # Estado
        self.expresion = ""      # lo que el usuario tipea
        self.ultimo_resultado = None
        self.sobreescribir = False  # true tras apretar "="

        self._configurar_fuentes()
        self._crear_pantalla()
        self._crear_teclado()
        self._atajar_teclado_fisico()

        # Centrar en pantalla
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_reqwidth()) // 2
        y = (self.winfo_screenheight() - self.winfo_reqheight()) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    # ------------------------------------------------------------------ UI
    def _configurar_fuentes(self):
        self.fuente_pantalla = tkfont.Font(family="Helvetica", size=32, weight="bold")
        self.fuente_historial = tkfont.Font(family="Helvetica", size=12)
        self.fuente_boton = tkfont.Font(family="Helvetica", size=18, weight="bold")

    def _crear_pantalla(self):
        marco = tk.Frame(self, bg=self.FONDO)
        marco.pack(fill="both", expand=True, padx=12, pady=(12, 6))

        # Línea de historial (expresión anterior)
        self.historial = tk.Label(
            marco, text="", anchor="e", bg=self.PANTALLA_BG, fg="#8e8e93",
            font=self.fuente_historial, padx=16, pady=4,
        )
        self.historial.pack(fill="x")

        # Pantalla principal
        self.pantalla = tk.Label(
            marco, text="0", anchor="e", bg=self.PANTALLA_BG, fg=self.TEXTO,
            font=self.fuente_pantalla, padx=16, pady=10,
        )
        self.pantalla.pack(fill="x", pady=(0, 12))

    def _crear_boton(self, parent, texto, fila, columna, bg, comando, valor=None,
                     columnspan=1, rowspan=1, **kwargs):
        """
        Crea un botón. `texto` es lo que se muestra; `valor` es lo que se
        pasa a `comando` al presionarlo (para self.insertar).
        `columnspan` y `rowspan` se pasan a .grid(), no al botón.
        """
        if valor is not None:
            accion = lambda v=valor: comando(v)
        else:
            accion = comando
        btn = tk.Button(
            parent, text=texto, font=self.fuente_boton,
            bg=bg, fg=self.TEXTO, activeforeground=self.TEXTO,
            relief="flat", bd=0, cursor="hand2", command=accion,
            **kwargs,
        )
        btn.grid(row=fila, column=columna, sticky="nsew", padx=3, pady=3, ipady=10,
                 columnspan=columnspan, rowspan=rowspan)
        # Efecto al presionar
        activo = self._color_activo(bg)
        btn.bind("<ButtonPress-1>", lambda e, b=btn, a=activo: b.configure(bg=a))
        btn.bind("<ButtonRelease-1>", lambda e, b=btn, o=bg: b.configure(bg=o))
        return btn

    def _color_activo(self, bg):
        return {
            self.NUM_BG: self.NUM_ACTIVO,
            self.OP_BG: self.OP_ACTIVO,
            self.UTIL_BG: self.UTIL_ACTIVO,
        }.get(bg, bg)

    def _crear_teclado(self):
        grilla = tk.Frame(self, bg=self.FONDO)
        grilla.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        for i in range(5):
            grilla.columnconfigure(i, weight=1, uniform="col")
        for i in range(5):
            grilla.rowconfigure(i, weight=1)

        U = self.UTIL_BG   # utilidades
        N = self.NUM_BG    # números
        O = self.OP_BG    # operadores

        # Fila 0: C, ⌫, %, ÷
        self._crear_boton(grilla, "C",  0, 0, U, self.limpiar_todo)
        self._crear_boton(grilla, "⌫",  0, 1, U, self.borrar_uno)
        self._crear_boton(grilla, "%",  0, 2, U, self.insertar, valor="%")
        self._crear_boton(grilla, "÷",  0, 3, O, self.insertar, valor="/")

        # Fila 1: ( ) x² ×
        self._crear_boton(grilla, "(",  1, 0, U, self.insertar, valor="(")
        self._crear_boton(grilla, ")",  1, 1, U, self.insertar, valor=")")
        self._crear_boton(grilla, "x²", 1, 2, U, self.potencia)
        self._crear_boton(grilla, "×",  1, 3, O, self.insertar, valor="*")

        # Fila 2: 7 8 9 −
        self._crear_boton(grilla, "7",  2, 0, N, self.insertar, valor="7")
        self._crear_boton(grilla, "8",  2, 1, N, self.insertar, valor="8")
        self._crear_boton(grilla, "9",  2, 2, N, self.insertar, valor="9")
        self._crear_boton(grilla, "−",  2, 3, O, self.insertar, valor="-")

        # Fila 3: 4 5 6 +
        self._crear_boton(grilla, "4",  3, 0, N, self.insertar, valor="4")
        self._crear_boton(grilla, "5",  3, 1, N, self.insertar, valor="5")
        self._crear_boton(grilla, "6",  3, 2, N, self.insertar, valor="6")
        self._crear_boton(grilla, "+",  3, 3, O, self.insertar, valor="+")

        # Fila 4: 1 2 3 =
        self._crear_boton(grilla, "1",  4, 0, N, self.insertar, valor="1")
        self._crear_boton(grilla, "2",  4, 1, N, self.insertar, valor="2")
        self._crear_boton(grilla, "3",  4, 2, N, self.insertar, valor="3")
        self._crear_boton(grilla, "=",  4, 3, O, self.evaluar, rowspan=2)

        # Fila 5: 0 (doble ancho) y .
        cero = self._crear_boton(grilla, "0",  5, 0, N, self.insertar, valor="0", columnspan=2)
        cero.configure(width=1)
        self._crear_boton(grilla, ".",  5, 2, N, self.insertar, valor=".")
        self._crear_boton(grilla, "√",  5, 3, O, self.raiz)

    def _atajar_teclado_fisico(self):
        self.bind("<Key>", self._on_key)
        self.bind("<Return>", lambda e: self.evaluar())
        self.bind("<KP_Enter>", lambda e: self.evaluar())
        self.bind("<Escape>", lambda e: self.limpiar_todo())
        self.bind("<BackSpace>", lambda e: self.borrar_uno())

    def _on_key(self, evento):
        """Mapea el teclado físico a acciones."""
        char = evento.char
        simbolos_validos = set("0123456789+-*/().%")
        if char in simbolos_validos:
            self.insertar(texto=char)

    # ------------------------------------------------------------- Lógica
    def _actualizar_pantalla(self):
        texto = self.expresion if self.expresion else "0"
        self.pantalla.configure(text=texto)
        self._ajustar_fuente()

    def _ajustar_fuente(self):
        """Achica la fuente si la expresión es larga para que entre en pantalla."""
        largo = len(self.pantalla.cget("text"))
        if largo <= 12:
            tamaño = 32
        elif largo <= 18:
            tamaño = 24
        elif largo <= 26:
            tamaño = 18
        else:
            tamaño = 13
        self.fuente_pantalla.configure(size=tamaño)

    def insertar(self, texto):
        """Agrega un símbolo a la expresión actual."""
        if self.sobreescribir:
            # Si el usuario aprieta un número después del "=", empieza de cero
            if texto.isdigit() or texto == "(":
                self.expresion = ""
            self.sobreescribir = False
        self.expresion += texto
        self._actualizar_pantalla()

    def limpiar_todo(self):
        """Botón C: borra todo."""
        self.expresion = ""
        self.ultimo_resultado = None
        self.sobreescribir = False
        self.historial.configure(text="")
        self._actualizar_pantalla()

    def borrar_uno(self):
        """Botón ⌫: borra el último carácter."""
        if self.sobreescribir:
            self.sobreescribir = False
        self.expresion = self.expresion[:-1]
        self._actualizar_pantalla()

    def potencia(self):
        """Eleva al cuadrado el último número ingresado."""
        self.insertar(texto="**2")

    def raiz(self):
        """Raíz cuadrada del último número ingresado."""
        try:
            valor = calcular(self.expresion) if self.expresion else 0
        except ErrorCalculo:
            valor = 0
        if valor < 0:
            self._mostrar_error("Raíz de negativo")
            return
        raiz = math.sqrt(valor)
        self.historial.configure(text=f"√({formatear(valor)})")
        self.expresion = formatear(raiz)
        self.sobreescribir = True
        self._actualizar_pantalla()

    def evaluar(self):
        """Evalúa la expresión y muestra el resultado."""
        if not self.expresion:
            return
        try:
            resultado = calcular(self.expresion)
        except ErrorCalculo as error:
            self._mostrar_error(str(error))
            return
        except OverflowError:
            self._mostrar_error("desbordamiento")
            return

        self.historial.configure(text=f"{self.expresion} =")
        self.ultimo_resultado = resultado
        self.expresion = formatear(resultado)
        self.sobreescribir = True
        self._actualizar_pantalla()

    def _mostrar_error(self, mensaje):
        self.historial.configure(text=self.expresion)
        self.pantalla.configure(text="Error")
        self.fuente_pantalla.configure(size=28)
        self.expresion = ""
        self.after(1200, self._actualizar_pantalla)


# ---------------------------------------------------------------------------

def _demo_consola():
    """Demo rápida sin GUI para probar el motor de cálculo."""
    print("Probando el motor de cálculo (sin GUI):")
    pruebas = [
        "2 + 3 * (4 - 1)",
        "10 / 4",
        "2 ** 10",
        "-5 + 3",
        "7 % 3",
        "100 / 0",
    ]
    for expresion in pruebas:
        try:
            print(f"  {expresion:22s} = {formatear(calcular(expresion))}")
        except ErrorCalculo as error:
            print(f"  {expresion:22s} -> Error: {error}")


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        _demo_consola()
    else:
        app = Calculadora()
        app.mainloop()
