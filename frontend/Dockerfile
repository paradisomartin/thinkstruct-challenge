# Local development only; not a production web server.
FROM node:26-bookworm-slim@sha256:5df79989ed685e09f0a98019db4cebfb22fb9df1a53c0161664a011f7ff6b0f1

WORKDIR /app
RUN mkdir -p node_modules && chown -R node:node /app
USER node

# Refresh the isolated dependency volume from the current lockfile on each start.
CMD ["sh", "-c", "npm ci && exec npm run dev -- --host 0.0.0.0"]
