# Testing Strategies and Quality Assurance

## Overview

This context provides comprehensive guidelines for implementing effective testing strategies that ensure code quality, prevent regressions, and maintain system reliability. Use these practices to build confidence in your software through systematic testing approaches.

## Testing Pyramid and Strategy

### Testing Pyramid Structure

```
    /\
   /  \     E2E Tests (Few)
  /____\    - User journey validation
 /      \   - Cross-system integration
/________\  Integration Tests (Some)
           - API contract testing
           - Database integration
           - Service communication
___________
           Unit Tests (Many)
           - Function-level testing
           - Business logic validation
           - Edge case coverage
```

### Test Distribution Guidelines

- **70% Unit Tests**: Fast, isolated, comprehensive coverage
- **20% Integration Tests**: Component interaction validation
- **10% End-to-End Tests**: Critical user journey verification

## Unit Testing Best Practices

### Core Principles

- **Fast**: Tests should run quickly (< 1ms per test)
- **Independent**: Tests don't depend on each other
- **Repeatable**: Same results every time
- **Self-Validating**: Clear pass/fail without manual inspection
- **Timely**: Written before or with the code

### Unit Test Structure (AAA Pattern)

```javascript
describe("UserService", () => {
  it("should calculate user score correctly", () => {
    // Arrange
    const user = new User({ points: 100, level: 5 });
    const service = new UserService();

    // Act
    const score = service.calculateScore(user);

    // Assert
    expect(score).toBe(500);
  });
});
```

### What to Test in Unit Tests

- **Business Logic**: Core algorithms and calculations
- **Edge Cases**: Boundary conditions and error scenarios
- **Input Validation**: Parameter checking and sanitization
- **State Changes**: Object state modifications
- **Return Values**: Expected outputs for given inputs

### Unit Testing Checklist

- [ ] Each function/method has corresponding tests
- [ ] Happy path scenarios are covered
- [ ] Edge cases and error conditions are tested
- [ ] Input validation is verified
- [ ] Mocks are used for external dependencies
- [ ] Tests are readable and well-named
- [ ] Test coverage meets team standards (typically 80%+)

### Common Unit Testing Patterns

**Test Doubles**:

```javascript
// Mock - Verify interactions
const mockEmailService = jest.fn();
userService.sendWelcomeEmail = mockEmailService;
userService.registerUser(userData);
expect(mockEmailService).toHaveBeenCalledWith(userData.email);

// Stub - Control return values
const stubDatabase = {
  findUser: jest.fn().mockReturnValue({ id: 1, name: "John" }),
};

// Spy - Monitor real object behavior
const spy = jest.spyOn(userService, "validateEmail");
userService.registerUser(userData);
expect(spy).toHaveBeenCalled();
```

## Integration Testing Strategies

### Types of Integration Tests

**API Integration Tests**

- Test HTTP endpoints with real requests
- Validate request/response contracts
- Test authentication and authorization
- Verify error handling and status codes

**Database Integration Tests**

- Test data persistence and retrieval
- Validate complex queries and transactions
- Test database constraints and relationships
- Verify migration scripts

**Service Integration Tests**

- Test communication between services
- Validate message passing and event handling
- Test circuit breakers and retry logic
- Verify service discovery and load balancing

### Integration Test Example

```javascript
describe("User API Integration", () => {
  beforeEach(async () => {
    await setupTestDatabase();
  });

  afterEach(async () => {
    await cleanupTestDatabase();
  });

  it("should create user and return 201", async () => {
    const userData = {
      name: "John Doe",
      email: "john@example.com",
    };

    const response = await request(app)
      .post("/api/users")
      .send(userData)
      .expect(201);

    expect(response.body).toMatchObject({
      id: expect.any(Number),
      name: userData.name,
      email: userData.email,
    });

    // Verify database state
    const user = await User.findById(response.body.id);
    expect(user).toBeTruthy();
  });
});
```

### Integration Testing Checklist

