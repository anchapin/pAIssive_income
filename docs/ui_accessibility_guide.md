# UI Accessibility Guide

This guide documents the accessibility features implemented in the pAIssive Income Framework's React frontend.

## Table of Contents
- [Overview](#overview)
- [Implemented Accessibility Features](#implemented-accessibility-features)
- [Component-Specific Accessibility](#component-specific-accessibility)
- [Testing Accessibility](#testing-accessibility)
- [Best Practices](#best-practices)

## Overview

The pAIssive Income Framework is committed to creating an accessible user experience for all users, including those with disabilities. Our UI components follow the Web Content Accessibility Guidelines (WCAG) 2.1 AA standards and implement best practices for keyboard navigation, screen reader support, and visual design.

## Implemented Accessibility Features

### Semantic HTML Structure

The application uses semantic HTML elements to provide a clear document structure:

- `<main>` for the main content area
- `<nav>` for navigation menus
- `<header>` and `<footer>` for page sections
- `<section>` and `<article>` for content organization
- Proper heading hierarchy (`<h1>` through `<h6>`)

### ARIA Attributes

ARIA (Accessible Rich Internet Applications) attributes are used throughout the application:

- `aria-label` for elements without visible text
- `aria-labelledby` to associate elements with their labels
- `aria-describedby` for additional descriptions
- `aria-current="page"` for indicating the current page in navigation
- `aria-expanded` for collapsible sections
- `aria-hidden` for decorative elements
- `role` attributes for custom components

### Keyboard Navigation

All interactive elements are keyboard accessible:

- Logical tab order follows the visual layout
- Focus indicators are visible and high-contrast
- Skip links allow users to bypass navigation
- Custom keyboard shortcuts are documented
- Modal dialogs trap focus appropriately

### Screen Reader Support

The application is optimized for screen reader compatibility:

- All images have meaningful alt text
- Form controls have associated labels
- Status messages are announced with ARIA live regions
- Complex widgets use appropriate ARIA roles and properties
- Dynamic content changes are announced appropriately

### Color and Contrast

The UI design ensures sufficient color contrast:

- Text meets WCAG AA contrast requirements (4.5:1 for normal text, 3:1 for large text)
- Interactive elements have visual states beyond color
- Information is not conveyed by color alone
- Focus indicators are high-contrast

### Responsive Design

The application is responsive and adapts to different viewport sizes:

- Content reflows at different zoom levels
- Text can be resized up to 200% without loss of functionality
- Touch targets are appropriately sized for mobile devices
- Orientation changes are handled gracefully

## Component-Specific Accessibility

### Layout Component

The main Layout component (`Layout.jsx`) includes:

- Proper ARIA roles for navigation and content regions
- Keyboard-accessible drawer toggle
- Skip link for keyboard users to bypass navigation
- Responsive design for different screen sizes

```jsx
<Drawer
  variant="persistent"
  anchor="left"
  open={open}
  role="navigation"
  aria-label="Main Navigation"
>
  {/* Navigation content */}
</Drawer>

<Main open={open}>
  <DrawerHeader />
  <div className="content-wrapper" role="region" aria-label="Main Content">
    {children}
  </div>
</Main>
```

### Authentication Forms

The login and registration forms (`LoginForm.jsx` and `RegisterForm.jsx`) include:

- Proper form validation with error messages
- Password visibility toggles with appropriate ARIA attributes
- Loading states with accessible indicators
- Clear error messaging for form validation

```jsx
<TextField
  required
  fullWidth
  id="username"
  label="Username"
  name="username"
  autoComplete="username"
  autoFocus
  value={values.username}
  onChange={handleChange}
  onBlur={handleBlur}
  error={touched.username && Boolean(errors.username)}
  helperText={touched.username && errors.username}
  disabled={isSubmitting}
/>
```

### Navigation Menu

The navigation menu includes:

- Current page indication with `aria-current="page"`
- Proper focus management
- Keyboard navigation support
- Clear visual indicators for the current selection

```jsx
<ListItemButton
  selected={location.pathname === item.path}
  onClick={() => handleNavigation(item.path)}
  aria-label={item.text}
  aria-current={location.pathname === item.path ? "page" : undefined}
  tabIndex={0}
>
  <ListItemIcon>
    {item.icon}
  </ListItemIcon>
  <ListItemText primary={item.text} />
</ListItemButton>
```

## Testing Accessibility

To ensure the UI meets accessibility standards, we recommend:

1. **Automated Testing**:
   - Use tools like Axe, Lighthouse, or WAVE to identify common issues
   - Integrate accessibility testing into CI/CD pipelines

2. **Manual Testing**:
   - Test with keyboard navigation only
   - Use screen readers (NVDA, JAWS, VoiceOver)
   - Test at different zoom levels and viewport sizes
   - Verify color contrast with tools like the WebAIM Contrast Checker

3. **User Testing**:
   - Conduct testing with users who have disabilities
   - Gather feedback on usability and accessibility

## Best Practices

When developing new UI components or modifying existing ones:

1. **Use Semantic HTML**: Choose the appropriate HTML elements for their semantic meaning.
2. **Add ARIA When Needed**: Use ARIA attributes to enhance accessibility, but prefer native HTML semantics when possible.
3. **Test Keyboard Navigation**: Ensure all interactive elements can be accessed and operated using only a keyboard.
4. **Provide Alternative Text**: Add descriptive alt text for images and icons.
5. **Manage Focus**: Ensure focus is managed appropriately, especially in modal dialogs and dynamic content.
6. **Consider Screen Reader Users**: Test with screen readers to ensure content is properly announced.
7. **Ensure Sufficient Contrast**: Verify that text and interactive elements have sufficient color contrast.
8. **Make Error Messages Accessible**: Ensure error messages are linked to their corresponding form fields and announced to screen readers.
9. **Document Accessibility Features**: Include accessibility information in component documentation.
10. **Stay Current**: Keep up with evolving accessibility standards and best practices.
