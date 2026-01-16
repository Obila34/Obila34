# Hi there, I'm Sam Obila Allela 👋

<div align="center">
  <svg viewBox="0 0 1280 360" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Gradient backgrounds -->
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0a0e27;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#1a1f3a;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0f1420;stop-opacity:1" />
    </linearGradient>
    
    <linearGradient id="accentGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#00d4ff;stop-opacity:0.8" />
      <stop offset="50%" style="stop-color:#7b2ff7;stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:#f72585;stop-opacity:0.8" />
    </linearGradient>

    <!-- Glow effects -->
    <filter id="glow">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="softGlow">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <!-- Background -->
  <rect width="1280" height="360" fill="url(#bgGradient)"/>
  
  <!-- Animated neural network visualization -->
  <g opacity="0.3">
    <!-- Neural network nodes -->
    <circle cx="100" cy="80" r="3" fill="#00d4ff">
      <animate attributeName="opacity" values="0.3;1;0.3" dur="3s" repeatCount="indefinite"/>
    </circle>
    <circle cx="180" cy="120" r="3" fill="#7b2ff7">
      <animate attributeName="opacity" values="0.5;1;0.5" dur="2.5s" repeatCount="indefinite"/>
    </circle>
    <circle cx="140" cy="180" r="3" fill="#f72585">
      <animate attributeName="opacity" values="0.4;1;0.4" dur="2.8s" repeatCount="indefinite"/>
    </circle>
    <circle cx="220" cy="200" r="3" fill="#00d4ff">
      <animate attributeName="opacity" values="0.6;1;0.6" dur="3.2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="80" cy="240" r="3" fill="#7b2ff7">
      <animate attributeName="opacity" values="0.3;1;0.3" dur="2.7s" repeatCount="indefinite"/>
    </circle>
    <circle cx="280" cy="140" r="3" fill="#f72585">
      <animate attributeName="opacity" values="0.5;1;0.5" dur="3.1s" repeatCount="indefinite"/>
    </circle>

    <!-- Connecting lines -->
    <line x1="100" y1="80" x2="180" y2="120" stroke="url(#accentGradient)" stroke-width="1" opacity="0.4"/>
    <line x1="180" y1="120" x2="140" y2="180" stroke="url(#accentGradient)" stroke-width="1" opacity="0.4"/>
    <line x1="140" y1="180" x2="220" y2="200" stroke="url(#accentGradient)" stroke-width="1" opacity="0.4"/>
    <line x1="100" y1="80" x2="280" y2="140" stroke="url(#accentGradient)" stroke-width="1" opacity="0.3"/>
    <line x1="80" y1="240" x2="140" y2="180" stroke="url(#accentGradient)" stroke-width="1" opacity="0.4"/>
  </g>

  <!-- Floating particles -->
  <g opacity="0.6">
    <circle cx="400" cy="100" r="2" fill="#00d4ff">
      <animate attributeName="cy" values="100;90;100" dur="4s" repeatCount="indefinite"/>
    </circle>
    <circle cx="550" cy="280" r="1.5" fill="#7b2ff7">
      <animate attributeName="cy" values="280;270;280" dur="3.5s" repeatCount="indefinite"/>
    </circle>
    <circle cx="850" cy="150" r="2" fill="#f72585">
      <animate attributeName="cy" values="150;140;150" dur="4.5s" repeatCount="indefinite"/>
    </circle>
  </g>

  <!-- Accent line -->
  <rect x="0" y="280" width="1280" height="2" fill="url(#accentGradient)" opacity="0.6" filter="url(#softGlow)"/>

  <!-- Vibrant subtitle -->
  <text x="1240" y="75" font-family="'Inter', 'Segoe UI', sans-serif" font-size="24" font-weight="600" fill="url(#accentGradient)" text-anchor="end" letter-spacing="3" filter="url(#softGlow)">
    DATA SCIENCE | MACHINE LEARNING
  </text>

  <!-- Main title - more modern, smaller font -->
  <text x="1240" y="120" font-family="'Inter', 'Segoe UI', 'Roboto', sans-serif" font-size="46" font-weight="700" fill="#ffffff" text-anchor="end" letter-spacing="1">
    DATA SCIENTIST &
  </text>
  <text x="1240" y="175" font-family="'Inter', 'Segoe UI', 'Roboto', sans-serif" font-size="46" font-weight="700" fill="#ffffff" text-anchor="end" letter-spacing="1">
    MACHINE LEARNING
  </text>
  <text x="1240" y="230" font-family="'Inter', 'Segoe UI', 'Roboto', sans-serif" font-size="46" font-weight="700" fill="url(#accentGradient)" text-anchor="end" letter-spacing="1" filter="url(#softGlow)">
    ENGINEER
  </text>

  <!-- Contact section with modern styling -->
  <g>
    <!-- Contact label -->
    <text x="640" y="315" font-family="'Inter', 'Segoe UI', sans-serif" font-size="14" font-weight="600" fill="#00d4ff" text-anchor="middle" letter-spacing="2" opacity="0.9">
      CONTACT
    </text>
    
    <!-- Email -->
    <text x="640" y="340" font-family="'Inter', 'Segoe UI', sans-serif" font-size="16" font-weight="400" fill="#ffffff" text-anchor="middle" opacity="0.9">
      Obilasam3@gmail.com  |  +254795849256
    </text>
  </g>

  <!-- Decorative elements -->
  <circle cx="50" cy="320" r="3" fill="#00d4ff" opacity="0.5">
    <animate attributeName="r" values="3;5;3" dur="2s" repeatCount="indefinite"/>
  </circle>
  <circle cx="1230" cy="320" r="3" fill="#f72585" opacity="0.5">
    <animate attributeName="r" values="3;5;3" dur="2s" repeatCount="indefinite"/>
  </circle>
