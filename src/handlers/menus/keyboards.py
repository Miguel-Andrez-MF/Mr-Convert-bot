from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# =============================================================================
# TECLADOS PRINCIPALES
# =============================================================================

# Menú principal
MAIN_MENU_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎨 Edición de Imágenes", callback_data="menu_images")],
    [InlineKeyboardButton("📄 Conversión de Documentos", callback_data="menu_documents")],
    [InlineKeyboardButton("ℹ️ Ayuda", callback_data="help")]
])

# Menú de imágenes  
IMAGES_MENU_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔄 Convertir Formato", callback_data="convert_format")],
    [InlineKeyboardButton("📏 Redimensionar", callback_data="resize_image")],
    [InlineKeyboardButton("⚡ Cambiar Calidad", callback_data="change_quality")],
    [InlineKeyboardButton("🎭 Aplicar Filtros", callback_data="apply_filters")],
    [InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="back_to_main")]
])

# Menú de documentos
DOCUMENTS_MENU_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("📄➡️🖼️ PDF a Imágenes", callback_data="pdf_to_images")],
    [InlineKeyboardButton("🖼️➡️📄 Imágenes a PDF", callback_data="images_to_pdf")],
    [InlineKeyboardButton("🗜️ Comprimir PDF", callback_data="compress_pdf")],
    [InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="back_to_main")]
])

# Menú de ayuda
HELP_MENU_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="back_to_main")]
])

# Menú de continuación
CONTINUE_MENU_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔄 Repetir Operación", callback_data="repeat_operation")],
    [InlineKeyboardButton("🎨 Edición de Imágenes", callback_data="menu_images")],
    [InlineKeyboardButton("📄 Conversión de Documentos", callback_data="menu_documents")],
    [InlineKeyboardButton("🏠 Menú Principal", callback_data="back_to_main")]
])

# =============================================================================
# MENSAJES DE LOS MENÚS
# =============================================================================

WELCOME_MESSAGE = (
    "👋 ¡Hola! Soy **Mr.Convert**\n\n"
    "🤖 Tu asistente personal para conversión y edición de archivos\n\n"
    "Selecciona una categoría para comenzar:"
)

IMAGES_MENU_MESSAGE = "🎨 **Edición de Imágenes**\n\nSelecciona la operación que deseas realizar:"

DOCUMENTS_MENU_MESSAGE = "📄 **Conversión de Documentos**\n\nSelecciona la operación que deseas realizar:"

SUCCESS_MESSAGE = (
    "✅ **¡Operación completada!**\n\n"
    "¿Qué te gustaría hacer ahora?"
)

HELP_MESSAGE = (
    "ℹ️ **Ayuda - Mr.Convert**\n\n"
    "🎨 **Edición de Imágenes:**\n"
    "• Convierte entre PNG, JPEG y otros formatos\n"
    "• Cambia el tamaño de tus imágenes\n"
    "• Ajusta la calidad para reducir peso\n"
    "• Aplica filtros artísticos\n\n"
    "📄 **Conversión de Documentos:**\n"
    "• Convierte PDF a imágenes individuales\n"
    "• Combina imágenes en un solo PDF\n"
    "• Comprime PDFs para reducir tamaño\n\n"
    "💡 **Consejos:**\n"
    "• Envía archivos de hasta 20MB\n"
    "• Los archivos temporales se eliminan automáticamente\n"
    "• Usa /start para volver al menú principal"
)

# =============================================================================
# MENSAJES DE INSTRUCCIONES
# =============================================================================

CONVERT_FORMAT_MESSAGE = (
    "🔄 **Conversión de Formato**\n\n"
    "📸 Envía una imagen y la convertiré automáticamente:\n"
    "• PNG → JPEG\n"
    "• JPEG → PNG\n"
    "• Otros formatos compatibles"
)

RESIZE_IMAGE_MESSAGE = (
    "📏 **Redimensionar Imagen**\n\n"
    "📸 Envía una imagen para cambiar su tamaño\n"
    "Podrás elegir dimensiones personalizadas o usar presets"
)

CHANGE_QUALITY_MESSAGE = (
    "⚡ **Cambiar Calidad**\n\n"
    "📸 Envía una imagen para ajustar su calidad\n"
    "Reduce el tamaño del archivo manteniendo buena resolución"
)

APPLY_FILTERS_MESSAGE = (
    "🎭 **Aplicar Filtros**\n\n"
    "📸 Envía una imagen para aplicar efectos:\n"
    "• Blanco y negro\n"
    "• Sepia vintage\n"
    "• Y más filtros artísticos"
)

PDF_TO_IMAGES_MESSAGE = (
    "📄➡️🖼️ **PDF a Imágenes**\n\n"
    "📎 Envía un archivo PDF y lo convertiré en imágenes\n"
)

IMAGES_TO_PDF_MESSAGE = (
    "🖼️➡️📄 **Imágenes a PDF**\n\n"
    "📸 Envía múltiples imágenes y las combinaré en un PDF\n"
    "Puedes enviar una o varias imágenes"
)

COMPRESS_PDF_MESSAGE = (
    "🗜️ **Comprimir PDF**\n\n"
    "📎 Envía un PDF para reducir su tamaño\n"
    "Manteniendo una calidad aceptable"
)