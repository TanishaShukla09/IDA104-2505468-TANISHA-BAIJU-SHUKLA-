# IDA104-2505468-TANISHA-BAIJU-SHUKLA-

# Rocket Launch Analytics Dashboard

A Streamlit-based interactive analytics dashboard designed to explore rocket launch simulations, mission data, and scientific trends through numerical modeling and visualization.

This project combines physics-based simulation, numerical integration, and data analytics within an interactive web interface built for learning, experimentation, and analysis.

---

## Features

### Interactive Simulation

- Rocket motion modeled using numerical integration
- Comparison between drag and no-drag conditions
- Step-by-step visualization of altitude, velocity, mass, and acceleration
- Mission parameter customization

### Scientific Visualization

- Multi-graph analysis of motion and forces
- Velocity and altitude trend curves
- Mass variation and thrust behavior
- Integration accuracy comparison

### Physics Concepts Integration

- Rocket propulsion principles
- Atmospheric drag proportional to velocity squared
- Mass loss effects on acceleration
- Burnout dynamics and thrust-to-weight behavior

### Data Handling and Export

- Simulation data export to CSV
- Parameter export to JSON
- Structured scientific workflow support

### Mission Insights and Analytics

- Payload and fuel relationship analysis
- Cost versus mission success exploration
- Altitude loss due to drag
- Crew size optimization observations

### Session Tracking

- Storage of recent simulation runs
- Comparative analysis across missions
- Exportable simulation history

---

## Tech Stack

- Python 3.9+
- Streamlit
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Plotly
- SciPy

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/your-username/rocket-launch-analytics-dashboard.git
cd rocket-launch-analytics-dashboard
```

### Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

### Activate Environment

**Windows**

```bash
venv\Scripts\activate
```

**macOS / Linux**

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install streamlit pandas numpy matplotlib seaborn plotly scipy
```

---

## Running the Application

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal, typically:

```
http://localhost:8501
```

---

## Project Structure

```
.
├── app.py
├── README.md
└── requirements.txt
```

---

## Key Improvements Implemented

- Fixed Streamlit component label handling
- Resolved timestamp conversion compatibility issues
- Updated deprecated layout parameters
- Added structured validation and loading indicators
- Implemented export functionality and session tracking

---

## Usage Guide

1. Launch the Streamlit application.
2. Configure rocket mission parameters.
3. Run the numerical simulation.
4. Explore generated graphs and analytics.
5. Export results for further analysis.

---

## Future Enhancements

- Deployment via cloud hosting platforms
- Integration with real-world launch datasets
- Predictive modeling using machine learning
- Persistent user sessions and dashboards

## Streamlit Link 

