import gettext
import os
import locale

# Ruta donde estarán los archivos de traducción (locales/es/LC_MESSAGES/open-yt.mo)
localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locales')

# Intentamos obtener el idioma del sistema del usuario
try:
    system_lang = locale.getdefaultlocale()[0]
except Exception:
    system_lang = "en_US"

# Configuramos gettext
# domain es el nombre del archivo .mo (open-yt.mo)
translation = gettext.translation(
    domain='open-yt',
    localedir=localedir,
    languages=[system_lang, 'en'],
    fallback=True
)

# Exponemos la función `_` que se usará en todo el proyecto
_ = translation.gettext
