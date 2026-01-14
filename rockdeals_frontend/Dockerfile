FROM node:20-slim

WORKDIR /app

# Copy package.json first to leverage Docker cache
COPY rockdeals_frontend/package.json /app/package.json

# Install dependencies (uses npm by default; cloud shell typically has npm)
RUN npm install

# Copy frontend source
COPY rockdeals_frontend /app

# Expose Vite dev server port
EXPOSE 5173

# Run Vite dev server bound to 0.0.0.0
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
