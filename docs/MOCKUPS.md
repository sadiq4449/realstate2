# UI/UX layout spec (Figma / AI import friendly)

**Design tokens**

- Background: `#F8F9FA`
- Primary: `#2D9CDB`
- Success: `#27AE60`
- Text primary: `#1a1a1a`
- Text muted: `#6b7280`
- Radius card: `12px`
- Shadow card: `0 8px 24px rgba(0,0,0,0.06)`
- Font: Inter (fallback Poppins, Roboto)

**Breakpoints**

- Mobile: 360×800 frames
- Desktop: 1440×900 frames

---

## 1) Landing (desktop 1440)

- **Nav**: logo left, links (Search, Pricing, Login), primary CTA “List your property”.
- **Hero**: two columns — H1 “Rent homes without friction”, subcopy, dual CTAs (primary filled, ghost “Browse listings”); right: hero image card with rounded corners.
- **Below**: three feature cards (Owners / Seekers / Secure payments) in a row.

## 2) Owner dashboard

- **Top bar**: greeting, subscription badge, “New listing” button (primary).
- **Grid**: listing cards (image slider 16:10, price pill top-right, city, beds/baths chips).
- **Empty state**: illustration + CTA.

## 3) Listing creation (wizard-lite)

- Single-page form sections: Details, Pricing, Location (lat/lng helper text), Amenities chips, Images dropzone.
- Sticky footer: Save draft (ghost), Submit (primary).

## 4) Seeker search

- **Left 320px drawer (collapsible on mobile)**: filters — price range, beds, baths, furnished toggle, amenities multi-select, city.
- **Main**: toggle List | Map; list uses same card component; map full-width panel (Leaflet).
- **Mobile**: filters in bottom sheet.

## 5) Admin dashboard

- **KPI row**: users, listings, pending, MRR (from analytics).
- **Charts**: bar “Listings by city”, line “Revenue” (mock from transactions).
- **Table**: pending listings with Approve / Reject icon buttons; sortable headers.

## 6) Subscription & payment

- Pricing cards (Basic / Pro) with feature bullets; selected state ring `2px solid #2D9CDB`.
- Mock payment panel: card last4 placeholder, “Pay now” success toast `#27AE60`.

## 7) Chat inbox

- **Desktop split**: left 280px thread list (avatar circle, name, snippet, time); right message pane with bubbles (own right-aligned primary tint, other gray-100).
- **Composer**: textarea + attach + send; timestamps `text-xs` muted below bubbles.

## 8) Mobile frames

- Stack nav with hamburger; cards full-bleed with `16px` padding; map tab full screen; chat threads full width with back chevron.

Use **8px spacing grid**, **44px min touch targets**, focus rings `2px outline #2D9CDB`.
