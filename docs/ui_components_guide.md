# UI Components Guide

This guide documents the React frontend components and their usage in the pAIssive Income Framework.

## Table of Contents
- [Layout Components](#layout-components)
- [Authentication Components](#authentication-components)
- [Page Components](#page-components)
- [Styling](#styling)
- [Accessibility](#accessibility)

## Layout Components

### Main Layout

The main layout component (`Layout.jsx`) provides the application shell with a responsive navigation drawer and content area.

**Features:**
- Persistent navigation drawer with collapsible functionality
- Responsive design that adapts to different screen sizes
- Accessible navigation with proper ARIA attributes
- Consistent styling across the application

**Usage:**
```jsx
import Layout from '../components/Layout/Layout';

function MyPage() {
  return (
    <Layout>
      <YourPageContent />
    </Layout>
  );
}
```

## Authentication Components

### Login Form

The `LoginForm` component (`LoginForm.jsx`) provides a secure authentication interface with validation.

**Features:**
- Form validation with error messages
- Password visibility toggle
- Security enhancements to prevent credential exposure
- Loading state during authentication
- Accessible form controls with proper ARIA attributes

### Registration Form

The `RegisterForm` component (`RegisterForm.jsx`) allows users to create new accounts with validation.

**Features:**
- Comprehensive form validation
- Password visibility toggles
- Security enhancements for credential handling
- Grid-based responsive layout
- Accessible form controls

## Page Components

### Dashboard Page

The Dashboard page (`DashboardPage.jsx`) displays key metrics and project information.

**Features:**
- Summary cards for revenue and subscriber metrics
- Project progress tracking
- Responsive grid layout

### Niche Analysis Page

The Niche Analysis page (`NicheAnalysisPage.jsx`) provides tools for analyzing market opportunities.

**Features:**
- Interactive form for niche research
- Data visualization components:
  - Opportunity radar charts
  - Opportunity bar charts
  - Score distribution pie charts
- Tabbed interface for different visualization types

### Profile Page

The Profile page (`ProfilePage.jsx`) allows users to view and edit their account information.

**Features:**
- User profile display with avatar
- Editable form fields for profile information
- Role-based chip indicators
- Loading states during data fetching and saving

## Styling

The application uses a combination of Material-UI styled components and custom CSS:

- **Global Styles** (`index.css`): Provides base styling for the application
- **Component-Specific Styles**: Uses Material-UI's `styled` API for component-level styling
- **Responsive Design**: Media queries ensure proper display across device sizes

**Example:**
```css
@media (max-width: 600px) {
  .content-wrapper {
    padding: 8px;
  }
  .card, .card-header, .card-body {
    padding: 8px;
    margin-bottom: 12px;
  }
}
```

## Accessibility

The frontend implements several accessibility enhancements:

### Keyboard Navigation
- All interactive elements are keyboard accessible
- Focus management for modal dialogs and drawers
- Proper tab order throughout the application

### ARIA Attributes
- `aria-label` for buttons and controls without visible text
- `aria-current` for indicating current page in navigation
- `aria-expanded` for collapsible sections
- `role` attributes for semantic HTML

### Screen Reader Support
- Meaningful alt text for images
- Semantic HTML structure
- Hidden helper text for complex interactions
- Status announcements for dynamic content changes

### Color Contrast
- All text meets WCAG AA standards for contrast
- Visual indicators beyond color for state changes

For detailed information about accessibility features and best practices, see the [UI Accessibility Guide](ui_accessibility_guide.md).

## Best Practices

When developing new UI components or modifying existing ones:

1. Ensure responsive design works on all screen sizes
2. Implement proper accessibility attributes
3. Use consistent styling patterns
4. Include loading states for asynchronous operations
5. Implement proper form validation
6. Handle error states gracefully
7. Use semantic HTML elements where possible
