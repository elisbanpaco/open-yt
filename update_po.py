import os

po_file = "src/open_yt/locales/es/LC_MESSAGES/open-yt.po"
with open(po_file, "a", encoding="utf-8") as f:
    f.write('\nmsgid "Download directory"\nmsgstr "Directorio de descarga"\n\n')
    f.write('msgid "Default format"\nmsgstr "Formato por defecto"\n\n')
    f.write('msgid "Default quality"\nmsgstr "Calidad por defecto"\n\n')
    f.write('msgid "Default resolution"\nmsgstr "Resolucion por defecto"\n\n')
    f.write('msgid "Configuration (Select to edit)"\nmsgstr "Configuracion (Selecciona para editar)"\n\n')
    f.write('msgid "Looking for critical engine updates (yt-dlp)..."\nmsgstr "Buscando actualizaciones críticas para el motor (yt-dlp)..."\n\n')
    f.write('msgid "✓ Engine successfully updated and tuned. Ready to download!"\nmsgstr "✓ Motor actualizado y afinado con éxito. ¡Listo para descargar!"\n\n')
    f.write('msgid "✗ Could not update automatically. Run manually:"\nmsgstr "✗ No se pudo actualizar automáticamente. Ejecuta manualmente:"\n\n')
    f.write('msgid "✗ Fatal error trying to update:"\nmsgstr "✗ Error fatal al intentar actualizar:"\n\n')
os.system("msgfmt src/open_yt/locales/es/LC_MESSAGES/open-yt.po -o src/open_yt/locales/es/LC_MESSAGES/open-yt.mo")
