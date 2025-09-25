# Architectural Design System

A comprehensive AI-powered architectural design system that generates detailed residential plans, 3D visualizations, and professional reports in minutes.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v2.3+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🏗️ Overview

Transform your dream home into reality with our intelligent design system. Generate professional floor plans, 3D visualizations, and comprehensive reports that comply with building codes and Vastu principles.

### ✨ Key Features

- **🧠 AI-Powered Design Engine**: Automated FAR calculations, optimal room allocation, and compliance checking
- **📐 Professional 2D Floor Plans**: CAD-style blueprints with accurate dimensions and annotations
- **📊 Advanced Analytics**: Space utilization analysis, efficiency scoring, and optimization recommendations
- **🌐 Modern Web Interface**: Intuitive design input with real-time validation
- **📱 Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **🏛️ Cultural Compliance**: Automatic Vastu/Feng Shui principles integration
- **💰 Cost Estimation**: Detailed construction cost and timeline predictions

## 🚀 Quick Start

### Option 1: One-Click Startup (Recommended)
```bash
python run.py
```

### Option 2: Demo Mode (No Web Interface)
```bash
python demo.py
```

### Option 3: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start the web application
python app.py
```

## 📋 Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 1GB free space

## 📦 Installation

### 1. Clone or Download
```bash
# If using git
git clone <repository-url>
cd ArchitecturalDesignSystem

# Or download and extract the ZIP file
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python run.py
```

### 4. Access the Web Interface
Open your browser and navigate to: `http://localhost:5000`

## 🎯 Usage Examples

### Web Interface
1. Open `http://localhost:5000` in your browser
2. Click "Start Designing" 
3. Enter your plot details (size, orientation, etc.)
4. Select building type and bedroom configuration
5. Add any special requirements
6. Click "Generate Design"
7. View results and download complete package

### API Usage
```python
from architectural_engine import ArchitecturalDesigner

# Initialize the designer
designer = ArchitecturalDesigner()

# Define input parameters
design_input = {
    "land_size": 1200.0,
    "facing": "East",
    "building_type": "Independent House", 
    "bedroom_config": "3BHK",
    "staircase_type": "Straight",
    "floors": 2,
    "budget_range": "Medium"
}

# Generate design
design = designer.generate_design(design_input)

# Generate floor plan
floor_plan = designer.generate_floor_plan(design)

# Export results
designer.export_design_json(design, "my_design.json")
```

### Programmatic Visualization
```python
from visualization.cad_renderer import CADRenderer
from analytics.chart_generator import ChartGenerator

# Generate 2D floor plan
renderer = CADRenderer()
floor_plan_image = renderer.render_floor_plan(floor_plan, output_path="floor_plan.png")

# Generate analytics charts
chart_gen = ChartGenerator()
space_chart = chart_gen.generate_space_allocation_pie_chart(design)
efficiency_chart = chart_gen.generate_efficiency_dashboard(design)
```

## 📁 Project Structure

```
ArchitecturalDesignSystem/
├── 🚀 run.py                    # Main startup script
├── 🎮 demo.py                   # Demo without web interface
├── 🌐 app.py                    # Flask web application
├── 📋 requirements.txt          # Python dependencies
├── 🏗️ architectural_engine/     # Core design algorithms
│   ├── designer.py              # Main design orchestrator
│   ├── calculator.py            # FAR, setbacks, room calculations
│   ├── validator.py             # Design validation logic
│   ├── schemas.py               # Data structures and validation
│   └── layout_generator.py      # 2D layout generation
├── 🎨 visualization/            # Rendering and visualization
│   ├── cad_renderer.py          # 2D CAD-style floor plans
│   └── renderer_3d.py           # 3D visualization (future)
├── 📊 analytics/                # Analysis and reporting
│   ├── space_analyzer.py        # Space utilization analysis
│   ├── chart_generator.py       # Charts and dashboards
│   └── report_generator.py      # PDF report generation
├── 🌐 templates/                # HTML templates
│   ├── base.html               # Base template
│   ├── index.html              # Landing page
│   ├── design.html             # Design input form
│   ├── results.html            # Results display
│   ├── gallery.html            # Design gallery
│   ├── about.html              # About page
│   └── error.html              # Error handling
├── 🎨 static/                   # Static web assets
│   ├── css/style.css           # Custom styles
│   ├── js/app.js               # JavaScript functionality
│   └── output/                 # Generated design files
└── 📁 output/                   # Design output directory
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
```

### Customization
- **Room Standards**: Modify `ROOM_STANDARDS` in `calculator.py`
- **FAR Guidelines**: Update `FAR_GUIDELINES` for different regions
- **Vastu Principles**: Customize `vastu_principles` dictionary
- **Styling**: Edit `static/css/style.css` for UI customization

## 📊 Sample Outputs

### Design Results
- **Total Built Area**: 1,850 sq.ft
- **Carpet Area**: 1,480 sq.ft  
- **Efficiency Ratio**: 80%
- **Utilization Score**: 85/100
- **Estimated Cost**: ₹32.5 Lakhs
- **Timeline**: 14 months

### Generated Files
- 📐 `floor_plan.png` - Professional 2D blueprint
- 📊 `space_allocation.png` - Space distribution pie chart
- 📈 `efficiency_dashboard.png` - Comprehensive analytics
- 📄 `design_report.pdf` - Complete documentation
- 💾 `design_data.json` - Raw design data
- 📦 `complete_package.zip` - All files bundled

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Install missing packages
pip install -r requirements.txt

# For visualization issues
pip install matplotlib seaborn

# For PDF generation
pip install reportlab
```

**Port Already in Use**
```bash
# Kill existing process
lsof -ti:5000 | xargs kill -9

# Or use different port
python app.py --port 5001
```

**Permission Errors**
```bash
# On Windows, run as administrator
# On macOS/Linux, check file permissions
chmod +x run.py
```

### Debug Mode
```bash
# Enable detailed error messages
export FLASK_DEBUG=1
python app.py
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Vastu Shastra** principles for traditional architectural wisdom
- **Building codes** and regulations for compliance standards
- **Open source community** for excellent Python libraries
- **Architectural professionals** for domain expertise validation

## 📞 Support

- 📧 **Email**: support@architecturaldesign.ai
- 📖 **Documentation**: [Wiki](wiki-url)
- 🐛 **Issues**: [GitHub Issues](issues-url)
- 💬 **Discussions**: [GitHub Discussions](discussions-url)

---

<div align="center">
  <strong>🏠 Building Dreams with AI 🏠</strong><br>
  Made with ❤️ for architects, builders, and dreamers
</div>
