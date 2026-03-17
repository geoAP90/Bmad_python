"""
Streamlit UI for Strata Analysis
"""
import os
import streamlit as st

from components import call_backend_api

# Get API_HOST from environment variable
API_HOST = os.getenv("API_HOST", "http://api:8000")#"http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="Article Analyzer",
    page_icon="🔬",
    layout="wide"
)


def main():
    """Main Streamlit application."""
    st.title("🔬 Article Analyzer")
    st.markdown("Enter text below and click **Summarise Text** to process your data.")
    
    # Large text area for input
    text_input = st.text_area(
        "Input Text",
        height=300,
        placeholder="Enter the text you want to analyze...",
        key="input_text_area"
    )
    
    # Analyze button
    if st.button("Analyze"):
        if not text_input.strip():
            st.warning("Please enter some text to analyze.")
        else:
            with st.spinner("Analyze text..."):
                result = call_backend_api(text_input)
                
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success("Analysis complete!")
                    st.json(result)
    
    # Display API connection info (debug mode)
    with st.expander("Debug Info"):
        st.write(f"API Host: {API_HOST}")


if __name__ == "__main__":
    main()
