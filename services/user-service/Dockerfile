# ── Stage 1: Dependencies ──────────────────────────────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app

COPY package*.json ./
# Install only production deps; ci ensures reproducible installs
RUN npm ci --omit=dev

# ── Stage 2: Production image ──────────────────────────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app

# Principle of least privilege: run as non-root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

COPY --chown=appuser:appgroup --from=deps /app/node_modules ./node_modules
COPY --chown=appuser:appgroup src ./src
COPY --chown=appuser:appgroup package.json ./

USER appuser

EXPOSE 3001

# Graceful shutdown support
ENV NODE_ENV=production
CMD ["node", "src/index.js"]