</svg>
</div>

## 🚀 About Me

I'm a **Data Scientist** passionate about turning data into actionable insights and building machine learning solutions that make a real-world impact. With expertise in statistical modeling, deep learning, and data visualization, I love solving complex problems through data-driven approaches.  

- 🔭 I'm currently working on **Building A ChatBot For Customer Support**  
- 🌱 I'm learning **Keras and OpenCV**  
- 👯 I'm looking to collaborate on **Machine Learning & AI Projects**  
- 💬 Ask me about **Data Science, Machine Learning, Python, and Analytics**  
- 📫 How to reach me: **Obilasam3@gmail.com**  
- ⚡ Fun fact: **💻 Building logic, framing shots.**

## 🛠️ Tech Stack

### Languages  
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)


### Data Science & ML  
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)  ![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)  ![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white) 
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)  ![Keras](https://img.shields.io/badge/Keras-D00000?style=for-the-badge&logo=keras&logoColor=white)

### Data Visualization  
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557c?style=for-the-badge&logo=python&logoColor=white)  
![Seaborn](https://img.shields.io/badge/Seaborn-3776AB?style=for-the-badge&logo=python&logoColor=white)  
![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)

### Tools & Platforms  
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)     ![Azure](https://img.shields.io/badge/Azure-0078D4?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)       ![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)  



## 🏆 Featured Projects

### [Housing Price Explore](https://github.com/Obila34/HousingPrice_Explore-)
**Data Exploration & Predictive Modeling**  
- Analyzed a housing dataset to uncover key factors affecting house prices.  
- Built a predictive regression model using Python and scikit-learn to predict house prices with high accuracy.  
- Leveraged data visualization libraries like Plotly and Seaborn to present impactful insights for understanding price determinants.

### [Sign Language Detector](https://github.com/Obila34/SignLanguageDetector)
**Deep Learning Model for Real-Time Sign Language Recognition**  
- Designed and trained a Convolutional Neural Network (CNN) using TensorFlow and Keras for detecting hand gestures.  
- Integrated OpenCV to process video input for real-time gesture recognition.  
- Achieved outstanding performance on sign language datasets with an accuracy of 92%.

### [Sales Forecasting with Facebook Prophet](https://github.com/Obila34/Sales-Forasting-with-FaceBook-Prophet)
**Time Series Forecasting for Retail Sales Trends**  
- Developed a sales forecasting model using Facebook Prophet to predict future sales trends based on historical data.  
- Optimized hyperparameters for enhanced prediction accuracy and incorporated seasonality effects.  
- Visualized future sales using interactive dashboards with Plotly Dash, enabling actionable insights for decision-makers.

## 📝 Latest Blog Posts
<!-- BLOG-POST-LIST:START -->  
- [Article Title 1](https://yourblog.com/article1)  
- [Article Title 2](https://yourblog.com/article2)  
- [Article Title 3](https://yourblog.com/article3)  
<!-- BLOG-POST-LIST:END -->

## 🤝 Connect with Me

<div align="center">

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/sam-allela?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3Bd1RWDzziRvuYFe22B1FqPQ%3D%3D)
[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/yourhandle)
[![Medium](https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white)](https://medium.com/@yourprofile)

</div>

---

<div align="center">
  
💡 *"Data is the new oil, but insights are the refined fuel that powers innovation"*

⭐️ From [Obila34](https://github.com/Obila34)

</div>
