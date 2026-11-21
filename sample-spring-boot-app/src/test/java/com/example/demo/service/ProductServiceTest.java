package com.example.demo.service;

import com.example.demo.dto.ProductDto;
import com.example.demo.exception.ResourceNotFoundException;
import com.example.demo.model.Product;
import com.example.demo.repository.ProductRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ProductServiceTest {

    @Mock
    private ProductRepository productRepository;

    @InjectMocks
    private ProductService productService;

    private Product testProduct;

    @BeforeEach
    void setUp() {
        testProduct = new Product(1L, "Laptop", new BigDecimal("999.99"), "Developer Laptop");
    }

    @Test
    @DisplayName("Should return all products as DTOs")
    void testGetAllProducts() {
        when(productRepository.findAll()).thenReturn(List.of(testProduct));

        List<ProductDto> result = productService.getAllProducts();

        assertThat(result).hasSize(1);
        assertThat(result.get(0).name()).isEqualTo("Laptop");
        verify(productRepository, times(1)).findAll();
    }

    @Test
    @DisplayName("Should return product DTO when found by ID")
    void testGetProductByIdSuccess() {
        when(productRepository.findById(1L)).thenReturn(Optional.of(testProduct));

        ProductDto result = productService.getProductById(1L);

        assertThat(result).isNotNull();
        assertThat(result.id()).isEqualTo(1L);
        assertThat(result.price()).isEqualTo(new BigDecimal("999.99"));
    }

    @Test
    @DisplayName("Should throw ResourceNotFoundException when product ID not found")
    void testGetProductByIdNotFound() {
        when(productRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> productService.getProductById(99L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("99");
    }

    @Test
    @DisplayName("Should save and return newly created product")
    void testCreateProduct() {
        ProductDto inputDto = new ProductDto(null, "Mouse", new BigDecimal("49.99"), "Wireless Mouse");
        Product savedProduct = new Product(2L, "Mouse", new BigDecimal("49.99"), "Wireless Mouse");

        when(productRepository.save(any(Product.class))).thenReturn(savedProduct);

        ProductDto result = productService.createProduct(inputDto);

        assertThat(result.id()).isEqualTo(2L);
        assertThat(result.name()).isEqualTo("Mouse");
        verify(productRepository, times(1)).save(any(Product.class));
    }
}
