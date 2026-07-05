FROM node:20-alpine

WORKDIR /app

# Instala dependencias primero (mejor cache). node_modules queda en la imagen;
# docker-compose solo monta ./frontend/src encima, así que node_modules persiste.
COPY package.json ./
RUN npm install

COPY . .

EXPOSE 5173

# El comando real lo define docker-compose (npm run dev).
CMD ["npm", "run", "dev"]
