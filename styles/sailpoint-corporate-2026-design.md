---
version: 2.0
name: SailPoint Corporate 2026
description: Official 2026 SailPoint brand standard optimized for dark mode presentations. Deep gradient blending black, deep cobalt (#011C48), and cobalt (#0033A1) with glowing accents in aqua (#54C0E8) and hot pink (#D60EB5), paired with monoline tech iconography.
template_file: "templates/SailPoint PowerPoint Template 2026.pptx"
assets_dir: "assets/themes/sailpoint"
logo_path: "assets/themes/sailpoint/logo.svg"

colors:
  primary: "#FFFFFF"
  accent: "#54C0E8"
  accent-alt: "#D60EB5"
  accent-green: "#93D500"
  cobalt: "#0033A1"
  deep-cobalt: "#011C48"
  background: "#000000"
  surface: "#000000"
  surface-soft: "#0B111E"
  hairline: "#415364"
  divider: "#415364"
  ink: "#FFFFFF"
  ink-muted: "#DAE1E9"
  card-background: "#0B111E"
  card-border: "#415364"

css_variables:
  --sp-bg-gradient: "radial-gradient(circle at 85% 15%, rgba(0, 51, 161, 0.5) 0%, rgba(1, 28, 72, 0.7) 45%, #000000 100%)"
  --sp-card-gradient: "linear-gradient(145deg, rgba(11, 17, 30, 0.95) 0%, rgba(1, 28, 72, 0.35) 100%)"
  --sp-glow-aqua: "0 0 24px rgba(84, 192, 232, 0.35)"
  --sp-glow-pink: "0 0 24px rgba(214, 14, 181, 0.35)"

typography:
  google-fonts: "Poppins:wght@300;400;500;600;700"
  font-family: "'Poppins', system-ui, -apple-system, sans-serif"
  title-slide:
    fontFamily: "'Poppins', system-ui, sans-serif"
    fontSize: 56px
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: -0.02em
  title-content:
    fontFamily: "'Poppins', system-ui, sans-serif"
    fontSize: 38px
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: -0.01em
  subtitle:
    fontFamily: "'Poppins', system-ui, sans-serif"
    fontSize: 22px
    fontWeight: 400
    lineHeight: 1.4
  body-lg:
    fontFamily: "'Poppins', system-ui, sans-serif"
    fontSize: 20px
    fontWeight: 400
    lineHeight: 1.5
  body-md:
    fontFamily: "'Poppins', system-ui, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
  caption:
    fontFamily: "'Poppins', system-ui, sans-serif"
    fontSize: 13px
    fontWeight: 300
    lineHeight: 1.4
  bullets:
    fontFamily: "'Poppins', system-ui, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.55

spacing:
  xxs: 4px
  xs: 8px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
  section: 80px

rounded:
  none: 0px
  sm: 6px
  md: 10px
  lg: 14px
  xl: 18px
  full: 9999px
  default: xl

components:
  slide-background:
    background: "var(--sp-bg-gradient), #000000"
  slide-title-text:
    textColor: "{colors.ink}"
    typography: "{typography.title-content}"
  slide-body-text:
    textColor: "{colors.ink-muted}"
    typography: "{typography.body-md}"
  card:
    backgroundColor: "{colors.card-background}"
    borderColor: "{colors.card-border}"
    rounded: "{rounded.default}"
    padding: "{spacing.lg}"
    boxShadow: "0 8px 32px rgba(0, 0, 0, 0.45)"
  callout-box:
    backgroundColor: "{colors.surface-soft}"
    borderColor: "{colors.accent}"
    textColor: "{colors.ink}"
    rounded: "{rounded.default}"
    padding: "{spacing.md}"
    boxShadow: "var(--sp-glow-aqua)"
  badge:
    backgroundColor: "rgba(84, 192, 232, 0.15)"
    borderColor: "{colors.accent}"
    textColor: "{colors.accent}"
    rounded: "{rounded.full}"
    padding: "4px 12px"
  iconography:
    library: "lucide"
    strokeWidth: "1.75px"
    color: "{colors.accent}"
    colorHighlight: "{colors.accent-alt}"
    size: "26px"
    container: "badge"
    badgeBackground: "rgba(84, 192, 232, 0.12)"
    badgeBorder: "rgba(84, 192, 232, 0.25)"
    badgeGlow: "var(--sp-glow-aqua)"
---

## Overview

Official 2026 SailPoint corporate brand design. Optimized for dark mode presentations, establishing high contrast and clean hierarchy with deep cobalt backgrounds, white headings, and aqua/magenta glowing accents.

## Visual Execution

**Motif:** Clean, monoline tech iconography (identity security, shield nodes, access tokens, governance workflows) in `#54C0E8` (aqua) and `#FFFFFF`. Icons are drawn from `assets/themes/sailpoint/media/*.svg`.

**Execution:**
- **Backgrounds:** Deep layered gradient (`#000000` base with radial cobalt highlight at top-right `#0033A1` / `#011C48`).
- **Headings:** Poppins 600 weight in pure white `#FFFFFF`.
- **Body & Subtitles:** Poppins 400 weight in soft silver-gray `#DAE1E9`.
- **Cards & Containers:** Background `#0B111E`, border 1px solid `#415364`, border-radius 18px, with subtle top-border highlight.
- **Accents:** Electric aqua (`#54C0E8`) for primary tags, active states, and focal metrics; hot pink (`#D60EB5`) for critical highlights; lime (`#93D500`) for verified status.

**Diagram Grammar:** Monoline nodes with 1.5px strokes in aqua or white over dark surfaces; straight connectors with neat arrowheads; glowing aqua node marking the focal point.

**Mode:** dark