- [ ] API endpoints are tested with various inputs
- [ ] Database operations are verified
- [ ] External service integrations are tested
- [ ] Error scenarios and timeouts are handled
- [ ] Authentication and authorization work correctly
- [ ] Data validation across system boundaries
- [ ] Performance under normal load is acceptable

## End-to-End Testing Approaches

### E2E Testing Scope

- **Critical User Journeys**: Core business workflows
- **Cross-Browser Compatibility**: Major browser support
- **Mobile Responsiveness**: Different screen sizes
- **Performance Validation**: Load times and responsiveness
- **Security Verification**: Authentication flows

### E2E Test Example (Playwright)

```javascript
test("user registration and login flow", async ({ page }) => {
  // Navigate to registration
  await page.goto("/register");

  // Fill registration form
  await page.fill('[data-testid="name"]', "John Doe");
  await page.fill('[data-testid="email"]', "john@example.com");
  await page.fill('[data-testid="password"]', "securePassword123");

  // Submit and verify redirect
  await page.click('[data-testid="register-button"]');
  await expect(page).toHaveURL("/dashboard");

  // Verify user is logged in
  await expect(page.locator('[data-testid="user-name"]')).toContainText(
    "John Doe"
  );

  // Test logout
  await page.click('[data-testid="logout-button"]');
  await expect(page).toHaveURL("/login");
});
```

### E2E Testing Best Practices

- **Page Object Model**: Encapsulate page interactions
- **Data Management**: Use test-specific data and cleanup
- **Stable Selectors**: Use data-testid attributes
- **Wait Strategies**: Explicit waits for dynamic content
- **Parallel Execution**: Run tests concurrently when possible

### E2E Testing Checklist

- [ ] Critical user paths are covered
- [ ] Tests run reliably in CI/CD pipeline
- [ ] Test data is managed and cleaned up
- [ ] Screenshots/videos captured on failures
- [ ] Cross-browser testing implemented
- [ ] Mobile testing included
- [ ] Performance thresholds validated

## Test Automation Frameworks

### Popular Testing Frameworks

**JavaScript/TypeScript**

- **Jest**: Unit and integration testing
- **Playwright**: E2E testing with multi-browser support
- **Cypress**: E2E testing with great developer experience
- **Testing Library**: Component testing utilities

**Python**

- **pytest**: Flexible testing framework
- **unittest**: Built-in testing framework
- **Selenium**: Web automation
- **requests**: API testing

**Java**

- **JUnit**: Unit testing standard
- **TestNG**: Advanced testing framework
- **Mockito**: Mocking framework
- **RestAssured**: API testing

**C#**

- **NUnit**: Unit testing framework
- **xUnit**: Modern testing framework
- **Moq**: Mocking framework
- **SpecFlow**: BDD testing

### Framework Selection Criteria

- **Language Ecosystem**: Native language support
- **Team Expertise**: Learning curve and adoption
- **Feature Requirements**: Specific testing needs
- **CI/CD Integration**: Pipeline compatibility
- **Community Support**: Documentation and plugins

## Test Data Management

### Test Data Strategies

**Static Test Data**

- Predefined datasets for consistent testing
- Version controlled with code
- Good for regression testing
- Limited flexibility for edge cases

**Dynamic Test Data**

- Generated during test execution
- Factories and builders for object creation
- Better coverage of edge cases
- Requires cleanup strategies

**Test Data Isolation**

- Each test uses independent data
- Prevents test interference
- Enables parallel execution
- Requires efficient setup/teardown

### Test Data Patterns

**Object Mother Pattern**

```javascript
class UserMother {
  static validUser() {
    return {
      name: "John Doe",
      email: "john@example.com",
      age: 30,
    };
  }

  static minorUser() {
    return {
      ...this.validUser(),
      age: 16,
    };
  }

  static userWithLongName() {
    return {
      ...this.validUser(),
      name: "A".repeat(100),
    };
  }
}
```

**Builder Pattern**

