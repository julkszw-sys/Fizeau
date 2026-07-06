# Fizeau RGB Gains + simple UI patch

Adds true per-channel RGB gains to Fizeau and exposes them in the full Fizeau app and Tesla overlay.

## New settings

```ini
red_gain_day = 1.000000
green_gain_day = 0.985000
blue_gain_day = 0.970000

red_gain_night = 1.000000
green_gain_night = 0.985000
blue_gain_night = 0.970000
```

Range: `0.50` to `1.50`; default: `1.00`.

## UI

The patch adds sliders:

- Red gain
- Green gain
- Blue gain

They appear in the Fizeau app under `Colors -> RGB gains` and in the Tesla overlay after Hue.

## Build

Use the supplied GitHub Actions workflow:

`.github/workflows/build-rgb-gains-ui.yml`

Run it manually from GitHub's Actions tab. The artifact will contain the built Fizeau output from `out/`.

## Suggested starting preset

```ini
temperature_day = 6500
saturation_day = 1.000000
hue_day = 0.000000
red_gain_day = 1.000000
green_gain_day = 0.985000
blue_gain_day = 0.970000
contrast_day = 1.140000
gamma_day = 2.280000
luminance_day = 0.000000
components = all
```

Do not mix old Fizeau app/overlay/sysmodule with this patched build. Install the whole generated package together.
trigger build
