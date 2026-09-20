# Wine Quality — proyecto reproducible

Este proyecto viene de la práctica de S1, donde teníamos un CSV y dos scripts sueltos (train.py y test_train.py). Aquí lo hemos reorganizado como un paquete de Python instalable con uv, para que cualquiera pueda clonar el fork, instalarlo tal cual y que le funcione sin tener que tocar nada a mano.

# Instalación

Necesitamos tener uv instalado,hecho en anteriores clases. Desde la raíz del fork (la carpeta que se crea al hacer `git clone <urldelrepo>`, la que contiene la carpeta oculta `.git`,en mi caso especifico ~/dev/icai-muiaap-operacion-de-modelos/), entras en la carpeta del proyecto y sincronizas el entorno:

```
cd semana2/wine-quality-project
uv sync --locked
```

`uv sync` lee el `pyproject.toml` (contiene la sección dependencies = [..],donde se encuentra lo que necesitas descargar con versiones flexibles,pandas>=3.0.6 por ejemplo) y el `uv.lock`, crea (o actualiza) el entorno virtual `.venv` del proyecto, e instala ahí dentro exactamente las dependencias que necesitas (pandas, scikit-learn, etc.) más el propio paquete `wine_quality`. Con `--locked` le decimos que use tal cual las versiones ya fijadas en `uv.lock`, sin resolver versiones nuevas.

# Estructura

El CSV original está en data/raw/WineQT.csv (semana2/wine-quality-project/data/raw/WineQT.csv). El código de entrenamiento (train.py) está dentro de src/wine_quality/, que es la carpeta del paquete en sí. Los tests están aparte, en tests/test_train.py, fuera del paquete (es la forma normal de organizarlo: el código que se ejecuta de verdad va en src/, y lo que solo sirve para comprobar que funciona se queda fuera). El `pyproject.toml` tiene las dependencias del proyecto, y el `uv.lock` es el que guarda las versiones exactas que se han instalado, como ya explique antess

# Comprobaciones

Todos los comandos de esta sección se ejecutan desde `semana2/wine-quality-project` (la carpeta donde hicimos `cd` en el paso de instalación).
Para todo esto usamos --frozen, que le dice a uv "usa el entorno tal y como está bloqueado, no lo toques"Es decir,que siempre use las versiones marcadas en el `uv.lock ` sin comprobar que coincide exactamente con el pyproject.toml

Nota para mi mismo:diferencias entre --locked y --frozen

--locked: SÍ comprueba que uv.lock está sincronizado con pyproject.toml. Si detecta que no coinciden (por ejemplo, añadiste una dependencia y se te olvidó regenerar el lock), da error y para, en vez de arreglarlo por su cuenta.

--frozen: NO comprueba nada. Ni mira si uv.lock coincide con pyproject.toml, ni actualiza nada — simplemente coge el uv.lock tal cual está y lo usa, punto.

En la práctica: --locked es una alarma de seguridad ("avísame si algo no cuadra"), y --frozen es un "no preguntes, usa esto y ya" — por eso --locked se usa en el sync inicial (para pillar despistes) y --frozen en las ejecuciones del día a día (para ir rápido sin repetir esa comprobación cada vez).

 ## Entrenar el modelo:

uv run --frozen python -m wine_quality.train

Lo lanzamos como módulo (con -m) en vez de ejecutar el archivo directamente, porque así Python reconoce el paquete wine_quality igual que lo hacen los tests, y no da problemas de imports.

Esto te imprime el número de filas del dataset, cuántas variables se usan, cuántas clases hay y el F1 macro que saca el modelo en validación.

 ##Correr los tests:

uv run --frozen pytest

 ## Pasar el linter (Ruff, revisa que el código esté bien escrito):

Nota para mi mismo:Un linter es una herramienta que lee tu código sin ejecutarlo y busca problemas de estilo o errores típicos: variables que declaras y nunca usas, imports que sobran, líneas demasiado largas, espacios mal puestos, convenciones de nombres no seguidas, etc. No comprueba que el resultado sea "correcto" (para eso están los tests), sino que el código esté bien escrito y sea consistente. 

uv run --frozen ruff check .