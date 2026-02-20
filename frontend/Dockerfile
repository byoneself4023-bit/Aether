# Frontend - Next.js
FROM node:20-alpine AS builder

WORKDIR /app

# Build-time arguments for NEXT_PUBLIC_ env vars (baked into JS bundle)
ARG NEXT_PUBLIC_AUTH_URL=http://localhost:8003
ARG NEXT_PUBLIC_PORTFOLIO_URL=http://localhost:8001
ARG NEXT_PUBLIC_LLM_URL=http://localhost:8002

ENV NEXT_PUBLIC_AUTH_URL=$NEXT_PUBLIC_AUTH_URL
ENV NEXT_PUBLIC_PORTFOLIO_URL=$NEXT_PUBLIC_PORTFOLIO_URL
ENV NEXT_PUBLIC_LLM_URL=$NEXT_PUBLIC_LLM_URL

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application (NEXT_PUBLIC_ vars are embedded at this stage)
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001

# Copy built assets
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Change ownership
RUN chown -R nextjs:nodejs /app

USER nextjs

# Expose port
EXPOSE 3000

# Set environment
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget -q --spider http://localhost:3000 || exit 1

# Run the application
CMD ["node", "server.js"]
