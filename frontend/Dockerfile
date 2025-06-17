FROM node:18-alpine

# Устанавливаем необходимые зависимости для сборки
RUN apk add --no-cache python3 make g++

WORKDIR /app

# Сначала копируем все файлы проекта
COPY . .

# Очищаем кэш npm и node_modules для чистой установки
RUN rm -rf node_modules package-lock.json
RUN npm cache clean --force

# Устанавливаем все зависимости
RUN npm install

EXPOSE 3000

# Запускаем приложение
CMD ["npm", "run", "dev"]
