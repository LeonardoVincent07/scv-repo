
# MissionHalo — MVP UX Design Principles

## Overview
MissionHalo ensures that all generated UI components share a consistent look and feel.  
For the MVP, Halo focuses exclusively on enforcing a unified visual design system:
- typography  
- colour palette  
- spacing  
- basic component styling  
- Tailwind-based enforcement  

---

## 1. Colour System

### 1.1 Core Palette
- **Primary (teal):** rgb(26,153,136) / #1A9988  
- **Secondary (orange):** rgb(235,86,0) / #EB5600  
- **Background:** white (#FFFFFF)

### 1.2 Supporting Palette
- Soft green: rgb(176,192,159) / #B0C09F  
- Soft yellow: rgb(241,205,86) / #F1CD56  
- Soft blue-grey: rgb(205,226,235) / #CDE2EB  

Usage:
- Subtle highlights  
- Card accents  
- Status tags  

### 1.3 Grey System
- Primary text: charcoal  
- Secondary text: mid-grey  
- Muted labels/help: light grey  
- Borders: very light grey  

---

## 2. Typography

### 2.1 Typefaces
- **Headings:** Raleway  
- **Body:** Lato  

### 2.2 Rules
- Max 3 font sizes per screen  
- No all-caps except tags  
- Generous line-height for clarity  

---

## 3. Layout & Spacing
- **Base spacing unit: 8px**  
- Generous whitespace  
- Group related items in white cards with soft grey borders  
- Consistent panel-level padding (16–24px)  

---

## 4. Components & Style

### Cards
- White or light grey background  
- Subtle border or shadow  
- Rounded corners  

### Buttons
- Primary: teal bg, white text  
- Secondary: white bg, teal border/text  
- Destructive: orange  

### Navigation
- Light backgrounds  
- Teal underline or pill for active tab  

---

## 5. Tone & Copy (MVP-level)
- Calm, precise, professional  
- Short labels, literal naming  
- Error messages state problem + next action  

---

## 6. Enforcement (Halo Adherence)
Halo adherence = PASS when:
- Components use Raleway/Lato  
- Colours come exclusively from MissionHalo palette  
- Spacing uses Tailwind's 8px-based scale  
- Components follow card/button patterns above  

Halo adherence = FAIL when:
- Arbitrary fonts are used  
- Unapproved colours appear  
- Spacing grid violated  
- Components deviate from visual rules  

---

## 7. Tailwind Configuration Snippet

```js
// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        heading: ['Raleway', 'system-ui', 'sans-serif'],
        body: ['Lato', 'system-ui', 'sans-serif'],
      },
      colors: {
        halo: {
          primary: 'rgb(26,153,136)',     // #1A9988
          secondary: 'rgb(235,86,0)',     // #EB5600
          softGreen: 'rgb(176,192,159)',  // #B0C09F
          softYellow: 'rgb(241,205,86)',  // #F1CD56
          softBlue: 'rgb(205,226,235)',   // #CDE2EB
        },
      },
      borderRadius: {
        halo: '16px',
      },
    },
  },
  plugins: [],
};
```

---

## Storage Location
Place this file in:

```
scv-repo/docs/mission_halo/mission_halo_mvp.md
```

MissionHalo sits alongside MissionFramework as part of the system-wide governance layer.
