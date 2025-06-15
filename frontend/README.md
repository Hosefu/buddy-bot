# BudTest Frontend

React-based Telegram Mini App frontend for BudTest. It follows the architecture described in `docs/` and includes basic authentication, flows navigation and step pages.

## Development

### Local

```bash
npm install
npm run dev
```

### Docker Compose

Start the backend and frontend together:

```bash
docker-compose up frontend web
```

### Mock Telegram WebApp

To run the app without Telegram, open `public/mock-telegram.html` in your browser.
It provides a minimal mock of the Telegram Mini App API for local development.

For quick testing you can use refresh tokens from the `tokens_*.txt` files in the project root and paste them into the login form.

Run tests with:

```bash
npm run test
```