```javascript
class UserBuilder {
  constructor() {
    this.user = {
      name: "Default Name",
      email: "default@example.com",
      age: 25,
    };
  }

  withName(name) {
    this.user.name = name;
    return this;
  }

  withEmail(email) {
    this.user.email = email;
    return this;
  }

  build() {
    return { ...this.user };
  }
}

// Usage
const user = new UserBuilder()
  .withName("Jane Doe")
  .withEmail("jane@example.com")
  .build();
```

## Performance Testing

### Types of Performance Tests

**Load Testing**

- Normal expected load
- Validate system performance under typical usage
- Identify performance baselines
- Verify SLA compliance

**Stress Testing**

- Beyond normal capacity
- Find breaking points
- Test system recovery
- Identify failure modes

**Spike Testing**

- Sudden load increases
- Test auto-scaling
- Validate circuit breakers
- Check system stability

**Volume Testing**

- Large amounts of data
- Database performance
- Memory usage patterns
- Storage capacity limits

### Performance Testing Tools

- **Artillery**: Load testing toolkit
- **JMeter**: Comprehensive performance testing
- **k6**: Developer-centric load testing
- **Gatling**: High-performance load testing
- **Lighthouse**: Web performance auditing

### Performance Test Example (k6)

```javascript
import http from "k6/http";
import { check, sleep } from "k6";

export let options = {
  stages: [
    { duration: "2m", target: 100 }, // Ramp up
    { duration: "5m", target: 100 }, // Stay at 100 users
    { duration: "2m", target: 200 }, // Ramp up to 200
    { duration: "5m", target: 200 }, // Stay at 200
    { duration: "2m", target: 0 }, // Ramp down
  ],
};

export default function () {
  let response = http.get("https://api.example.com/users");

  check(response, {
    "status is 200": (r) => r.status === 200,
    "response time < 500ms": (r) => r.timings.duration < 500,
  });

  sleep(1);
}
```

## Security Testing

### Security Testing Types

**Authentication Testing**

- Login/logout functionality
- Password policies
- Multi-factor authentication
- Session management

**Authorization Testing**

- Role-based access control
- Permission boundaries
- Privilege escalation prevention
- Resource access validation

**Input Validation Testing**

- SQL injection prevention
- XSS protection
- Command injection prevention
- File upload security

**Security Test Examples**

```javascript
describe("Security Tests", () => {
  it("should prevent SQL injection", async () => {
    const maliciousInput = "'; DROP TABLE users; --";

    const response = await request(app)
      .get(`/api/users?name=${maliciousInput}`)
      .expect(400);

    expect(response.body.error).toContain("Invalid input");
  });

  it("should require authentication for protected routes", async () => {
    await request(app).get("/api/admin/users").expect(401);
  });

  it("should sanitize XSS attempts", async () => {
    const xssPayload = '<script>alert("xss")</script>';

    const response = await request(app)
      .post("/api/comments")
      .send({ content: xssPayload })
      .expect(201);

    expect(response.body.content).not.toContain("<script>");
  });
});
```

## Test-Driven Development (TDD)

### TDD Cycle (Red-Green-Refactor)

**1. Red Phase**

- Write a failing test
- Test should be minimal and focused
- Verify test fails for the right reason

**2. Green Phase**

- Write minimal code to make test pass
- Don't worry about code quality yet
- Focus on making the test pass quickly

**3. Refactor Phase**

- Improve code quality
- Remove duplication
- Ensure tests still pass

### TDD Example

```javascript
// 1. Red: Write failing test
describe("Calculator", () => {
  it("should add two numbers", () => {
    const calc = new Calculator();
    expect(calc.add(2, 3)).toBe(5);
  });
});

// 2. Green: Minimal implementation
class Calculator {
  add(a, b) {
    return 5; // Hardcoded to pass test
  }
}

// 3. Refactor: Proper implementation
class Calculator {
  add(a, b) {
    return a + b;
  }
}
```

### TDD Benefits

- **Design Improvement**: Tests drive better API design
- **Documentation**: Tests serve as living documentation
- **Confidence**: High test coverage from the start
- **Regression Prevention**: Immediate feedback on changes

## Behavior-Driven Development (BDD)

