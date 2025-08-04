import React, { useState, useEffect } from 'react';
import {
  Container,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  Typography,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  FormControlLabel,
  Switch,
  RadioGroup,
  Radio,
  Box
} from '@mui/material';
import axios from 'axios';
import { format } from 'date-fns';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icons
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

interface Product {
  id: string;
  name: string;
  price: number;
  category: string;
  lat: number;
  lon: number;
  description: string;
  created_at?: string;
  rating?: number;
  is_available: boolean;
}

const MapClickHandler = ({ onMapClick }: { onMapClick: (lat: number, lon: number) => void }) => {
  useMapEvents({
    click: (e) => {
      onMapClick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
};

function App() {
  const [query, setQuery] = useState('');
  const [lat, setLat] = useState(0);
  const [lon, setLon] = useState(0);
  const [radius, setRadius] = useState(10);
  const [minPrice, setMinPrice] = useState<number | null>(null);
  const [maxPrice, setMaxPrice] = useState<number | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [results, setResults] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState('list');
  const [sortBy, setSortBy] = useState('relevance');
  const [showOnlyAvailable, setShowOnlyAvailable] = useState(false);
  const [mapCenter, setMapCenter] = useState<[number, number]>([0, 0]);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://34.42.51.177:8000';
      const response = await axios.post(`${apiUrl}/search/`, {
        query,
        lat,
        lon,
        radius_km: radius,
        max_results: 20,
        min_price: minPrice,
        max_price: maxPrice,
        categories: categories.length > 0 ? categories : undefined,
        sort_by: sortBy,
        show_only_available: showOnlyAvailable
      });
      setResults(response.data);
      if (response.data.length > 0) {
        setMapCenter([response.data[0].lat, response.data[0].lon]);
      }
    } catch (error) {
      console.error('Error searching:', error);
    }
    setLoading(false);
  };

  const handleMapClick = (clickedLat: number, clickedLon: number) => {
    setLat(clickedLat);
    setLon(clickedLon);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Inventory Search
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <TextField
                fullWidth
                label="Search Query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                sx={{ mb: 2 }}
              />

              <Typography gutterBottom>Location</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Latitude"
                    type="number"
                    value={lat}
                    onChange={(e) => setLat(parseFloat(e.target.value))}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Longitude"
                    type="number"
                    value={lon}
                    onChange={(e) => setLon(parseFloat(e.target.value))}
                  />
                </Grid>
              </Grid>

              <Typography gutterBottom sx={{ mt: 2 }}>
                Search Radius: {radius} km
              </Typography>
              <Slider
                value={radius}
                onChange={(_, value) => setRadius(value as number)}
                min={1}
                max={100}
                step={1}
              />

              <Typography gutterBottom sx={{ mt: 2 }}>
                Price Range
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Min Price"
                    type="number"
                    value={minPrice || ''}
                    onChange={(e) => setMinPrice(e.target.value ? parseFloat(e.target.value) : null)}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Max Price"
                    type="number"
                    value={maxPrice || ''}
                    onChange={(e) => setMaxPrice(e.target.value ? parseFloat(e.target.value) : null)}
                  />
                </Grid>
              </Grid>

              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>Categories</InputLabel>
                <Select
                  multiple
                  value={categories}
                  onChange={(e) => setCategories(e.target.value as string[])}
                  renderValue={(selected) => (selected as string[]).join(', ')}
                >
                  <MenuItem value="electronics">Electronics</MenuItem>
                  <MenuItem value="clothing">Clothing</MenuItem>
                  <MenuItem value="books">Books</MenuItem>
                  <MenuItem value="furniture">Furniture</MenuItem>
                </Select>
              </FormControl>

              <FormControlLabel
                control={
                  <Switch
                    checked={showOnlyAvailable}
                    onChange={(e) => setShowOnlyAvailable(e.target.checked)}
                  />
                }
                label="Show only available items"
                sx={{ mt: 2, display: 'block' }}
              />

              <Button
                variant="contained"
                color="primary"
                onClick={handleSearch}
                fullWidth
                sx={{ mt: 2 }}
                disabled={loading}
              >
                {loading ? 'Searching...' : 'Search'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
                <Tabs value={viewMode} onChange={(_, value) => setViewMode(value)}>
                  <Tab label="List View" value="list" />
                  <Tab label="Map View" value="map" />
                </Tabs>
              </Box>

              <RadioGroup
                row
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                sx={{ mb: 2 }}
              >
                <FormControlLabel value="relevance" control={<Radio />} label="Relevance" />
                <FormControlLabel value="price_asc" control={<Radio />} label="Price: Low to High" />
                <FormControlLabel value="price_desc" control={<Radio />} label="Price: High to Low" />
                <FormControlLabel value="rating" control={<Radio />} label="Rating" />
                <FormControlLabel value="newest" control={<Radio />} label="Newest" />
              </RadioGroup>

              {viewMode === 'list' ? (
                <Grid container spacing={2}>
                  {results.map((product) => (
                    <Grid item xs={12} key={product.id}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6">{product.name}</Typography>
                          <Typography color="textSecondary">${product.price}</Typography>
                          <Typography>{product.category}</Typography>
                          <Typography>{product.description}</Typography>
                          {product.rating && (
                            <Typography>Rating: {product.rating}/5</Typography>
                          )}
                          {product.created_at && (
                            <Typography>
                              Added: {format(new Date(product.created_at), 'MMM d, yyyy')}
                            </Typography>
                          )}
                          <Typography>
                            Status: {product.is_available ? 'Available' : 'Out of Stock'}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <div style={{ height: '600px', width: '100%' }}>
                  <MapContainer
                    center={mapCenter}
                    zoom={13}
                    style={{ height: '100%', width: '100%' }}
                  >
                    <TileLayer
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    />
                    <MapClickHandler onMapClick={handleMapClick} />
                    {results.map((product) => (
                      <Marker
                        key={product.id}
                        position={[product.lat, product.lon]}
                      >
                        <Popup>
                          <div>
                            <Typography variant="h6">{product.name}</Typography>
                            <Typography>${product.price}</Typography>
                            <Typography>{product.category}</Typography>
                            <Typography>
                              Status: {product.is_available ? 'Available' : 'Out of Stock'}
                            </Typography>
                          </div>
                        </Popup>
                      </Marker>
                    ))}
                  </MapContainer>
                </div>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}

export default App; 