import streamlit as st
from streamlit_option_menu import option_menu
from base_datos import mostrar_base_datos
from asignar_tareas import mostrar_tareas_asignadas, mostrar_todas_las_tareas, asignar_tarea_form
import json

# Cargar roles desde secrets.toml
roles_data = st.secrets["roles_autorizados"]["data"]
ROLES = json.loads(roles_data)

st.set_page_config(page_title="Sistema de Inventario", layout="wide")
st.title("PLATAFORMA DE INGENIERÍA CLÍNICA")

# Inicializar variables en session_state
if "input_email" not in st.session_state:
    st.session_state["input_email"] = ""
if "login_attempt" not in st.session_state:
    st.session_state["login_attempt"] = False
if "user_authenticated" not in st.session_state:
    st.session_state["user_authenticated"] = False
if "reload_trigger" not in st.session_state:
    st.session_state["reload_trigger"] = False

def login():
    st.session_state["login_attempt"] = True

def logout():
    st.session_state.clear()
    st.session_state["reload_trigger"] = not st.session_state.get("reload_trigger", False)

# Si no está autenticado, mostrar login
if not st.session_state["user_authenticated"]:
    email_input = st.text_input(
        "Ingresa tu correo institucional para autenticar",
        value=st.session_state["input_email"],
        key="input_email"
    )
    if st.button("Ingresar"):
        login()

    if st.session_state["login_attempt"]:
        if st.session_state["input_email"] in ROLES:
            st.session_state["user_authenticated"] = True
            st.session_state["email"] = st.session_state["input_email"]
            st.session_state["login_attempt"] = False
            # Toggle para forzar recarga sin experimental_rerun
            st.session_state["reload_trigger"] = not st.session_state["reload_trigger"]
            st.experimental_rerun()
        else:
            st.error("Correo no autorizado")
            st.session_state["login_attempt"] = False
    st.stop()

email = st.session_state["email"]
rol_info = ROLES.get(email)

if rol_info is None:
    st.error("🚫 Acceso denegado. Tu cuenta no está autorizada.")
    st.stop()

role, rol_nivel = rol_info

with st.sidebar:
    st.markdown(f"👤 **{email}**\n🛡️ Rol: `{role}`")
    menu = option_menu(
        menu_title="Menú Principal",
        options=["Inicio", "Ver Base de Datos", "Asignación de Tareas", "Gestión de Usuarios", "Perfil", "Configuración"],
        icons=["house", "database", "clipboard-check", "people", "person", "gear"],
        default_index=0
    )
    if st.button("Cerrar sesión"):
        logout()
        st.experimental_rerun()

# Sección inicio
if menu == "Inicio":
    st.title("🏥 Bienvenido al Sistema de Inventario")
    st.write("Navega usando el menú lateral para ver y gestionar los equipos médicos.")

# Base de datos
elif menu == "Ver Base de Datos":
    mostrar_base_datos()

# Tareas
elif menu == "Asignación de Tareas":
    st.title("🗂️ Asignación de Tareas")
    if rol_nivel in [1, 2]:
        mostrar_tareas_asignadas(email)
    elif rol_nivel >= 3:
        mostrar_todas_las_tareas()
        asignar_tarea_form()
    else:
        st.warning("🔒 Tu rol actual no tiene acceso a tareas asignadas.")

# Gestión de Usuarios solo para jefe (nivel 5)
elif menu == "Gestión de Usuarios":
    if rol_nivel == 5:
        from gestion_usuarios import gestion_usuarios_app
        gestion_usuarios_app(ROLES)
    else:
        st.warning("🚫 No tienes permiso para acceder a esta sección.")

# Perfil
elif menu == "Perfil":
    st.title("👤 Perfil del Usuario")
    st.write(f"Correo: {email}")
    st.write(f"Rol: {role}")

# Configuración
elif menu == "Configuración":
    st.title("⚙️ Configuración")
    st.write("Aquí irán las opciones de configuración personalizadas.")
