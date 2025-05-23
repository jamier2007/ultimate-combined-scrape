# Vehicle Data Explorer - Web Interface

A beautiful, modern web interface for the Unified Vehicle Data API that makes it easy to search and explore comprehensive vehicle information from multiple data sources.

## Features

### 🎨 Beautiful Modern Design
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Modern UI Components**: Clean cards, smooth animations, and professional styling
- **Gradient Backgrounds**: Eye-catching visual design with professional color schemes
- **Interactive Elements**: Hover effects, smooth transitions, and loading animations

### 🔍 Advanced Search Interface
- **Simple VRM Search**: Enter any UK vehicle registration mark to get comprehensive data
- **Auto-formatting**: VRM input automatically converts to uppercase
- **Force Refresh**: Always gets the latest data for accurate results

### 📊 Data Visualization
- **Source Separation**: Data clearly organized by source (E3Technical vs BookMyGarage)
- **Field Count Badges**: See how many data fields each source provides
- **Performance Metrics**: Display query time and caching status
- **Statistics Bar**: Overview of total fields, sources, and performance

### 🚀 Smart Features
- **Error Handling**: Graceful error messages for API issues or invalid VRMs
- **Loading States**: Professional spinner and status messages during searches
- **Responsive Grid**: Data fields automatically adjust to screen size
- **Hover Effects**: Interactive field highlighting for better user experience

## Data Sources

The website displays data from two primary sources:

### E3 Technical (Technical Data)
- Vehicle specifications and technical details
- Engine information, dimensions, fuel consumption
- Manufacturing and registration data
- DVLA verified information

### BookMyGarage (Service Data)
- Service and maintenance information
- Garage-specific vehicle data
- MOT and service history insights

## Usage

1. **Open the Website**: Navigate to `http://localhost:8000` in your web browser
2. **Enter VRM**: Type in a vehicle registration mark (e.g., "NG04UBV")
3. **Search**: Click "Search Vehicle" to get comprehensive data
4. **Explore Results**: View organized data from both sources with field counts and performance metrics

## Technical Details

### Responsive Breakpoints
- **Desktop**: Full grid layout with side-by-side source cards
- **Tablet**: Responsive grid that adjusts to screen width
- **Mobile**: Single column layout with stacked cards

### Performance Features
- **Async JavaScript**: Non-blocking API calls for smooth user experience
- **Smart Caching**: Shows when data is cached for faster subsequent loads
- **Error Recovery**: Handles network issues and API errors gracefully

### Accessibility
- **Keyboard Navigation**: Full keyboard support for form interactions
- **Screen Reader Friendly**: Proper semantic HTML and ARIA labels
- **High Contrast**: Colors meet WCAG accessibility guidelines
- **Focus Indicators**: Clear visual focus states for all interactive elements

## API Integration

The website seamlessly integrates with the Unified Vehicle Data API:
- **GET /**: Serves the main website interface
- **GET /{vrm}**: Fetches vehicle data using default credentials
- **Error Handling**: Displays meaningful error messages for failed requests
- **Real-time Data**: Always shows the most current vehicle information available

## Browser Support

- **Chrome**: Full support for all features
- **Firefox**: Full support for all features  
- **Safari**: Full support for all features
- **Edge**: Full support for all features
- **Mobile Browsers**: Optimized responsive experience

## Future Enhancements

Potential improvements that could be added:
- **Export Functionality**: Download vehicle data as PDF or JSON
- **Search History**: Save and revisit previous searches
- **Comparison Tool**: Compare data between multiple vehicles
- **Bulk Search**: Upload multiple VRMs for batch processing
- **Data Filtering**: Filter and search within vehicle data fields 