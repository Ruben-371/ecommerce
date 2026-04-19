package handlers

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/google/uuid"
	"github.com/gorilla/mux"
)

// PaymentRequest represents the incoming payment payload.
type PaymentRequest struct {
	ProductID string  `json:"product_id"`
	Quantity  int     `json:"quantity"`
	UserID    string  `json:"user_id"`
	Amount    float64 `json:"amount"`
}

// PaymentResponse represents the result of a payment attempt.
type PaymentResponse struct {
	TransactionID string    `json:"transaction_id"`
	Status        string    `json:"status"`
	Amount        float64   `json:"amount"`
	Currency      string    `json:"currency"`
	ProcessedAt   time.Time `json:"processed_at"`
	Message       string    `json:"message"`
}

// In-memory store (replace with PostgreSQL in production).
var paymentStore = map[string]PaymentResponse{}

// Health godoc
func Health(w http.ResponseWriter, _ *http.Request) {
	respond(w, http.StatusOK, map[string]string{"status": "ok", "service": "payment-service"})
}

// ProcessPayment simulates a payment transaction and validates stock with the catalog service.
func ProcessPayment(catalogURL string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var req PaymentRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			respondError(w, http.StatusBadRequest, "invalid request body")
			return
		}

		if req.ProductID == "" || req.Quantity <= 0 || req.UserID == "" || req.Amount <= 0 {
			respondError(w, http.StatusBadRequest, "product_id, quantity, user_id and amount are required")
			return
		}

		// Validate product stock via catalog service
		ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
		defer cancel()

		productURL := fmt.Sprintf("%s/api/v1/products/%s", catalogURL, req.ProductID)
		httpReq, _ := http.NewRequestWithContext(ctx, http.MethodGet, productURL, nil)
		resp, err := http.DefaultClient.Do(httpReq)
		if err != nil || resp.StatusCode != http.StatusOK {
			respondError(w, http.StatusServiceUnavailable, "catalog service unavailable")
			return
		}
		defer resp.Body.Close()

		var product map[string]any
		_ = json.NewDecoder(resp.Body).Decode(&product)

		stock, _ := product["stock"].(float64)
		if int(stock) < req.Quantity {
			respondError(w, http.StatusConflict, "insufficient stock")
			return
		}

		// Simulate payment processing (always succeeds in this demo)
		txID := uuid.New().String()
		result := PaymentResponse{
			TransactionID: txID,
			Status:        "approved",
			Amount:        req.Amount,
			Currency:      "USD",
			ProcessedAt:   time.Now().UTC(),
			Message:       "Payment processed successfully (simulated)",
		}
		paymentStore[txID] = result

		respond(w, http.StatusCreated, result)
	}
}

// GetPayment retrieves a stored payment by ID.
func GetPayment(w http.ResponseWriter, r *http.Request) {
	id := mux.Vars(r)["id"]
	payment, ok := paymentStore[id]
	if !ok {
		respondError(w, http.StatusNotFound, "payment not found")
		return
	}
	respond(w, http.StatusOK, payment)
}

func respond(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(payload)
}

func respondError(w http.ResponseWriter, status int, msg string) {
	respond(w, status, map[string]string{"error": msg})
}
