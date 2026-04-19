package main

import (
	"log"
	"net/http"
	"os"

	"github.com/gorilla/mux"
	"ecommerce-lite/payment-service/internal/handlers"
	"ecommerce-lite/payment-service/internal/middleware"
)

func main() {
	port := getEnv("PORT", "3003")
	catalogURL := getEnv("CATALOG_SERVICE_URL", "http://catalog-service:3002")

	r := mux.NewRouter()

	// Middleware
	r.Use(middleware.Logger)
	r.Use(middleware.RecoverPanic)

	// Routes
	r.HandleFunc("/health", handlers.Health).Methods(http.MethodGet)
	r.HandleFunc("/api/payments/process", handlers.ProcessPayment(catalogURL)).Methods(http.MethodPost)
	r.HandleFunc("/api/payments/{id}", handlers.GetPayment).Methods(http.MethodGet)

	log.Printf("Payment Service listening on :%s", port)
	if err := http.ListenAndServe(":"+port, r); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}

func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
