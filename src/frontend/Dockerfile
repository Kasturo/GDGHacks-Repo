FROM node:20-alpine

WORKDIR /app/src/frontend

COPY src/frontend/package*.json /app/src/frontend/
RUN npm install

COPY . /app

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
