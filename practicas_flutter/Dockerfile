ARG FLUTTER_IMAGE=ghcr.io/cirruslabs/flutter:stable
FROM ${FLUTTER_IMAGE} AS construir
WORKDIR /app
COPY pubspec.yaml pubspec.lock ./
RUN flutter pub get
COPY . .
ARG API_BASE=http://127.0.0.1:8000
RUN flutter build web --release --dart-define=API_BASE=${API_BASE}
FROM nginx:1.27-alpine
COPY --from=construir /app/build/web /usr/share/nginx/html
EXPOSE 80
