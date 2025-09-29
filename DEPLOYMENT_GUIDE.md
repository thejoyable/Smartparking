# 🚗 Smart Parking Streamlit Deployment Guide

## 📋 Prerequisites

- Python 3.8 or higher
- Webcam/Camera access
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 🚀 Quick Deployment

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run app.py
```

### 3. Access the Application
Open your browser and go to: `http://localhost:8501`

## 🌐 Streamlit Cloud Deployment

### Step 1: Prepare Repository
1. Push your code to GitHub repository
2. Ensure all files are included:
   - `app.py`
   - `parking_manager.py`
   - `detection_engine.py`
   - `csv_data_manager.py`
   - `parking_system.py`
   - `requirements.txt`
   - `West_Bengal_Holidays_2025.csv`
   - `parking_data.csv`
   - `.streamlit/config.toml`

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path: `app.py`
6. Click "Deploy!"

## 🔧 Common Issues & Solutions

### Issue 1: Camera Access Denied
**Error**: `Camera not accessible` or `Permission denied`
**Solution**:
- Ensure camera permissions are granted
- Try different browsers (Chrome works best)
- Check if camera is being used by another application

### Issue 2: Module Import Errors
**Error**: `ModuleNotFoundError: No module named 'streamlit'`
**Solution**:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue 3: WebRTC Connection Failed
**Error**: `WebRTC connection failed`
**Solution**:
- Use HTTPS in production (Streamlit Cloud provides this automatically)
- Check firewall settings
- Try different network connection

### Issue 4: Model Loading Errors
**Error**: `YOLO model not found` or `MediaPipe initialization failed`
**Solution**:
- Ensure internet connection for first-time model downloads
- Check available disk space (models are ~50MB)
- Verify all dependencies are installed

### Issue 5: Performance Issues
**Symptoms**: Slow detection, high CPU usage
**Solutions**:
- Close other applications
- Reduce camera resolution in browser
- Use hardware acceleration if available

## 📁 File Structure
```
Smart Parking Streamlit/
├── app.py                          # Main Streamlit application
├── parking_manager.py              # Parking logic and pricing
├── detection_engine.py             # AI detection engine
├── csv_data_manager.py             # CSV data management
├── parking_system.py               # Console-based system
├── requirements.txt                 # Python dependencies
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── West_Bengal_Holidays_2025.csv   # Holiday data
├── parking_data.csv                # Parking data storage
└── models/                         # AI model files (auto-downloaded)
    ├── best.pt
    └── yolo12n.pt
```

## 🎯 Production Deployment Tips

### 1. Environment Variables
Set these for production:
```bash
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
```

### 2. Docker Deployment (Optional)
Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 3. Performance Optimization
- Use `streamlit run app.py --server.maxUploadSize=200` for larger files
- Set `--server.enableCORS=false` for local development
- Use `--server.enableXsrfProtection=false` if needed

## 🐛 Troubleshooting Checklist

- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Camera permissions granted
- [ ] Internet connection for model downloads
- [ ] Sufficient disk space (>500MB)
- [ ] Modern browser with WebRTC support
- [ ] No firewall blocking port 8501
- [ ] Python 3.8+ installed

## 📞 Support

If you encounter issues:
1. Check the browser console for JavaScript errors
2. Check the terminal/console for Python errors
3. Verify all files are present in the repository
4. Test with a simple Streamlit app first
5. Check Streamlit Cloud logs for deployment issues

## 🎉 Success Indicators

Your deployment is successful when:
- ✅ Application loads without errors
- ✅ Camera feed displays
- ✅ AI detection works (vehicle, license plate, gestures)
- ✅ Auto-parking functionality works
- ✅ CSV data saves correctly
- ✅ Continuous detection cycle operates smoothly
