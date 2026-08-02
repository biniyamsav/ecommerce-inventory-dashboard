import streamlit as st


def data_table(df, height=400):
    st.dataframe(df, height=height, use_container_width=True)


def attention_table(df, title="Attention", message=None, height=320):
    st.markdown(
        f"""
        <div style='border-left: 4px solid #D97706; background: rgba(217, 119, 6, 0.08); padding: 14px 18px; border-radius: 10px; margin-bottom: 12px;'>
            <strong style='color: #B45309;'>{title}</strong><br>
            <span style='color: #92400E; font-size: 0.95rem;'>{message or 'Review these records for follow-up action.'}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("No records match this filter.")
        return

    st.dataframe(df, height=height, use_container_width=True)
