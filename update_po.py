import os

po_file = "src/open_yt/locales/es/LC_MESSAGES/open-yt.po"
with open(po_file, "a", encoding="utf-8") as f:
    f.write('\nmsgid "Download directory"\nmsgstr "Directorio de descarga"\n\n')
    f.write('msgid "Default format"\nmsgstr "Formato por defecto"\n\n')
    f.write('msgid "Default quality"\nmsgstr "Calidad por defecto"\n\n')
    f.write('msgid "Default resolution"\nmsgstr "Resolucion por defecto"\n\n')
    f.write('msgid "Configuration (Select to edit)"\nmsgstr "Configuracion (Selecciona para editar)"\n\n')

os.system("msgfmt src/open_yt/locales/es/LC_MESSAGES/open-yt.po -o src/open_yt/locales/es/LC_MESSAGES/open-yt.mo")
