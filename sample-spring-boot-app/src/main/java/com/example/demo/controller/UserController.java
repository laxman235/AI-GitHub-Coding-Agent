package com.example.demo.controller;

import com.example.demo.dto.UserLoginDto;
import com.example.demo.dto.UserRegistrationDto;
import com.example.demo.model.User;
import com.example.demo.service.UserService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/auth")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping("/register")
    public ResponseEntity<User> registerUser(@Valid @RequestBody UserRegistrationDto dto) {
        User created = userService.registerUser(dto);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PostMapping("/login")
    public ResponseEntity<User> loginUser(@Valid @RequestBody UserLoginDto dto) {
        User user = userService.loginUser(dto);
        return ResponseEntity.ok(user);
    }

    @GetMapping("/users/{id}")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        return ResponseEntity.ok(userService.getUserById(id));
    }

    @GetMapping("/users")
    public ResponseEntity<List<User>> getAllUsers() {
        return ResponseEntity.ok(userService.getAllUsers());
    }
}
