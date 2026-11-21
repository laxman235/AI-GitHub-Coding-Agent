package com.example.demo.controller;

import com.example.demo.dto.ProductDto;
import com.example.demo.service.ProductService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(ProductController.class)
class ProductControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ProductService productService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("GET /api/products returns list of products")
    void testGetAllProducts() throws Exception {
        ProductDto dto = new ProductDto(1L, "Keyboard", new BigDecimal("79.99"), "Mechanical Keyboard");
        when(productService.getAllProducts()).thenReturn(List.of(dto));

        mockMvc.perform(get("/api/products"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].name").value("Keyboard"))
                .andExpect(jsonPath("$[0].price").value(79.99));
    }

    @Test
    @DisplayName("POST /api/products creates product on valid payload")
    void testCreateProductValid() throws Exception {
        ProductDto input = new ProductDto(null, "Monitor", new BigDecimal("299.99"), "4K Monitor");
        ProductDto output = new ProductDto(10L, "Monitor", new BigDecimal("299.99"), "4K Monitor");

        when(productService.createProduct(any(ProductDto.class))).thenReturn(output);

        mockMvc.perform(post("/api/products")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(input)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value(10))
                .andExpect(jsonPath("$.name").value("Monitor"));
    }

    @Test
    @DisplayName("POST /api/products returns 400 Bad Request on invalid price")
    void testCreateProductInvalidPrice() throws Exception {
        ProductDto invalidInput = new ProductDto(null, "Invalid", new BigDecimal("-10.00"), "Negative price");

        mockMvc.perform(post("/api/products")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(invalidInput)))
                .andExpect(status().isBadRequest());
    }
}
