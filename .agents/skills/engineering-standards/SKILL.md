---
name: engineering-standards
description: Enforces industry-level engineering standards, emphasizing component reuse and cohesive aesthetics (glassmorphism).
---

# Engineering Standards

This skill documents the industry-level standards to be followed during development. The primary goal is to maximize code reuse, reduce redundancy, and maintain a high-quality, consistent aesthetic.

## 1. Frontend Development Standards

### Component Reusability
- **Check Existing First:** Before creating any new UI component, thoroughly check the existing codebase. If a similar component exists, reuse or extend it rather than building a new one from scratch.
- **Build for Reuse:** When a new component is strictly necessary, build it to be highly generic and configurable (e.g., accepting customizable props for styling and behavior) so it can be reused in future tasks.
- **Centralized Components:** Keep all reusable UI components in a shared, clearly defined directory to ensure they are easily discoverable by others.

### UI & Aesthetics
- **Glassmorphism:** Design new UI elements using a "glass" (glassmorphism) look and feel. This involves:
  - Using semi-transparent background colors (e.g., `rgba(255, 255, 255, 0.1)`).
  - Applying background blur effects (e.g., `backdrop-filter: blur(10px)`).
  - Adding subtle, bright borders to simulate glass edges (e.g., `border: 1px solid rgba(255, 255, 255, 0.2)`).
  - Pairing glass elements with vibrant, dynamic background colors or mesh gradients to emphasize the translucent effect.
- **Modern Polish:** Aim for high-quality, modern web aesthetics with smooth micro-animations for interactive elements (hover, active states).

## 2. Backend Development Standards

### Architecture & Communication
- **RPC First:** Wherever possible, try to make an RPC (Remote Procedure Call) call for interactions instead of traditional REST or ad-hoc methods.
- **Database Readiness:** Although a database is not set up yet, that is something that needs to be added. Ensure the architecture and RPC handlers are designed to easily integrate with a database in the near future.

### Code Reusability & Modularity
- **Avoid Duplication:** Just like the frontend, actively search for existing utilities, middlewares, or services before implementing new logic. Never re-implement what already exists.
- **Framework Extraction:** If you find yourself writing the same logic to solve a problem multiple times (e.g., specific data transformations, validation routines, recurring API wrappers), abstract that logic into a centralized, reusable framework or library module.
- **Modularity:** Ensure background services and handlers are decoupled and modular, making them easier to plug into different parts of the backend system as needed.

## 3. General Practices
- **Refactoring:** Be proactive about refactoring duplicate code into shared modules whenever you spot it.
- **Documentation:** Document newly created reusable components or backend framework utilities so that any developer can easily understand and utilize them.
