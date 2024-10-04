import streamlit as st

def render_header(translations):
    header_col1, header_col2, header_col3 = st.columns(3, gap="large")
    with header_col2:
        st.image("https://ik.imagekit.io/indesign/optisales/optisales_logo.png?updatedAt=1727501703582")
        st.write(" ")
    st.html(
        f"<h1 style='text-align: center; padding: 20px; line-height: 1.5; max-width: 1200px; margin: 40px auto;'>"
        f"{translations['header_message']}"
        "</h1>",
    )
    
          

def render_features(translations):
    st.html(
        f"""
        <div style='
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            margin: 40px 0;
        '>
            <!-- Feature 1 -->
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
                <h2>{translations['feature1_title']}</h2>
                <p>{translations['feature1_desc']}</p>
            </div>

            <!-- Feature 2 -->
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
                <h2>{translations['feature2_title']}</h2>
                <p>{translations['feature2_desc']}</p>
            </div>
            
            <!-- Feature 3 -->
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
                <h2>{translations['feature3_title']}</h2>
                <p>{translations['feature3_desc']}</p>
            </div>
            
            <!-- Feature 4 -->
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
              <h2>{translations['feature4_title']}</h2>
              <p>{translations['feature4_desc']}</p>
            </div>
            <!-- Feature 5 -->
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
              <h2>{translations['feature5_title']}</h2>
              <p>{translations['feature5_desc']}</p>
            </div>
        </div>
        """
    )