package com.project.gateway.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api")
public class ProxyController {

    @GetMapping("/health")
    public Mono<String> health() {
        return Mono.just("OK");
    }
}
