import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import kaleido
import os
from datetime import datetime
from io import BytesIO

# Configuration
st.set_page_config(
    page_title="Interactive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Internationalization
def set_language():
    lang = st.sidebar.radio("اللغة / Language", ["العربية", "English"])
    return lang

lang = set_language()

# Translation dictionary
translations = {
    "title": {
        "العربية": "لوحة تحليل البيانات التفاعلية",
        "English": "Interactive Data Analysis Dashboard"
    },
    "upload_file": {
        "العربية": "رفع ملف البيانات (CSV, Excel, JSON)",
        "English": "Upload Data File (CSV, Excel, JSON)"
    },
    "data_preview": {
        "العربية": "معاينة البيانات",
        "English": "Data Preview"
    },
    "data_summary": {
        "العربية": "ملخص البيانات",
        "English": "Data Summary"
    },
    "filter_data": {
        "العربية": "تصفية البيانات",
        "English": "Filter Data"
    },
    "select_column": {
        "العربية": "اختر العمود للتصفية",
        "English": "Select column to filter by"
    },
    "select_value": {
        "العربية": "اختر القيمة",
        "English": "Select value"
    },
    "visualization": {
        "العربية": "تصور البيانات",
        "English": "Data Visualization"
    },
    "chart_type": {
        "العربية": "نوع الرسم البياني",
        "English": "Chart Type"
    },
    "x_axis": {
        "العربية": "محور السينات (X)",
        "English": "X-Axis Column"
    },
    "y_axis": {
        "العربية": "محور الصادات (Y)",
        "English": "Y-Axis Column"
    },
    "color_column": {
        "العربية": "عمود التلوين",
        "English": "Color Column"
    },
    "generate_plot": {
        "العربية": "إنشاء الرسم البياني",
        "English": "Generate Plot"
    },
    "save_data": {
        "العربية": "حفظ البيانات المصفاة",
        "English": "Save Filtered Data"
    },
    "save_plot": {
        "العربية": "حفظ الرسم البياني",
        "English": "Save Plot"
    },
    "waiting_file": {
        "العربية": "في انتظار رفع الملف...",
        "English": "Waiting for file upload..."
    },
    "kaleido_error": {
        "العربية": "يجب تثبيت مكتبة kaleido لحفظ الرسومات. قم بتشغيل: pip install kaleido",
        "English": "kaleido library required to save plots. Run: pip install kaleido"
    },
    "tabs": {
        "data": {
            "العربية": "البيانات",
            "English": "Data"
        },
        "visualization": {
            "العربية": "التصور",
            "English": "Visualization"
        }
    }
}

# Main App
def main():
    st.title(translations["title"][lang])
    
    # Initialize session state for demo data if not exists
    if 'df' not in st.session_state:
        st.session_state.df = None
    
    # File uploader with multiple format support
    uploaded_file = st.sidebar.file_uploader(
        translations["upload_file"][lang],
        type=["csv", "xlsx", "xls", "json"]
    )
    
    # Sample data option
    if uploaded_file is None:
        st.info(translations["waiting_file"][lang])
        if st.checkbox("Use sample data for demo"):
            df = pd.DataFrame({
                'Date': pd.date_range(start='2023-01-01', periods=100),
                'Product': np.random.choice(['A', 'B', 'C', 'D'], 100),
                'Sales': np.random.randint(100, 1000, 100),
                'Region': np.random.choice(['North', 'South', 'East', 'West'], 100),
                'Profit': np.random.uniform(10, 500, 100)
            })
            st.session_state.df = df
        elif st.session_state.df is not None:
            df = st.session_state.df
        else:
            return
    else:
        # Read file based on extension
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        try:
            if file_ext == '.csv':
                df = pd.read_csv(uploaded_file)
            elif file_ext in ('.xlsx', '.xls'):
                df = pd.read_excel(uploaded_file)
            elif file_ext == '.json':
                df = pd.read_json(uploaded_file)
            else:
                st.error("Unsupported file format")
                return
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return
        
        # Store dataframe in session state
        st.session_state.df = df
    
    # Create tabs
    tab1, tab2 = st.tabs([
        translations["tabs"]["data"][lang],
        translations["tabs"]["visualization"][lang]
    ])
    
    with tab1:
        # Data Preview Section
        st.subheader(translations["data_preview"][lang])
        with st.expander("View Full Data"):
            st.dataframe(st.session_state.df)
            
        # Data Summary Section
        st.subheader(translations["data_summary"][lang])
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Numerical Columns Summary**")
            st.write(st.session_state.df.describe())
            
        with col2:
            st.write("**Categorical Columns Summary**")
            cat_cols = st.session_state.df.select_dtypes(include=['object']).columns
            for col in cat_cols:
                st.write(f"**{col}**")
                st.write(st.session_state.df[col].value_counts().head())
                
        # Filter Data Section
        st.subheader(translations["filter_data"][lang])
        columns = st.session_state.df.columns.tolist()
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_column = st.selectbox(
                translations["select_column"][lang],
                columns
            )
            
        with col2:
            if pd.api.types.is_numeric_dtype(st.session_state.df[selected_column]):
                min_val = float(st.session_state.df[selected_column].min())
                max_val = float(st.session_state.df[selected_column].max())
                selected_value = st.slider(
                    translations["select_value"][lang],
                    min_val, max_val, (min_val, max_val))
                filtered_df = st.session_state.df[
                    (st.session_state.df[selected_column] >= selected_value[0]) & 
                    (st.session_state.df[selected_column] <= selected_value[1])
                ]
            else:
                unique_values = st.session_state.df[selected_column].unique()
                selected_value = st.selectbox(
                    translations["select_value"][lang],
                    unique_values
                )
                filtered_df = st.session_state.df[st.session_state.df[selected_column] == selected_value]
                
        st.write(f"**Filtered Data ({len(filtered_df)} rows)**")
        st.dataframe(filtered_df)
        
        # Save filtered data
        if st.button(translations["save_data"][lang]):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"filtered_data_{timestamp}.csv",
                mime="text/csv"
            )
    
    with tab2:
        # Data Visualization Section
        st.subheader(translations["visualization"][lang])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            chart_type = st.selectbox(
                translations["chart_type"][lang],
                ["Line", "Bar", "Scatter", "Histogram", "Box", "Pie"]
            )
            
        with col2:
            x_column = st.selectbox(
                translations["x_axis"][lang],
                st.session_state.df.columns,
                index=min(0, len(st.session_state.df.columns)-1)
            )
            
        with col3:
            y_options = [col for col in st.session_state.df.columns if col != x_column] if x_column in st.session_state.df.columns else st.session_state.df.columns
            y_column = st.selectbox(
                translations["y_axis"][lang],
                y_options,
                index=min(1, len(y_options)-1)
            )
            
        color_column = st.selectbox(
            translations["color_column"][lang],
            ["None"] + [col for col in st.session_state.df.columns if pd.api.types.is_numeric_dtype(st.session_state.df[col])]
        )
        
        if st.button(translations["generate_plot"][lang]):
            try:
                fig = None
                if chart_type == "Line":
                    if color_column != "None":
                        fig = px.line(filtered_df, x=x_column, y=y_column, color=color_column)
                    else:
                        fig = px.line(filtered_df, x=x_column, y=y_column)
                elif chart_type == "Bar":
                    if color_column != "None":
                        fig = px.bar(filtered_df, x=x_column, y=y_column, color=color_column)
                    else:
                        fig = px.bar(filtered_df, x=x_column, y=y_column)
                elif chart_type == "Scatter":
                    if color_column != "None":
                        fig = px.scatter(filtered_df, x=x_column, y=y_column, color=color_column)
                    else:
                        fig = px.scatter(filtered_df, x=x_column, y=y_column)
                elif chart_type == "Histogram":
                    fig = px.histogram(filtered_df, x=x_column)
                elif chart_type == "Box":
                    fig = px.box(filtered_df, x=x_column, y=y_column)
                elif chart_type == "Pie":
                    fig = px.pie(filtered_df, names=x_column, values=y_column)
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Save plot button with kaleido check
                    try:
                        buf = BytesIO()
                        fig.write_image(buf, format="png")
                        st.download_button(
                            label=translations["save_plot"][lang],
                            data=buf,
                            file_name=f"plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                            mime="image/png"
                        )
                    except Exception as e:
                        st.error(translations["kaleido_error"][lang])
                    
            except Exception as e:
                st.error(f"Error generating plot: {str(e)}")

if __name__ == "__main__":
    main()