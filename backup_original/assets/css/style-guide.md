# AgIL Style Guide

## Colors

| Token          | Hex       | Usage                                    |
|----------------|-----------|------------------------------------------|
| `--primary`    | `#339966` | Navbar, buttons, headings, accents       |
| `--primary-light` | `#3db576` | Hover states, lighter accents         |
| `--primary-dark`  | `#2a7d53` | Active states, dark accents           |
| `--bg`         | `#ffffff` | Page background                          |
| `--muted`      | `#f5f7f6` | Section backgrounds, cards               |
| `--text`       | `#1f2937` | Primary text color                       |
| `--text-light` | `#6b7280` | Secondary text, descriptions             |
| `--border`     | `#e5e7eb` | Borders, dividers                        |

## Typography

- **Font**: Calibri, Arial, sans-serif, system fallback
- **Base size**: 16px
- **Scale**: `sm` 0.875rem, base 1rem, `lg` 1.125rem, `xl` 1.25rem, `2xl` 1.5rem, `3xl` 2rem, `4xl` 2.5rem
- **Line height**: 1.7 (body), 1.3 (headings)

## Spacing (8px Grid)

| Token       | Value |
|-------------|-------|
| `--space-1` | 4px   |
| `--space-2` | 8px   |
| `--space-3` | 16px  |
| `--space-4` | 24px  |
| `--space-5` | 32px  |
| `--space-6` | 48px  |
| `--space-7` | 64px  |
| `--space-8` | 96px  |

## Components

### Navbar (`.site-nav`)
- Sticky top, `--primary` background, white text
- Hamburger menu on mobile (≤768px)
- Active link has white bottom border

### Member Card (`.member-card`)
- 200px wide, centered text
- Circular avatar (150×150px) with shadow
- Role badge with color variants: `.chair`, `.co-chair`, `.member`, `.ra`, `.intern`

### Publication Card (`.pub-card`)
- Flex layout: left thumbnail (260px), right content
- Abstract clamped to 3 lines
- Buttons: `.btn-primary` (green) and `.btn-outline` (bordered)
- Stacks vertically on mobile

### Project Tile (`.project-tile`)
- Grid layout with `auto-fill, minmax(320px, 1fr)`
- Image top, content body with tags

### Timeline (`.timeline`)
- Vertical line with dot markers
- Date, title, description per item

## Breakpoints

| Name    | Max-width | Usage                        |
|---------|-----------|------------------------------|
| Mobile  | 576px     | Single column, small cards   |
| Tablet  | 768px     | 2 columns, hamburger menu    |
| Desktop | 1024px+   | Full layout, 3+ columns      |

## File Structure

```
assets/css/main.css    — All styles (single file)
assets/js/main.js      — Carousel, hamburger, utilities
assets/images/carousel/ — Homepage carousel images
```
