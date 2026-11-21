package com.example.demo.service;

import com.example.demo.dto.UserRegistrationDto;
import com.example.demo.exception.ResourceNotFoundException;
import com.example.demo.model.Role;
import com.example.demo.model.User;
import com.example.demo.repository.UserRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

@Service
@Transactional
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public User registerUser(UserRegistrationDto dto) {
        if (userRepository.existsByEmail(dto.email())) {
            throw new IllegalArgumentException("User with email " + dto.email() + " already exists");
        }
        if (userRepository.existsByUsername(dto.username())) {
            throw new IllegalArgumentException("User with username " + dto.username() + " already exists");
        }
        User user = new User(dto.username(), dto.email(), dto.password(), Role.USER);
        return userRepository.save(user);
    }

    @Transactional(readOnly = true)
    public User getUserById(Long id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + id));
    }

    @Transactional(readOnly = true)
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
}
