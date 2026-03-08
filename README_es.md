# Browser-Use Aplicación CLI Interactiva

[English](./README.md) | [中文](./README_zh.md) | [Español](./README_es.md)

> **🤖 Proyecto Desarrollado por IA**: Este proyecto fue desarrollado completamente por IA, después de docenas de rondas de optimización, y todos los errores fueron resueltos finalmente por **Gemini 3.1 Pro** para asegurar un funcionamiento excelente.

Una aplicación interactiva de control del navegador construida sobre la biblioteca browser-use. Controla la automatización del navegador usando comandos en lenguaje natural.

## Características

- **Control con Lenguaje Natural**: Describe tareas en inglés simple, por ejemplo, "open google", "close cookie popup", "search for Python tutorials"
- **Sesión de Navegador Persistente**: El navegador permanece abierto entre comandos, permitiendo flujos de trabajo de múltiples pasos
- **Modo Visible**: La ventana del navegador es visible para que puedas observar la automatización en tiempo real
- **Interfaz REPL**: Bucle de comandos continuo con soporte de historial
- **Manejo de Errores Robusto**: La aplicación continúa ejecutándose incluso si los comandos individuales fallan
- **Apagado Elegante**: Salida limpia con Ctrl+C o comandos exit/quit
- **Soporte Multi-LLM**: Funciona con OpenAI, Gemini, NVIDIA, o cualquier API compatible con OpenAI
- **Fallback Multi-Modelo**: Configura múltiples modelos en .env; si uno falla, cambia automáticamente al siguiente
- **Navegador Abre Inmediatamente**: El navegador se lanza al inicio y espera comandos

## Requisitos

- Python 3.10+
- Acceso a API de LLM (OpenAI o servicio compatible)

## Instalación

1. Clona o descarga los archivos del proyecto

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura el archivo `.env`:
```env
# Configuración de API de LLM
OPENAI_API_KEY=tu_api_key_aqui

# Opcional: URL base de API personalizada (por defecto: https://api.openai.com/v1)
OPENAI_API_BASE=https://api.openai.com/v1

# Opcional: Nombre del modelo (soporta múltiples modelos, separados por coma)
# Si se especifican múltiples modelos, el sistema automáticamente intentará el siguiente si uno falla
# Ejemplo: MODEL_NAME=qwen/qwen3.5-122b-a10b,deepseek-chat,gpt-4o
MODEL_NAME=gpt-4o
```

**Nota**: Puedes usar cualquier servicio compatible con OpenAI:
- NVIDIA: `OPENAI_API_BASE=https://integrate.api.nvidia.com/v1`
- Google Gemini: `OPENAI_API_BASE=https://generativelanguage.googleapis.com/v1beta/openai`
- DeepSeek: `OPENAI_API_BASE=https://api.deepseek.com/v1`
- Modelos locales (Ollama, LM Studio): `OPENAI_API_BASE=http://localhost:11434/v1`

## Uso

Ejecuta la aplicación:
```bash
python main.py
```

El navegador se lanzará automáticamente y verás un símbolo del sistema. La ventana del navegador se abrirá y esperará tus comandos.

### Opciones de Línea de Comandos

```bash
python main.py [-h] [-m {dom,screen}] [-c COMMAND]

# Opciones:
#   -h, --help            Mostrar mensaje de ayuda
#   -m, --mode {dom,screen}
#                         Modo de operación: 'dom' (solo texto) o 'screen' (con capturas/pantalla)
#                         Por defecto: screen
#   -c, --command COMMAND
#                         Ejecutar un solo comando y salir
```

### Ejemplos

```bash
# Modo interactivo (por defecto)
python main.py

# Modo de comando único
python main.py -c "ir a google.com y buscar Python"

# Usar modo DOM (solo texto, sin capturas)
python main.py -m dom

# Comando único con modo DOM
python main.py -m dom -c "¿cuál es el título de la página actual?"
```

### Comandos de Ejemplo

```
Command > go to google.com
Command > accept the cookie consent
Command > search for browser-use python library
Command > click the first result
Command > what is the current page title?
Command > go to bing.com
Command > exit
```

### Comandos Especiales

- `help` - Mostrar información de ayuda
- `status` - Mostrar estado del navegador
- `exit` / `quit` - Salir del programa
- `Ctrl+C` - Salida forzada

## Cómo Funciona

1. La aplicación inicia y configura el navegador (modo visible) y la configuración del LLM
2. Usa el Agente de browser-use para interpretar y ejecutar comandos en lenguaje natural
3. El Agente analiza el DOM de la página y decide qué acciones tomar (clic, escribir, navegar, etc.)
4. La sesión del navegador persiste entre comandos - El Agente recuerda el contexto anterior
5. Cada comando se agrega a la lista de tareas del Agente y se ejecuta secuencialmente

## Estructura del Proyecto

```
.
├── main.py # Punto de entrada principal de la aplicación
├── requirements.txt # Dependencias
├── .env # Archivo de configuración (crear esto)
├── README.md # Documentación en inglés
├── README_zh.md # Documentación en chino
├── README_es.md # Documentación en español
└── test_*.py # Archivos de prueba (opcional)
```

## Solución de Problemas

