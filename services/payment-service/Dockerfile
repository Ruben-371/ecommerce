# ── Stage 1: Builder ───────────────────────────────────────────────────────────
FROM golang:1.22-alpine AS builder
WORKDIR /app

# Cache dependencies
COPY go.mod go.sum ./
RUN go mod download

COPY . .
# CGO disabled for a fully static binary
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -ldflags="-w -s" -o /payment-service ./cmd/server

# ── Stage 2: Minimal runtime ───────────────────────────────────────────────────
FROM scratch AS runner
# Copy CA certs for HTTPS calls to catalog service
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /payment-service /payment-service

EXPOSE 3003
ENTRYPOINT ["/payment-service"]
