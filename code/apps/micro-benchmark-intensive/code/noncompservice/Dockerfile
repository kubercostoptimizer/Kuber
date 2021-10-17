FROM node:12
COPY . ./
ENV UV_THREADPOOL_SIZE=64
RUN npm install
EXPOSE 8081
CMD ["node","service_comp.js"]