1. **Error de API Key**: Asegúrate de que el archivo `.env` existe y `OPENAI_API_KEY` está configurado correctamente
2. **Fallo al Lanzar el Navegador**: Verifica si otra instancia del navegador está ejecutándose, o intenta reiniciar
3. **Comando Falla**: Algunas páginas complejas pueden necesitar comandos más detallados; el LLM intentará interpretar
4. **Errores de Importación**: Asegúrate de haber instalado los requisitos con `pip install -r requirements.txt`
5. **Errores de Unicode en Windows**: La aplicación configura automáticamente la codificación UTF-8
6. **Errores de Análisis JSON del LLM**: La aplicación ahora incluye un LLM de respaldo y desactiva el modo de pensamiento para mejor compatibilidad con algunos modelos
7. **Estado del Navegador No Persiste**: La aplicación ahora usa `user_data_dir` para persistir cookies, sesiones de login y otro estado del navegador en el directorio `browser_data/`

## Detalles Técnicos

- **Versión de browser-use**: 0.12.1
- **Arquitectura**: Instancia única de Agente persistente con perfil de navegador `keep_alive=True`
- **Soporte multi-tarea**: Usa `agent.add_new_task()` para encolar comandos sin reiniciar el estado del navegador
- **Async/Await**: Implementación completa de async para CLI responsiva
- **Persistencia de Datos del Navegador**: Usa `user_data_dir` para almacenar el perfil del navegador en el directorio `browser_data/`, preservando cookies, sesiones de login y otro estado del navegador entre sesiones

## Notas

- La primera ejecución descarga el driver del navegador (Playwright) - esto puede tomar un momento
- Se recomienda el modo visible (`headless=False`) para depuración
- Algunos sitios web tienen medidas anti-bot - usa responsablemente y respeta los términos de servicio
- Mejor usado en entornos de prueba; evita automatizar sitios web de producción

## Una Prueba Simple y Rendimiento de Modelos

### Comando de Prueba

```bash
python main.py -c "第一步、打开这个网页（番茄小说的小说管理界面）：https://fanqienovel.com/main/writer/chapter-manage/7601645527918201918&共和国特工?type=1 。第二步、根据网页内容判断上一次发布的最新章节序号，不需要翻页，默认显示的就是一定是最新章节。计算出你要发布的新一章序号（例如上一章是130，新章节就是131）。新一章对应的本地文件路径是：C:\Code\iNovel-v2.3\data\chapters\chapter-[序号].txt （注意替换实际的新章节序号，严禁修改目录结构，如果使用工具读取时报错找不到文件就停止操作，结束流程）。第三步、点击新建章节。第四步、在章节新建页面的填入工作，规则如下：【章节序号】计算出的新章节纯数字序号填到第___章之间的那个框（第一个可输入文本框）；【标题】请使用 read_local_file 工具，设置 start_line=1, end_line=1 读取第一行内容。你需要智能提取标题部分（去除"标题：""《""》"等字样），然后填入标题框(提示："请输入标题..."，第二个可输入文本框)；【正文】请直接使用 fill_from_file 动作，指定 index 为正文编辑框（提示"请输入正文..."的那个大文本框，第三个可输入文本框）的序号，设置 file_path 为刚才的文件路径，并且设置 start_line=3（从第二行开始读取全部正文），让系统直接填充，不要尝试自己复制粘贴正文内容。第五步、填入完毕后点击下一步。后续步骤处理弹窗：弹窗类型一、问有错别字未修改，不用理会，点击提交继续。弹窗类型二、问是否进行内容风险监测，点击确定。弹窗类型三、发布设置窗口，在是否使用AI的部分选择"否"(右边那个radiobox)，不要点击确认发布，然后暂停100秒后，退出。弹窗类型四、内容检测不合格，就退出流程，停止操作。弹窗类型五、提示本地服务器版本冲突什么，不用理会。"
```

> **Nota**: Esta prueba solo funciona con modelos grandes que soportan entrada de imagen, de lo contrario definitivamente fallará.

### Resultados de Rendimiento del Modelo

| Modelo | Resultado | Tiempo |
|--------|-----------|--------|
| Gemini 2.5 Flash-lite | ✅ Aprobado (1 error corregido) | Rápido: 1:30 |
| Gemini 2.5 Flash | 🟢 Bueno | Rápido: 1:30 |
| Gemini 3.0 Flash | 🟢 Bueno | Rápido: 1:30 |
| Gemini 3.1 Flash Lite | 🟢 Bueno | Rápido: 1:15 |
| *** Proveído por ModelScope *** | | |
| Xiaomi MIMO V2 Flash | 🟢 Bueno | Lento: 3:15 |
| K2.5 | ✅ Aprobado (error no fatal) | Medio: 2:13 |
| Qwen3.5 35B | ⚠️ Apenas (error en último paso) | Rápido: 1:12 |
| Qwen3.5 27B | 🟢 Bueno | Medio: 2:35 |
| Qwen3.5 122B | ✅ Aprobado (error corregido) | Rápido: 1:25 |
| Qwen3.5 397B | ⚠️ Apenas (error en último paso) | Rápido: 1:20 |

## Licencia

MIT License