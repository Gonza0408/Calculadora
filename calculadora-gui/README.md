# Calculadora GUI 🇳🇮

Calculadora con interfaz gráfica hecha en **Python + tkinter**. Pura vida.

## Cómo usarla

```bash
python3 calculadora.py
```

Si no tenés tkinter instalado:

```bash
# Ubuntu / Debian / WSL
sudo apt install python3-tk

# macOS (con Homebrew)
brew install python-tk

# Fedora
sudo dnf install python3-tkinter
```

## Funciones

| Botón | Qué hace |
|-------|----------|
| `0-9` | Números |
| `+ − × ÷` | Operaciones básicas |
| `( )` | Paréntesis con precedencia correcta |
| `%` | Porcentaje / módulo |
| `x²` | Eleva al cuadrado |
| `√` | Raíz cuadrada |
| `=` | Evalúa la expresión |
| `C` | Limpia todo |
| `⌫` | Borra el último carácter |

## Ejemplos que soporta

- `2 + 3 * (4 - 1)` → `11` (respeta precedencia)
- `2 ** 10` → `1024` (potencias)
- `-5 + 3` → `-2` (números negativos)

## Atajos de teclado

| Tecla | Acción |
|-------|--------|
| `0-9 + - * / ( ) . %` | Insertar |
| `Enter` | Calcular (`=`) |
| `Escape` | Limpiar todo (`C`) |
| `Backspace` | Borrar último (`⌫`) |

## Modo consola (sin GUI)

Para probar el motor de cálculo sin ventana:

```bash
python3 calculadora.py --demo
```

## Seguridad

Las expresiones se evalúan con `ast` de Python estándar, **no** con
`eval()`. Solo se permiten operaciones aritméticas — no se puede ejecutar
código arbitrario pegando texto raro en la calculadora.

## Requisitos

- Python 3.8+
- tkinter (incluido en la instalación estándar de Python en la mayoría de sistemas)
