# Frontend multi-stage Dockerfile

# Build stage
FROM node:20-alpine AS build
WORKDIR /app

# Install build deps for native modules
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    autoconf \
    automake \
    libtool \
    pkgconfig \
    nasm \
    git \
    bash

# Enable corepack for pnpm
RUN corepack enable

# Copy package files
COPY package.json pnpm-lock.yaml ./

# 安装所有依赖
RUN pnpm install --frozen-lockfile --prod=false

# 路径调试信息
RUN echo "=== Path Debug Information ===" && \
    echo "Working directory: $(pwd)" && \
    echo "Node modules exists: $(test -d node_modules && echo 'YES' || echo 'NO')" && \
    echo "vue-tsc binary exists: $(test -f node_modules/.bin/vue-tsc && echo 'YES' || echo 'NO')" && \
    echo "vue-tsc symlink info:" && ls -la node_modules/.bin/vue-tsc 2>/dev/null || echo "Not found" && \
    echo "Actual vue-tsc files:" && find node_modules -name '*vue-tsc*' -type f 2>/dev/null | head -5

# 将 node_modules/.bin 添加到 PATH
ENV PATH="/app/node_modules/.bin:${PATH}"

# 验证 PATH 设置
RUN echo "=== PATH Verification ===" && \
    echo "PATH: $PATH" && \
    echo "vue-tsc in PATH: $(which vue-tsc 2>/dev/null && echo 'YES' || echo 'NO')" && \
    vue-tsc --version 2>/dev/null || echo "vue-tsc not executable"

# Copy source code
COPY . .

# Build the application (use dlx to avoid local bin resolution issues)
RUN pnpm dlx vite@6 build

# Serve stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]