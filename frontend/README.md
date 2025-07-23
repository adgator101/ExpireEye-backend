# ExpireEye Frontend

This is the React frontend for ExpireEye, built with Vite, React Router, and Tailwind CSS v4.

## Getting Started

### Install dependencies

```sh
npm install
```

### Start the development server

```sh
npm run dev
```

The app will be available at [http://localhost:5173](http://localhost:5173) by default.

## Project Structure

```
frontend/
├── public/
├── src/
│   ├── assets/                 # Store static assets
│   ├── components/             # Store reusable components here
│   ├── pages/                  # Add Pages here
│   │   ├── LoginPage.jsx
│   │   └── SignupPage.jsx
│   ├── App.jsx
│   ├── index.css
│   └── main.jsx
├── package.json
├── vite.config.js
├── README.md
└── ...
```

## Styling

- Tailwind CSS v4 is installed and configured.
- Shadcn UI is ready for use (run `npx shadcn-ui@latest add <component>` to add components).

## API Integration

- Connect to the backend at `http://127.0.0.1:8000/status`.
- Use `credentials: "include"` in fetch/axios to send cookies for authentication.

## License

MIT
