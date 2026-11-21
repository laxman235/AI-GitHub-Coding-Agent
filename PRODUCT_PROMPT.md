# 🎯 Product Vision & Architecture Roadmap

Write your product requirements here! The Autonomous AI Coding Agent reads this file daily to understand what product to build, figures out what features are missing, and implements them incrementally.

---

## 1. Product Overview
- **Product Name:** (e.g., CreatorHub Backend / Food Delivery / E-Commerce Store)
- **Domain:** (e.g., REST API for managing users, products, orders, and payments)
- **Target Tech Stack:** Java 21, Spring Boot 3.x, Spring Data JPA, H2/PostgreSQL, Bean Validation, JUnit 5, Mockito.

---

## 2. Core Modules & Features to Build

### Module 1: User & Authentication Management
- [ ] User entity (id, username, email, passwordHash, role: USER/ADMIN, createdAt)
- [ ] User registration DTO with Bean Validation (@Email, @NotBlank, @Size)
- [ ] UserService with password encoding & duplicate email checks
- [ ] UserController with REST endpoints (POST /api/users/register, GET /api/users/{id})
- [ ] JUnit 5 & Mockito test coverage

### Module 2: Product & Catalog Management
- [x] Product entity (id, name, price, description, createdAt)
- [x] ProductDto with Bean Validation
- [x] ProductService CRUD operations
- [x] ProductController REST endpoints
- [ ] Product categories and search filtering

### Module 3: Order & Transaction Processing
- [ ] Order & OrderItem entities (status: PENDING, PAID, SHIPPED, CANCELLED)
- [ ] OrderService with stock check and total calculation
- [ ] OrderController with checkout endpoints (POST /api/orders, GET /api/orders/user/{userId})
- [ ] Unit and slice tests with Mockito

### Module 4: Payment & Notification Integration
- [ ] Payment entity and transaction logging
- [ ] Notification service (email/webhook simulation)

---

## 3. Architecture & Quality Requirements
1. Constructor-based dependency injection.
2. DTO records for API requests and responses.
3. Proper `@ExceptionHandler` mappings in `GlobalExceptionHandler`.
4. Comprehensive JUnit 5 unit tests with Mockito mocks for every new Service and Controller.
