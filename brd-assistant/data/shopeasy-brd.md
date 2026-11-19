# Business Requirements Document – ShopEasy (v1.0)

## 1. Project Overview
ShopEasy is an online shopping web application for small retailers in India.
Customers can register, log in, browse products, add items to a cart, pay online and request refunds.
Project key: SHOP.

## 2. Login Module
- BR-LOGIN-01: Users log in with registered email and password.
- BR-LOGIN-02: Password must be 11 to 20 characters and contain at least one ₹ or $ symbol.
- BR-LOGIN-03: Account is locked after 4 consecutive failed login attempts.
- BR-LOGIN-04: Locked accounts are automatically unlocked after 23 minutes.
- BR-LOGIN-05: A 7-digit OTP is sent to the registered mobile for new device logins. OTP is valid for 90 seconds.
- BR-LOGIN-06: "Remember Me" keeps the user logged in for 9 days.

## 3. Cart Module
- BR-CART-01: Users can add up to 15 different products to the cart.
- BR-CART-02: Maximum quantity per product is 5.
- BR-CART-03: Cart items are saved for 30 days for logged-in users.
- BR-CART-04: If a product goes out of stock, it is moved to "Saved for later" and the user is notified.
- BR-CART-05: Cart total must update instantly when quantity changes.

## 4. Payment Module
- BR-PAY-01: Supported payment methods: UPI, credit card, debit card and net banking.
- BR-PAY-02: Cash on Delivery is available only for orders below ₹3,000.
- BR-PAY-03: Payment session times out after 8 minutes of inactivity.
- BR-PAY-04: A failed payment can be retried a maximum of 3 times per order.
- BR-PAY-05: Order confirmation email must be sent within 2 minutes of successful payment.

## 5. Refund Module
- BR-REF-01: Refunds can be requested within 10 days of delivery.
- BR-REF-02: Refunds for UPI payments are processed within 3 working days.
- BR-REF-03: Refunds for card payments are processed within 7 working days.
- BR-REF-04: Items marked "Final Sale" are not eligible for refunds.
- BR-REF-05: Partial refunds are allowed for multi-item orders.

## 6. Non-Functional Requirements
- NFR-01: Pages must load within 3 seconds on a 4G connection.
- NFR-02: The system must support 2,000 concurrent users.
- NFR-03: All passwords must be stored encrypted.