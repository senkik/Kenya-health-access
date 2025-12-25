# Kenya Health Access - Frontend

Modern React frontend for the Kenya Health Access platform.

## Tech Stack

- **React 19** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **React Query** - Data fetching and caching
- **Axios** - HTTP client
- **Leaflet** - Interactive maps (to be integrated)

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
copy .env.example .env

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
src/
├── components/       # Reusable UI components
│   ├── Layout.jsx
│   ├── Navbar.jsx
│   ├── Footer.jsx
│   ├── FacilityCard.jsx
│   └── SearchBar.jsx
├── pages/           # Page components
│   ├── Home.jsx
│   ├── Search.jsx
│   ├── FacilityDetail.jsx
│   └── About.jsx
├── services/        # API integration
│   └── api.js
├── utils/           # Helper functions
│   └── helpers.js
├── App.jsx          # Main app component with routing
└── main.jsx         # Entry point
```

## Features

- 🔍 **Search** - Find healthcare facilities by name, location, or services
- 🗺️ **Browse** - Explore facilities by county
- 📱 **Responsive** - Mobile-first design with Tailwind CSS
- ⚡ **Fast** - Optimized with Vite and React Query caching
- 🎨 **Modern UI** - Clean, accessible interface

## Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000/api
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## API Integration

The frontend connects to the Django REST API backend. Make sure the backend is running at
 `http://localhost:8000` before starting the frontend.

## PWA Integration

The frontend is configured with PWA features, including a service worker and manifest file. Make sure the backend is running at
 `http://localhost:8000` before starting the frontend.      
    

## Next Steps

- [ ] Add Leaflet map integration
- [ ] Implement PWA features (service worker, manifest)
- [ ] Add offline support
- [ ] Implement user authentication
- [ ] Add facility reviews and ratings
