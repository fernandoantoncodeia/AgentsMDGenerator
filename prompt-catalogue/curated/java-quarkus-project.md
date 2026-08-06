---
title: Java Quarkus Project
trigger: project contains pom.xml or build.gradle declaring Quarkus extensions (quarkus-*),
  or a src/main/java source tree
---
- Build and test with the Maven wrapper when one is committed (`./mvnw`); fall back to `mvn` only when the repo has no wrapper.
- Use records for immutable DTOs; reserve Lombok for types that carry real behavior.
- Return Mutiny `Uni<T>` / `Multi<T>` on reactive paths; never block a reactive thread with a synchronous JDBC call.
- Test with `@QuarkusTest` + RestAssured for integration and JUnit 5 + Mockito for unit; run single classes with `-Dtest=<Class>` instead of full scans.
- Keep configuration in `application.properties` with per-environment overrides; never hardcode endpoints or credentials in Java.
