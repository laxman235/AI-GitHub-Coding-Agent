package com.example.demo.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.Size;
import java.math.BigDecimal;

public record ProductDto(
    Long id,

    @NotBlank(message = "Product name cannot be blank")
    @Size(min = 2, max = 100, message = "Product name must be between 2 and 100 characters")
    String name,

    @NotNull(message = "Price is required")
    @Positive(message = "Price must be greater than zero")
    BigDecimal price,

    @Size(max = 500, message = "Description cannot exceed 500 characters")
    String description
) {}
