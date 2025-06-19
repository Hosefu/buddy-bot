FROM node:18-alpine

# Устанавливаем необходимые зависимости для сборки
RUN apk add --no-cache python3 make g++

WORKDIR /app

# Копируем package.json и package-lock.json (или yarn.lock, и т.д.)
COPY package*.json ./

# Устанавливаем зависимости
# Это создаст слой в Docker-образе, который будет кешироваться
# и пересобираться только при изменении package.json
RUN npm install

# Копируем остальной код приложения
COPY . .

EXPOSE 3000

# Запускаем приложение
CMD ["npm", "run", "dev"]