### BDD Structure (Given-When-Then)

```gherkin
Feature: User Registration
  As a new user
  I want to register for an account
  So that I can access the application

  Scenario: Successful registration
    Given I am on the registration page
    When I fill in valid user details
    And I submit the registration form
    Then I should be redirected to the dashboard
    And I should see a welcome message
```

### BDD Implementation (Cucumber/Jest)

```javascript
const { Given, When, Then } = require("@cucumber/cucumber");

Given("I am on the registration page", async function () {
  await this.page.goto("/register");
});

When("I fill in valid user details", async function () {
  await this.page.fill('[name="email"]', "user@example.com");
  await this.page.fill('[name="password"]', "password123");
});

When("I submit the registration form", async function () {
  await this.page.click('[type="submit"]');
});

Then("I should be redirected to the dashboard", async function () {
  await expect(this.page).toHaveURL("/dashboard");
});
```

## Continuous Testing in CI/CD

### Pipeline Integration

**Pre-commit Hooks**

- Run unit tests before commits
- Lint and format code
- Check test coverage thresholds
- Validate commit messages

**Pull Request Checks**

- Full test suite execution
- Code coverage reporting
- Security vulnerability scanning
- Performance regression testing

**Deployment Pipeline**

- Smoke tests after deployment
- Health checks and monitoring
- Rollback triggers on test failures
- Production monitoring validation

### CI/CD Configuration Example (GitHub Actions)

```yaml
name: Test Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: "16"

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test:unit

      - name: Run integration tests
        run: npm run test:integration

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Upload coverage
        uses: codecov/codecov-action@v1

      - name: Security scan
        run: npm audit
```

## Test Metrics and Quality Gates

### Key Testing Metrics

**Coverage Metrics**

- **Line Coverage**: Percentage of code lines executed
- **Branch Coverage**: Percentage of code branches tested
- **Function Coverage**: Percentage of functions called
- **Statement Coverage**: Percentage of statements executed

**Quality Metrics**

- **Test Pass Rate**: Percentage of tests passing
- **Test Execution Time**: Time to run test suites
- **Flaky Test Rate**: Tests that intermittently fail
- **Defect Escape Rate**: Bugs found in production

**Velocity Metrics**

- **Test Creation Rate**: New tests added over time
- **Test Maintenance Effort**: Time spent fixing tests
- **Feedback Time**: Time from code change to test results
- **Deployment Frequency**: Releases enabled by testing confidence

### Quality Gates

```yaml
quality_gates:
  unit_tests:
    coverage_threshold: 80%
    max_execution_time: 5m

  integration_tests:
    coverage_threshold: 70%
    max_execution_time: 15m

  e2e_tests:
    critical_path_coverage: 100%
    max_execution_time: 30m

  performance_tests:
    response_time_p95: 500ms
    error_rate_threshold: 0.1%
```

## Testing Anti-Patterns to Avoid

### Common Testing Mistakes

**The Ice Cream Cone**

- Too many E2E tests, few unit tests
- Slow feedback and brittle tests
- High maintenance overhead

**The Testing Trophy (Inverted)**

- Skipping integration tests
- Gap between unit and E2E tests
- Missing component interaction validation

**Flaky Tests**

- Tests that pass/fail inconsistently
- Often due to timing issues or dependencies
- Erodes confidence in test suite

**Test Pollution**

- Tests affecting each other
- Shared state between tests
- Non-deterministic test results

### Best Practices to Follow

**Test Independence**

- Each test should run in isolation
- Use setup/teardown for clean state
- Avoid shared test data

**Meaningful Test Names**

- Describe what is being tested
- Include expected behavior
- Use consistent naming conventions

**Fast Feedback**

- Prioritize fast-running tests
- Parallelize test execution
- Fail fast on critical issues

**Maintainable Tests**

- Keep tests simple and focused
- Use helper functions for common operations
- Regular test refactoring

Remember: Effective testing is about building confidence in your software through the right mix of test types, comprehensive coverage of critical paths, and continuous improvement of testing practices based on feedback and metrics.
