import streamlit as st
from streamlit_oauth import OAuth2Component
from streamlit_option_menu import option_menu
from generar_qr import generar_qrs  # Asegúrate de que esta función esté bien definida
import json

# Leer configuración desde secrets.toml
redirect_uri = st.secrets["auth"]["redirect_uri"]
client_id = st.secrets["auth.google"]["client_id"]
client_secret = st.secrets["auth.google"]["client_secret"]
server_metadata_url = st.secrets["auth.google"]["server_metadata_url"]
cookie_secret = st.secrets["auth"]["cookie_secret"]

# Inicializar componente OAuth2
oauth2 = OAuth2Component(
    client_id=client_id,
    client_secret=client_secret,
    auth_uri=server_metadata_url,
    token_uri="https://oauth2.googleapis.com/token",
    redirect_uri=redirect_uri,
    scope="openid email profile",
    cookie_secret=cookie_secret,
)

# Función para obtener información del usuario
def obtener_info_usuario():
    token = oauth2.get_token()
    if token is not None:
        user_info = oauth2.get_user_info(token)
        return user_info
    return None

# Diccionario de roles autorizados desde secrets
roles_autorizados = json.loads(st.secrets["roles_autorizados"]["data"])

# MAIN
def main():
    st.set_page_config(page_title="CMCH App", layout="wide")
    st.sidebar.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Cayetano_Heredia_University_logo.png/800px-Cayetano_Heredia_University_logo.png",
        width=180,
    )

    user_info = obtener_info_usuario()

    if user_info is None:
        st.warning("🔒 Por favor, inicia sesión con tu cuenta autorizada de Google.")
        st.stop()

    user_email = user_info.get("email", "")
    if user_email not in roles_autorizados:
        st.error("🚫 No tienes permiso para acceder a esta aplicación.")
        st.stop()

    rol_nombre, rol_nivel = roles_autorizados[user_email]
    st.sidebar.success(f"Sesión iniciada como: **{rol_nombre}**")

    menu = option_menu(
        menu_title="Menú Principal",
        options=[
            "Inicio",
            "Ver Base de Datos",
            "Asignación de Tareas",
            "Gestión de Usuarios",
            "Generar QR",
            "Perfil",
            "Configuración",
        ],
        icons=["house", "database", "clipboard-check", "people", "qr-code", "person", "gear"],
        default_index=0,
    )

    if menu == "Inicio":
        st.title("🏠 Bienvenido/a")
        st.write("Este es el panel principal del sistema del Departamento de Ingeniería Clínica.")
        st.info("Selecciona una opción del menú para comenzar.")

    elif menu == "Ver Base de Datos":
        st.title("📂 Base de Datos")
        st.write("Aquí iría la lógica para visualizar registros según tu rol.")

    elif menu == "Asignación de Tareas":
        if rol_nivel >= 2:
            st.title("✅ Asignación de Tareas")
            st.write("Aquí iría la lógica para asignar y visualizar tareas.")
        else:
            st.warning("🚫 No tienes permisos para ver esta sección.")

    elif menu == "Gestión de Usuarios":
        if rol_nivel >= 4:
            st.title("👥 Gestión de Usuarios")
            st.write("Aquí se podrían añadir, modificar o eliminar usuarios.")
        else:
            st.warning("🚫 Solo los ingenieros profesionales o jefes pueden acceder.")

    elif menu == "Generar QR":
        if rol_nivel >= 3:
            st.title("📲 Generar Código QR")
            generar_qrs()
        else:
            st.warning("🚫 Solo los ingenieros pueden generar códigos QR.")

    elif menu == "Perfil":
        st.title("👤 Mi Perfil")
        st.write(f"**Rol:** {rol_nombre}")
        st.write(f"**Correo electrónico:** {user_email}")

    elif menu == "Configuración":
        if rol_nivel >= 5:
            st.title("⚙️ Configuración Avanzada")
            st.write("Opciones para el jefe del departamento.")
        else:
            st.warning("🚫 Solo el jefe del departamento puede acceder.")

if __name__ == "__main__":
    main()
