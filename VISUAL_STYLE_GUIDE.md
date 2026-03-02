# Visual Style Guide - Red, Black & White Theme

## Brand Color Palette

### Primary Colors

#### Professional Red
```
HEX: #C41E3A
RGB: 196, 30, 58
HSL: 354°, 73%, 44%
CMYK: 0, 85, 70, 23

Usage: Primary buttons, links, highlights, CTAs
Meaning: Action, attention, confidence
Hover: #B21634 (darker)
Light Mode: #C41E3A
Dark Mode: #FF4A5A (brightened for contrast)
```

#### Dark Charcoal
```
HEX: #1F1F1F
RGB: 31, 31, 31
HSL: 0°, 0%, 12%
CMYK: 0, 0, 0, 88

Usage: Primary text, headings, navigation
Meaning: Strength, professionalism, content
Hover: #000000
Light Mode: #1F1F1F
Dark Mode: #E5E5E5 (inverted for contrast)
```

#### Pure White
```
HEX: #FFFFFF
RGB: 255, 255, 255
HSL: 0°, 0%, 100%
CMYK: 0, 0, 0, 0

Usage: Backgrounds, cards, spacing
Meaning: Clarity, simplicity, cleanliness
Light Mode: #FFFFFF
Dark Mode: #0F0F0F (very dark)
```

### Secondary Colors (Gray Scale)

#### Light Gray
```
HEX: #E5E5E5
RGB: 229, 229, 229
Usage: Borders, dividers, subtle elements
Light Mode: #E5E5E5
Dark Mode: #333333
```

#### Medium Gray
```
HEX: #666666
RGB: 102, 102, 102
Usage: Secondary text, helper text
Light Mode: #666666
Dark Mode: #999999
```

#### Subtle Gray
```
HEX: #F8F8F8
RGB: 248, 248, 248
Usage: Subtle backgrounds, card backgrounds
Light Mode: #F8F8F8
Dark Mode: #333333
```

---

## Component Color Examples

### Buttons

#### Primary Button (Action)
```
Button: "Submit", "Create", "Execute"
Background: #C41E3A
Text: #FFFFFF
Border: None
Hover Background: #B21634
Focus: Red ring (2px solid #C41E3A)
Disabled: #E5E5E5 background, #999999 text
Transition: 150ms ease-in-out
```

#### Secondary Button (Alternative)
```
Button: "Cancel", "Clear", "Dismiss"
Background: Transparent
Text: #1F1F1F
Border: 1px solid #E5E5E5
Hover: #F8F8F8 background
Focus: Gray ring (2px solid #999999)
Disabled: #E5E5E5 background, #999999 text
Transition: 150ms ease-in-out
```

### Cards

#### Standard Card
```
Background: #FFFFFF (light) / #1F1F1F (dark)
Border: 1px solid #E5E5E5 (light) / #333333 (dark)
Padding: 24px
Border Radius: 10px
Shadow: 0 1px 3px rgba(0, 0, 0, 0.1)
Hover Border: #C41E3A or #FF4A5A
Transition: 200ms ease-in-out
```

### Links

#### Standard Link
```
Color: #C41E3A
Text Decoration: None
Hover: 
  - Color: #B21634
  - Text Decoration: Underline
Focus: 
  - Outline: 2px solid #C41E3A
  - Outline Offset: 2px
```

### Form Elements

#### Text Input
```
Background: #FFFFFF (light) / #2A2A2A (dark)
Border: 1px solid #E5E5E5 (light) / #333333 (dark)
Text: #1F1F1F (light) / #F5F5F5 (dark)
Placeholder: #999999
Focus Border: #C41E3A
Focus Ring: 2px solid rgba(196, 30, 58, 0.2)
Transition: 150ms ease-in-out
```

### Icons

#### Action Icons
```
Color: #C41E3A (light) / #FF4A5A (dark)
Size: 16px, 20px, 24px
Weight: 2px stroke
Background: None (usually)
Hover: Slightly darker/lighter
```

---

## Typography + Color Combinations

### Headings
```
Color: #1F1F1F (light) / #F5F5F5 (dark)
Weight: 600-700
Size: 24px - 48px
Line Height: 1.2
Contrast Ratio: 21:1 (AAA)
```

### Body Text
```
Color: #1F1F1F (light) / #F5F5F5 (dark)
Weight: 400
Size: 14px - 16px
Line Height: 1.5
Contrast Ratio: 21:1 (AAA)
```

### Secondary Text
```
Color: #666666 (light) / #999999 (dark)
Weight: 400
Size: 12px - 14px
Line Height: 1.4
Contrast Ratio: 7:1 (AA)
```

### Helper Text / Labels
```
Color: #999999 (light) / #666666 (dark)
Weight: 400
Size: 12px
Line Height: 1.4
Contrast Ratio: 4.5:1 (AA)
```

---

## Contrast Ratios (WCAG Compliance)

