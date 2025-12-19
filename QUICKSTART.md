# 📚 Quick Start Guide

## 🚀 Getting Started

### 1. Start the Application
```bash
python app.py
```

The app will be available at: **http://127.0.0.1:5000**

### 2. Access the Dashboard
- **Home**: http://127.0.0.1:5000/
- **Charts**: http://127.0.0.1:5000/charts

---

## 📤 Upload Data

### CSV Format Required
Your CSV file must have these columns:
```
category,value,recorded_at
Sales,1500.00,2025-01-01 10:00:00
Marketing,2000.00,2025-01-01 11:00:00
Operations,800.50,2025-01-01 12:00:00
```

**Optional column**: `subcategory`

### Upload Methods
1. **Drag & Drop**: Drag CSV file onto the upload zone
2. **Click to Select**: Click upload area and select file
3. **Programmatic** (API):
   ```bash
   curl -X POST -F "file=@data.csv" http://127.0.0.1:5000/upload
   ```

---

## 📊 Key Features

### Dashboard Home
- 📈 View key statistics (total records, values, categories)
- 📤 Upload new data
- 📥 Export options
- 📊 Real-time data summary

### Charts Page
- **Timeseries Chart**: Interactive line chart with fill
- **Category Distribution**: Bar chart showing totals by category
- **Static Chart**: Matplotlib PNG visualization
- **Chart Controls**: Adjust frequency (hourly/daily/weekly/monthly) and date range

### Export Options
- **Excel Report**: Pivot table + raw data sheets
- **CSV Export**: Complete dataset with timestamps

---

## 🔌 API Endpoints

### Get Data
```bash
# All records (paginated)
curl http://127.0.0.1:5000/api/records?page=1&per_page=50

# Filter by category
curl http://127.0.0.1:5000/api/records?page=1&per_page=50&category=Sales

# Aggregated data
curl http://127.0.0.1:5000/api/aggregate?group_by=category

# Timeseries data
curl http://127.0.0.1:5000/api/timeseries?freq=D&days=30

# Dashboard statistics
curl http://127.0.0.1:5000/api/stats
```

### Get Charts
```bash
# Interactive timeseries (Plotly JSON)
curl http://127.0.0.1:5000/api/plotly_timeseries?freq=D&days=30

# Category distribution (Plotly JSON)
curl http://127.0.0.1:5000/api/plotly_category_distribution

# Static chart (PNG image)
curl http://127.0.0.1:5000/static_timeseries.png --output chart.png
```

### Upload
```bash
curl -X POST -F "file=@data.csv" http://127.0.0.1:5000/upload
```

### Export
```bash
# Excel
curl http://127.0.0.1:5000/export/excel --output report.xlsx

# CSV
curl http://127.0.0.1:5000/export/csv --output data.csv
```

---

## 📝 Sample Data Format

### CSV File Example
```csv
category,subcategory,value,recorded_at
Sales,North,1500.00,2025-01-01 10:00:00
Sales,South,1200.00,2025-01-01 10:00:00
Marketing,Digital,2000.00,2025-01-01 11:00:00
Marketing,Print,500.00,2025-01-01 11:00:00
Operations,Maintenance,800.50,2025-01-01 12:00:00
```

---

## 🔧 API Query Parameters

### Pagination
- `page` (default: 1): Page number
- `per_page` (default: 50, max: 1000): Records per page
- `category` (optional): Filter by category

### Timeseries
- `freq` (default: 'D'): Frequency - H (hourly), D (daily), W (weekly), M (monthly)
- `days` (default: 30): Look back days (1-3650)

### Aggregation
- `group_by` (default: 'category'): Group by category or subcategory

---

## 💡 Usage Examples

### Example 1: Upload and View
1. Create `sales_data.csv` with your data
2. Navigate to http://127.0.0.1:5000/
3. Drag-drop the CSV file
4. Click "Upload File"
5. Go to "Charts" to see visualizations

### Example 2: Get Weekly Aggregation
```bash
curl http://127.0.0.1:5000/api/timeseries?freq=W&days=90
```

### Example 3: Filter by Category
```bash
curl "http://127.0.0.1:5000/api/records?category=Sales&per_page=100"
```

### Example 4: Get Last 3 Months Data
```bash
curl http://127.0.0.1:5000/api/timeseries?freq=D&days=90
```

---

## 🛠️ Troubleshooting

### App Won't Start
```bash
# Check if port 5000 is in use
lsof -i :5000

# If in use, kill the process
kill -9 <PID>

# Clean database and restart
rm py_data_app.db
python app.py
```

### Upload Fails
- ✅ Ensure CSV has required columns: category, value, recorded_at
- ✅ Check date format: YYYY-MM-DD HH:MM:SS
- ✅ Ensure values are numeric (int or float)

### No Data Shows Up
- ✅ Upload a CSV file first
- ✅ Check `/api/stats` endpoint to see data count
- ✅ Verify date range matches your data

---

## 📊 Performance Tips

### Large Datasets
- Use paginated API endpoints instead of loading all records
- Filter by category or date range to reduce data size
- Use appropriate aggregation frequency (Weekly/Monthly for large datasets)

### Caching
- Results are cached for 60 seconds
- Cache clears automatically on new uploads
- Use `?_nocache=1` to bypass cache if needed

---

## 🔐 Important Notes

- Default database: **SQLite** (`py_data_app.db`)
- To use MySQL: Set `DB_USER` environment variable
- Max file upload: **16 MB**
- Debug mode: **ON** (for development)

---

## 📞 Common Questions

**Q: How do I change the database to MySQL?**
A: Set environment variables:
```bash
export DB_USER=root
export DB_PASS=password
export DB_HOST=localhost
export DB_NAME=my_database
python app.py
```

**Q: Can I upload the same file twice?**
A: Yes, it will add duplicate records. To prevent this, use unique timestamps or add a validation step.

**Q: How many records can I upload?**
A: Tested with thousands. Performance depends on your machine and database type.

**Q: Where is my data stored?**
A: In `py_data_app.db` (SQLite) in the same directory.

---

## 🎉 You're All Set!

Your data analytics dashboard is ready to use. Start uploading and visualizing your data! 📊
