# Frontend - React + TypeScript Starter

Clean React + TypeScript setup with modern tooling.

## Tech Stack

- **React 18** with TypeScript
- **Vite** - Fast build tool and dev server
- **TailwindCSS v4** - Modern utility-first CSS framework
- **Zustand** - Lightweight state management (installed, ready to use)

## Getting Started

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Build

```bash
npm run build
```

The production build will be in the `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── App.tsx           # Main application component
│   ├── main.tsx          # Application entry point
│   └── index.css         # TailwindCSS + custom styles
├── index.html
├── package.json
├── tsconfig.json         # TypeScript configuration
├── vite.config.ts        # Vite configuration
└── README.md
```

## Features

- **Vite** - Lightning-fast HMR and optimized builds
- **TailwindCSS v4** - Latest version with `@import "tailwindcss"` syntax
- **TypeScript** - Full type safety
- **Zustand** - Simple state management (when you need it)
- **ESLint** - Code quality
- **Hot Module Replacement** - Instant updates during development

## Custom Styles

The project includes custom utility classes in `src/index.css`:

- `.glass-card` - Glassmorphism effect with backdrop blur
- `.gradient-text` - Gradient text effect

## Next Steps

1. Create your components in `src/`
2. Add routes if needed (install `react-router-dom`)
3. Use Zustand for state management when needed
4. Build your application!

## License

MIT License