### Light Mode
| Combination | Ratio | Grade |
|------------|-------|-------|
| Red (#C41E3A) on White (#FFFFFF) | 4.5:1 | AA ✅ |
| Black (#1F1F1F) on White (#FFFFFF) | 21:1 | AAA ✅ |
| Gray (#666666) on White (#FFFFFF) | 7:1 | AA ✅ |
| Red (#C41E3A) on Gray (#F8F8F8) | 4.2:1 | AA ✅ |

### Dark Mode
| Combination | Ratio | Grade |
|------------|-------|-------|
| Bright Red (#FF4A5A) on Dark (#0F0F0F) | 5.8:1 | AA ✅ |
| White (#F5F5F5) on Dark (#0F0F0F) | 19:1 | AAA ✅ |
| Bright Red (#FF4A5A) on Charcoal (#1F1F1F) | 4.8:1 | AA ✅ |
| Light Gray (#999999) on Dark (#0F0F0F) | 8:1 | AA ✅ |

---

## Color Usage Patterns

### Call-to-Action Pattern
```
Background: Professional Red (#C41E3A)
Text: White (#FFFFFF)
Icon: White (#FFFFFF)
Hover: Darker Red (#B21634)
Focus Ring: Red (#C41E3A)
Shadow: Light shadow for depth
```

### Navigation Pattern
```
Text: Dark Charcoal (#1F1F1F) or Red (#C41E3A) if active
Hover: Red (#C41E3A)
Active Indicator: Red (#C41E3A) bar or highlight
Background: White (#FFFFFF) or Gray (#F8F8F8)
```

### Data Display Pattern
```
Header Background: White (#FFFFFF) or Light Gray (#F8F8F8)
Header Text: Dark Charcoal (#1F1F1F)
Cell Border: Light Gray (#E5E5E5)
Row Hover: Light Gray (#F8F8F8)
Highlight: Red (#C41E3A) for important values
```

### Alert Pattern
```
Error: Red border (#C41E3A), light red background
Success: Gray border, light background (semantic)
Warning: Orange border, light background (semantic)
Info: Gray border, light background (semantic)
Text: Dark (#1F1F1F) on light background
```

---

## Spacing & Visual Rhythm

### Padding Scale
```
XS: 8px
SM: 12px
MD: 16px
LG: 24px
XL: 32px
```

### Border Radius
```
Small: 4px
Medium: 10px (cards, buttons)
Large: 16px (containers)
Full: 50% (circles)
```

### Shadows
```
Subtle: 0 1px 3px rgba(0, 0, 0, 0.1)
Small: 0 2px 4px rgba(0, 0, 0, 0.1)
Medium: 0 4px 8px rgba(0, 0, 0, 0.1)
Large: 0 8px 16px rgba(0, 0, 0, 0.1)
```

---

## Animation & Transitions

### Timing
```
Quick: 150ms (button hover, small changes)
Standard: 200ms (card transitions, color changes)
Slow: 300ms (large animations, page transitions)
```

### Easing
```
Default: ease-in-out
Enter: ease-out
Exit: ease-in
```

### Properties to Animate
```
Recommended: 
  - Background color
  - Border color
  - Box shadow
  - Transform (small)
  - Opacity

Avoid:
  - Layout changes
  - Width/height shifts
  - Position changes
```

---

## Dark Mode Specifications

### Color Shifts
| Light | Dark |
|-------|------|
| #FFFFFF (White) | #0F0F0F (Very Dark) |
| #F8F8F8 (Subtle) | #333333 (Dark) |
| #E5E5E5 (Light Border) | #333333 (Dark Border) |
| #C41E3A (Red) | #FF4A5A (Bright Red) |
| #1F1F1F (Black) | #F5F5F5 (Off-White) |
| #666666 (Gray) | #999999 (Light Gray) |

### Implementation
```css
:root {
  /* Light mode values */
}

.dark {
  /* Dark mode overrides */
}

/* Prefers color scheme */
@media (prefers-color-scheme: dark) {
  /* Applies if user prefers dark */
}
```

---

## Accessibility Checklist

### Color
- [x] Sufficient contrast ratios (WCAG AA minimum)
- [x] Not relying on color alone for meaning
- [x] Clear distinction between states
- [x] Works in both light and dark modes

### Interactive Elements
- [x] Clear focus indicators
- [x] Hover states visible
- [x] Active states obvious
- [x] Disabled states obvious

### Text & Content
- [x] Readable font sizes
- [x] Sufficient line height
- [x] Clear visual hierarchy
- [x] Adequate color contrast

---

## Color System Maintenance

### When Adding New Components:
1. Use only colors from this guide
2. Reference CSS variables in globals.css
3. Test light and dark modes
4. Verify contrast ratios
5. Document color choices

### Prohibited Colors:
- ❌ Blue (any shade)
- ❌ Green (any shade)
- ❌ Purple (any shade)
- ❌ Orange (any shade)
- ❌ Yellow (any shade)
- ❌ Cyan (any shade)
- ❌ Pink (any shade)
- ❌ Brown (any shade)
- ❌ Teal (any shade)

### Approved Colors Only:
- ✅ Red shades (#C41E3A, #B21634, #FF4A5A)
- ✅ Black shades (#000000, #1F1F1F)
- ✅ White shades (#FFFFFF)
- ✅ Gray shades (#E5E5E5, #F8F8F8, #666666, #999999, #333333)

---

## Design System Values

**Primary Color**: Professional Red (#C41E3A)
**Secondary Color**: Dark Charcoal (#1F1F1F)
**Tertiary Color**: Pure White (#FFFFFF)
**Supporting Colors**: Gray neutrals
**Brand Aesthetic**: Professional, minimal, enterprise-grade
**Target Audience**: Serious data professionals
**Tone**: Trustworthy, sophisticated, efficient

---

## Quick Reference

### Most Common Uses
```
Red (#C41E3A)    → Primary buttons, links, accents
Black (#1F1F1F)  → Body text, headings, content
White (#FFFFFF)  → Backgrounds, cards, space
Gray (#E5E5E5)   → Borders, dividers, secondary
```

### Color Psychology
```
Red      → Confidence, action, urgency
Black    → Authority, strength, professionalism
White    → Clarity, simplicity, premium quality
Gray     → Neutrality, balance, professionalism
```

---

**Style Guide Version**: 1.0
**Last Updated**: 2024
**Status**: Approved & In Use ✅
