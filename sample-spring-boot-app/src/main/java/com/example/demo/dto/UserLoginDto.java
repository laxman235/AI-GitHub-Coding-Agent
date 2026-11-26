package com.example.demo.dto;

import jakarta.validation.constraints.NotBlank;

public record UserLoginDto(
    @NotBlank(message = "Username or email cannot be blank")
    String usernameOrEmail,

    @NotBlank(message = "Password cannot be blank")
    String password
) {}
