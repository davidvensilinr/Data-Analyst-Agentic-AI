# Professional Red, Black & White Color Theme

## Overview

This document describes the professional color scheme applied throughout the Autonomous Data Analyst frontend application. The theme uses only three primary colors:

- **Primary Red**: #C41E3A (Brand/Accent color - buttons, links, highlights)
- **Dark Charcoal**: #1F1F1F (Text, primary UI elements)
- **Pure White**: #FFFFFF (Backgrounds, cards, neutral space)

With grayscale neutrals for depth:
- **Light Gray**: #F8F8F8 (Subtle backgrounds)
- **Medium Gray**: #666666 (Secondary text)
- **Border Gray**: #E5E5E5 (Dividers, borders)

## Dark Mode Variants

### Light Mode (Default)
- Background: White (#FFFFFF)
- Text: Dark Charcoal (#1F1F1F)
- Accents: Professional Red (#C41E3A)

### Dark Mode
- Background: Very Dark (#0F0F0F)
- Card Background: Charcoal (#1F1F1F)
- Text: Off-White (#F5F5F5)
- Accents: Brighter Red (#FF4A5A) - adjusted for contrast

## Implementation

### CSS Variables (app/globals.css)

```css
/* Light Mode */
:root {
  --primary: #C41E3A;           /* Professional Red */
  --secondary: #1F1F1F;          /* Dark Charcoal */
  --background: #FFFFFF;         /* Pure White */
  --foreground: #1F1F1F;         /* Dark Text */
  --border: #E5E5E5;             /* Light Gray Border */
  --muted: #F8F8F8;              /* Subtle Background */
}

/* Dark Mode */
.dark {
  --primary: #FF4A5A;            /* Bright Red */
  --secondary: #E5E5E5;          /* Light Text */
  --background: #0F0F0F;         /* Very Dark */
  --foreground: #F5F5F5;         /* Off-White Text */
  --border: #333333;             /* Dark Border */
  --muted: #333333;              /* Dark Subtle */
}
```

## Color Usage by Component

### Navigation & Headers
- Background: White (light) / Charcoal (dark)
- Text: Dark Charcoal / Off-White
- Border: Light Gray
- Logo Accent: Professional Red

### Buttons
- Primary Buttons: Professional Red bg, White text
- Hover: Darker Red (#B21634)
- Secondary Buttons: Light Gray bg, Dark text
- Outline Buttons: Gray border, Dark text

### Cards & Containers
- Background: White (light) / Charcoal (dark)
- Border: Light Gray / Dark Gray
- Hover Border: Light Red (#FFE0E6) / Dark Red

### Links
- Color: Professional Red (#C41E3A)
- Hover: Darker Red (#B21634)

### Status Indicators
- Success: Dark Green (kept for semantic clarity)
- Error: Professional Red (#C41E3A)
- Warning: Dark Orange
- Info: Dark Blue

### Charts & Data Visualization
- Primary Series: Professional Red (#C41E3A)
- Secondary: Dark Charcoal (#1F1F1F)
- Tertiary: Medium Gray (#666666)
- Grid Lines: Light Gray / Dark Gray

### Form Elements
- Input Background: White / Very Dark (#2A2A2A)
- Input Border: Light Gray / Dark Gray
- Focus Border: Professional Red
- Label Text: Dark Charcoal / Off-White

## Pages Updated

1. **Landing Page** (`app/page.tsx`)
   - Hero section: White background, Red CTAs
   - Feature cards: White cards, Red accents
   - Footer: Black section with White text

2. **Projects Page** (`app/projects/page.tsx`)
   - Header: White bg with Red links
   - Project cards: White with Red hover borders
   - Buttons: Red primary, outline secondary

3. **Datasets Page** (`app/projects/[id]/datasets/page.tsx`)
   - Navigation: White bg, Red back link
   - Dataset cards: White with Red hover
   - Action buttons: Red primary

4. **Upload Page** (`app/projects/[id]/upload/page.tsx`)
   - Form cards: White with Gray borders
   - Upload button: Red primary
   - Metadata boxes: Light Gray bg
   - Error alerts: Red border and bg

5. **Profile Page** (`app/projects/[id]/datasets/[datasetId]/profile/page.tsx`)
   - Header: White bg with Red accents
   - Cards: White bg, Red hovers
   - Loader: Red spinner

6. **Query Page** (`app/projects/[id]/datasets/[datasetId]/query/page.tsx`)
   - Form: White card, Red submit button
   - Plan execution: Gray dividers, Red spinner
   - Results tabs: Gray borders, Red active
   - Charts: Red primary data series

## Professional Design Features

### Visual Hierarchy
- **Primary**: Professional Red - Main actions, important elements
- **Secondary**: Dark Charcoal - Text, navigation
- **Tertiary**: Light Gray - Subtle backgrounds, borders

### Accessibility
- High contrast ratios (WCAG AA compliant)
- Clear distinction between interactive and static elements
- Consistent color coding across all pages

### Consistency
- Same color tokens used across all components
- Unified dark mode experience
- Predictable color behavior

## CSS Class Examples

```tsx
// Primary Button
<Button className="bg-red-600 hover:bg-red-700 text-white">
  Action
</Button>

// Secondary Button
<Button variant="outline" className="border-gray-300 text-black dark:text-white dark:border-gray-700">
  Cancel
</Button>

// Card with Red Hover
<Card className="border border-gray-200 dark:border-gray-800 hover:border-red-300 dark:hover:border-red-900 transition-colors">
  Content
</Card>

// Link
<Link className="text-red-600 hover:text-red-700">
  Back to Project
</Link>
```

## Future Maintenance

When adding new components:
1. Use CSS custom properties (--primary, --secondary, etc.)
2. Never hardcode colors directly
3. Use only red, black, white, and gray neutrals
4. Test both light and dark modes
5. Ensure WCAG AA contrast ratios
6. Document any color changes here

## Color Palette Quick Reference

| Element | Light Mode | Dark Mode |
|---------|-----------|-----------|
| Primary Action | #C41E3A | #FF4A5A |
| Text | #1F1F1F | #F5F5F5 |
| Background | #FFFFFF | #0F0F0F |
| Cards | #FFFFFF | #1F1F1F |
| Borders | #E5E5E5 | #333333 |
| Hover State | #B21634 | #D63949 |
| Muted Text | #666666 | #999999 |
| Subtle BG | #F8F8F8 | #333333 |
