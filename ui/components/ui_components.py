import streamlit as st

def render_header():
    header_col1, header_col2, header_col3 = st.columns(3, gap="large")
    with header_col2:
        st.image("https://ik.imagekit.io/indesign/optisales/optisales_logo.png?updatedAt=1727501703582")
    st.write(" ")
    st.html(
        "<h1 style='text-align: center; padding: 20px; line-height: 1.5; max-width: 1200px; margin: 40px auto;'>"
        "Automatiza tus ventas 24/7 con agentes de IA, optimizando cada proceso mientras tu equipo se enfoca en cerrar negocios."
        "</h1>"
    )


def render_features():
  st.html(
      """
      <div style='
          display: flex;
          flex-wrap: wrap;
          justify-content: center;
          gap: 20px;
          margin: 40px 0;
      '>
          <!-- Característica 1 -->
          <div style='
              background-color: white;
              padding: 20px;
              border-radius: 15px;
              box-shadow: 0 4px 6px rgba(0,0,0,0.1);
              text-align: center;
              flex: 1 1 calc(33.333% - 40px);
              box-sizing: border-box;
              max-width: 300px;
          '>
              <h2>Automatización 24/7</h2>
              <p>Optimiza tus procesos con agentes de IA que trabajan sin descanso.</p>
          </div>

          <!-- Característica 2 -->
          <div style='
              background-color: white;
              padding: 20px;
              border-radius: 15px;
              box-shadow: 0 4px 6px rgba(0,0,0,0.1);
              text-align: center;
              flex: 1 1 calc(33.333% - 40px);
              box-sizing: border-box;
              max-width: 300px;
          '>
              <h2>Automatización de Emails</h2>
              <p>Envía correos electrónicos automatizados a tus clientes potenciales.</p>
          </div>

          <!-- Característica 3 -->
          <div style='
              background-color: white;
              padding: 20px;
              border-radius: 15px;
              box-shadow: 0 4px 6px rgba(0,0,0,0.1);
              text-align: center;
              flex: 1 1 calc(33.333% - 40px);
              box-sizing: border-box;
              max-width: 300px;
          '>
              <h2>Optimización de Procesos</h2>
              <p>Mejora cada paso de tu proceso de ventas con inteligencia artificial.</p>
          </div>

          <!-- Característica 4 -->
          <div style='
              background-color: white;
              padding: 20px;
              border-radius: 15px;
              box-shadow: 0 4px 6px rgba(0,0,0,0.1);
              text-align: center;
              flex: 1 1 calc(33.333% - 40px);
              box-sizing: border-box;
              max-width: 300px;
          '>
              <h2>Automatización de Redes Sociales</h2>
              <p>Gestiona y programa tus publicaciones en redes sociales de forma automática.</p>
          </div>

          <!-- Característica 5 -->
          <div style='
              background-color: white;
              padding: 20px;
              border-radius: 15px;
              box-shadow: 0 4px 6px rgba(0,0,0,0.1);
              text-align: center;
              flex: 1 1 calc(33.333% - 40px);
              box-sizing: border-box;
              max-width: 300px;
          '>
              <h2>Extracción de Leads</h2>
              <p>Obtén información valiosa de potenciales clientes de manera eficiente.</p>
          </div>

      </div>
      """
  )
