import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json

st.set_page_config(
    page_title="Fake News Detection",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1rem;
        padding: 0.5rem 1rem;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    
    .prediction-card-true {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    .prediction-card-fake {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

API_BASE_URL = "http://localhost:8000"

def get_api_health():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def predict_single(text):
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json={"text": text},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.json()}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server. Please make sure the backend is running.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def predict_batch(articles):
    try:
        payload = [{"text": article} for article in articles]
        response = requests.post(
            f"{API_BASE_URL}/batch-predict",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.json()}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server. Please make sure the backend is running.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def get_model_info():
    try:
        response = requests.get(f"{API_BASE_URL}/model-info", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def train_model():
    try:
        response = requests.post(
            f"{API_BASE_URL}/train",
            timeout=300
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": response.json()}
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Training timeout - model may still be training"}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": "Cannot connect to API server"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Sidebar
with st.sidebar:
    st.title("📰 Fake News Detector")
    st.markdown("---")
    
    # API Status
    api_health = get_api_health()
    if api_health:
        st.success("✅ API Status: Online")
    else:
        st.error("❌ API Status: Offline")
        st.warning("Please start the backend server with: `python -m uvicorn backend.main:app --reload`")
    
    st.markdown("---")
    st.markdown("### Navigation")
    page = st.radio(
        "Select a page:",
        ["🏠 Home", "🔍 Single Prediction", "📊 Batch Prediction", "📈 Model Info", "⚙️ Train Model"]
    )

# Main content
if page == "🏠 Home":
    st.title("🏠 Welcome to Fake News Detection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### About This Project
        
        This is a machine learning-based system designed to detect whether news articles 
        are **fake** or **true** using advanced Natural Language Processing techniques.
        
        **Key Features:**
        - 🎯 High accuracy predictions (>99%)
        - 📝 Single and batch article analysis
        - 📊 Real-time model metrics
        - 🔄 Model retraining capability
        - ⚡ Fast API-based backend
        
        **How it Works:**
        1. Text preprocessing (cleaning and normalization)
        2. TF-IDF vectorization for feature extraction
        3. Logistic Regression classification
        4. Confidence score calculation
        """)
    
    with col2:
        # Display model status
        model_info = get_model_info()
        
        st.markdown("### 📊 Current Model Status")
        
        if model_info and model_info.get("trained"):
            st.success("✅ Model Trained")
            
            metrics_data = {
                "Accuracy": f"{model_info['accuracy']:.4f}",
                "Precision": f"{model_info['precision']:.4f}",
                "Recall": f"{model_info['recall']:.4f}",
                "F1-Score": f"{model_info['f1_score']:.4f}",
                "Train Size": f"{model_info['train_size']:,}",
                "Test Size": f"{model_info['test_size']:,}"
            }
            
            for key, value in metrics_data.items():
                st.metric(key, value)
            
            if model_info.get("created_at"):
                st.caption(f"Trained: {model_info['created_at']}")
        else:
            st.warning("⚠️ Model Not Trained")
            st.info("Please train the model first using the 'Train Model' page.")
    
    st.markdown("---")
    st.markdown("### 🚀 Quick Start")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Try Single Prediction", use_container_width=True):
            st.switch_page("pages/01_single_prediction.py")
    
    with col2:
        if st.button("📊 Batch Analysis", use_container_width=True):
            st.switch_page("pages/02_batch_prediction.py")
    
    with col3:
        if st.button("⚙️ Train Model", use_container_width=True):
            st.switch_page("pages/04_train_model.py")

elif page == "🔍 Single Prediction":
    st.title("🔍 Single Article Prediction")
    
    st.markdown("""
    Enter or paste a news article text below to check if it's fake or true.
    The model will analyze the content and provide a prediction with confidence score.
    """)
    
    col1, col2 = st.columns([3, 1], gap="large")
    
    with col1:
        article_text = st.text_area(
            "Enter news article text:",
            placeholder="Paste your news article here...",
            height=250,
            key="article_input"
        )
    
    with col2:
        st.markdown("### Controls")
        analyze_button = st.button("🔍 Analyze", use_container_width=True, type="primary")
        clear_button = st.button("🗑️ Clear", use_container_width=True)
        
        if clear_button:
            st.rerun()
    
    if analyze_button and article_text:
        with st.spinner("Analyzing article..."):
            result = predict_single(article_text)
        
        if result:
            st.markdown("---")
            st.markdown("### 📊 Prediction Result")
            
            prediction = result['prediction']
            confidence = result['confidence']
            prob_fake = result['probability_fake']
            prob_true = result['probability_true']
            
            # Color-coded display
            if prediction == "TRUE":
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Prediction", "✅ TRUE", f"{confidence:.2f}%", 
                            delta_color="off", border=True)
                with col2:
                    st.metric("Confidence", f"{confidence:.2f}%", border=True)
                with col3:
                    st.metric("Model Certainty", f"HIGH" if confidence > 90 else "MEDIUM")
                
                st.success(f"This article is likely **TRUE** with {confidence:.2f}% confidence")
            else:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Prediction", "❌ FAKE", f"{confidence:.2f}%", 
                            delta_color="off", border=True)
                with col2:
                    st.metric("Confidence", f"{confidence:.2f}%", border=True)
                with col3:
                    st.metric("Model Certainty", f"HIGH" if confidence > 90 else "MEDIUM")
                
                st.error(f"This article is likely **FAKE** with {confidence:.2f}% confidence")
            
            st.markdown("---")
            
            # Probability visualization
            col1, col2 = st.columns(2)
            
            with col1:
                # Gauge chart
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=confidence,
                    title={'text': "Confidence Score"},
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 100], 'color': "gray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Probability comparison
                fig = go.Figure(data=[
                    go.Bar(
                        x=['FAKE', 'TRUE'],
                        y=[prob_fake, prob_true],
                        marker=dict(color=['#dc3545', '#28a745']),
                        text=[f'{prob_fake:.2%}', f'{prob_true:.2%}'],
                        textposition='auto'
                    )
                ])
                fig.update_layout(
                    title="Prediction Probabilities",
                    yaxis_title="Probability",
                    height=300,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Article summary
            st.markdown("---")
            st.markdown("### 📄 Article Summary")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Character Count:** {len(article_text):,}")
            with col2:
                st.info(f"**Word Count:** {len(article_text.split()):,}")
            
            st.markdown(f"**Preview:** {article_text[:300]}...")
    
    elif analyze_button and not article_text:
        st.warning("Please enter some text to analyze.")

elif page == "📊 Batch Prediction":
    st.title("📊 Batch Article Prediction")
    
    st.markdown("""
    Analyze multiple news articles at once. You can:
    - Paste articles separated by a delimiter
    - Upload a CSV file with articles
    - Paste sample articles
    """)
    
    input_method = st.radio("Choose input method:", ["📝 Text Input", "📁 CSV Upload"])
    
    if input_method == "📝 Text Input":
        st.markdown("### Enter Articles")
        st.info("Separate multiple articles with the delimiter: `---ARTICLE---`")
        
        batch_text = st.text_area(
            "Paste articles here:",
            placeholder="Article 1\n---ARTICLE---\nArticle 2\n---ARTICLE---\nArticle 3",
            height=250
        )
        
        if st.button("🔍 Analyze Batch", type="primary", use_container_width=True):
            articles = [a.strip() for a in batch_text.split("---ARTICLE---") if a.strip()]
            
            if articles:
                with st.spinner(f"Analyzing {len(articles)} articles..."):
                    results = predict_batch(articles)
                
                if results:
                    st.markdown("---")
                    st.markdown(f"### 📊 Results ({len(articles)} articles)")
                    
                    # Summary statistics
                    predictions = [p['prediction'] for p in results['predictions']]
                    true_count = predictions.count('TRUE')
                    fake_count = predictions.count('FAKE')
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Articles", len(articles))
                    with col2:
                        st.metric("True Articles", true_count)
                    with col3:
                        st.metric("Fake Articles", fake_count)
                    with col4:
                        percentage = (true_count / len(articles) * 100) if articles else 0
                        st.metric("True %", f"{percentage:.1f}%")
                    
                    # Summary chart
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=['TRUE', 'FAKE'],
                            values=[true_count, fake_count],
                            marker=dict(colors=['#28a745', '#dc3545']),
                            hole=0.3
                        )
                    ])
                    fig.update_layout(title="Prediction Distribution")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("---")
                    st.markdown("### 📋 Detailed Predictions")
                    
                    # Create dataframe for display
                    df_results = pd.DataFrame([
                        {
                            "Article": p['text'][:50] + "..." if len(p['text']) > 50 else p['text'],
                            "Prediction": p['prediction'],
                            "Confidence": f"{p['confidence']:.2f}%",
                            "Fake Prob": f"{p['probability_fake']:.4f}",
                            "True Prob": f"{p['probability_true']:.4f}"
                        }
                        for p in results['predictions']
                    ])
                    
                    st.dataframe(df_results, use_container_width=True)
                    
                    # Download results
                    csv = df_results.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv,
                        file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                st.warning("Please enter at least one article.")
    
    else:  # CSV Upload
        st.markdown("### Upload CSV File")
        st.info("CSV should have a 'text' column containing the articles")
        
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                if 'text' not in df.columns:
                    st.error("CSV must contain a 'text' column")
                else:
                    st.success(f"✅ Loaded {len(df)} articles")
                    
                    if st.button("🔍 Analyze CSV", type="primary", use_container_width=True):
                        articles = df['text'].tolist()
                        
                        with st.spinner(f"Analyzing {len(articles)} articles..."):
                            results = predict_batch(articles)
                        
                        if results:
                            st.markdown("---")
                            
                            # Add predictions to dataframe
                            df['Prediction'] = [p['prediction'] for p in results['predictions']]
                            df['Confidence'] = [f"{p['confidence']:.2f}%" for p in results['predictions']]
                            
                            st.dataframe(df, use_container_width=True)
                            
                            # Download results
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results",
                                data=csv,
                                file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")

elif page == "📈 Model Info":
    st.title("📈 Model Information & Metrics")
    
    model_info = get_model_info()
    
    if model_info and model_info.get("trained"):
        st.success("✅ Model Status: Trained")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Accuracy",
                f"{model_info['accuracy']:.4f}",
                f"{model_info['accuracy']*100:.2f}%"
            )
        
        with col2:
            st.metric(
                "Precision",
                f"{model_info['precision']:.4f}",
                f"{model_info['precision']*100:.2f}%"
            )
        
        with col3:
            st.metric(
                "Recall",
                f"{model_info['recall']:.4f}",
                f"{model_info['recall']*100:.2f}%"
            )
        
        with col4:
            st.metric(
                "F1-Score",
                f"{model_info['f1_score']:.4f}",
                f"{model_info['f1_score']*100:.2f}%"
            )
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Dataset Statistics")
            
            fig = go.Figure(data=[
                go.Bar(
                    x=['Training', 'Testing'],
                    y=[model_info['train_size'], model_info['test_size']],
                    marker=dict(color=['#0d6efd', '#6f42c1']),
                    text=[f"{model_info['train_size']:,}", f"{model_info['test_size']:,}"],
                    textposition='auto'
                )
            ])
            fig.update_layout(
                title="Data Split",
                yaxis_title="Number of Articles",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Model Performance")
            
            metrics = {
                'Accuracy': model_info['accuracy'],
                'Precision': model_info['precision'],
                'Recall': model_info['recall'],
                'F1-Score': model_info['f1_score']
            }
            
            fig = go.Figure(data=[
                go.Scatterpolar(
                    r=[v*100 for v in metrics.values()],
                    theta=list(metrics.keys()),
                    fill='toself',
                    name='Model Performance'
                )
            ])
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                title="Performance Radar",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### Training Details")
        
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.info(f"**Training Set Size:** {model_info['train_size']:,} articles")
        
        with info_col2:
            st.info(f"**Test Set Size:** {model_info['test_size']:,} articles")
        
        if model_info.get("created_at"):
            st.caption(f"Model trained on: {model_info['created_at']}")
    
    else:
        st.warning("⚠️ No trained model found")
        st.info("Please train the model first using the 'Train Model' page.")

elif page == "⚙️ Train Model":
    st.title("⚙️ Train News Detection Model")
    
    st.markdown("""
    Train or retrain the machine learning model using your dataset.
    Make sure you have the Fake.csv and True.csv files in the data folder.
    """)
    
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        st.markdown("### Training Configuration")
        
        st.info("""
        **Default Settings:**
        - TF-IDF Vectorizer with max 5000 features
        - Stop words removal (English)
        - Logistic Regression classifier
        - 80-20 train-test split
        - Random state: 42 (for reproducibility)
        """)
        
        st.markdown("The model will be trained on:")
        st.write("- `data/Fake.csv` - Fake news articles")
        st.write("- `data/True.csv` - True news articles")
    
    with col2:
        st.markdown("### Action")
        
        if st.button("🚀 Start Training", type="primary", use_container_width=True, key="train_btn"):
            with st.spinner("Training model... This may take a few minutes..."):
                result = train_model()
            
            if result['status'] == 'success':
                st.success("✅ Model trained successfully!")
                
                st.markdown("### 📊 Training Results")
                
                metrics = result['metrics']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Accuracy", f"{metrics['accuracy']:.4f}")
                
                with col2:
                    st.metric("Precision", f"{metrics['precision']:.4f}")
                
                with col3:
                    st.metric("Recall", f"{metrics['recall']:.4f}")
                
                with col4:
                    st.metric("F1-Score", f"{metrics['f1_score']:.4f}")
                
                st.success(f"Model trained at: {result['timestamp']}")
                
                st.balloons()
            else:
                st.error(f"❌ Training failed: {result['message']}")
        
        st.markdown("---")
        
        current_model = get_model_info()
        if current_model and current_model.get("trained"):
            st.markdown("### Current Model")
            st.success("✅ Model exists")
            if current_model.get("created_at"):
                st.caption(f"Trained: {current_model['created_at']}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p style='color: #999;'>
        🤖 Fake News Detection System | Built with Streamlit & FastAPI
    </p>
</div>
""", unsafe_allow_html=True)
