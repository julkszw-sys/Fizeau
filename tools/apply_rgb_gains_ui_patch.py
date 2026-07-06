#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    p = ROOT / path
    return p.read_text(encoding='utf-8')

def write(path, data):
    p = ROOT / path
    p.write_text(data, encoding='utf-8')

def insert_after(path, anchor, block, marker):
    s = read(path)
    if marker in s:
        return
    if anchor not in s:
        raise SystemExit(f"Anchor not found in {path}: {anchor!r}")
    s = s.replace(anchor, anchor + block, 1)
    write(path, s)

def insert_before(path, anchor, block, marker):
    s = read(path)
    if marker in s:
        return
    if anchor not in s:
        raise SystemExit(f"Anchor not found in {path}: {anchor!r}")
    s = s.replace(anchor, block + anchor, 1)
    write(path, s)

def replace_once(path, old, new, marker=None):
    s = read(path)
    if marker and marker in s:
        return
    if old not in s:
        raise SystemExit(f"Text not found in {path}: {old!r}")
    s = s.replace(old, new, 1)
    write(path, s)

# ---- Core ABI / settings -------------------------------------------------
insert_after(
    'common/include/types.h',
    '#define DEFAULT_HUE 0.0f\n',
    '\n'
    'typedef float ColorGain;\n'
    '#define MIN_GAIN 0.50f\n'
    '#define MAX_GAIN 1.50f\n'
    '#define DEFAULT_GAIN 1.0f\n'
    'typedef struct {\n'
    '    ColorGain r, g, b;\n'
    '} ColorGains;\n'
    '#define DEFAULT_GAINS { DEFAULT_GAIN, DEFAULT_GAIN, DEFAULT_GAIN }\n',
    'ColorGains'
)

insert_after(
    'common/include/fizeau.h',
    '    Hue hue;\n',
    '    ColorGains gains;\n',
    'ColorGains gains'
)

insert_after(
    'common/include/config.hpp',
    '        .hue = DEFAULT_HUE,\n',
    '        .gains = DEFAULT_GAINS,\n',
    '.gains = DEFAULT_GAINS'
)

insert_after(
    'common/include/color.hpp',
    'ColorMatrix filter_matrix(Component filter);\n',
    'ColorMatrix gains_matrix(ColorGains gains);\n',
    'gains_matrix'
)

insert_after(
    'common/src/color.cpp',
    '    return arr;\n}\n\nstd::tuple<float, float, float> whitepoint(Temperature temperature) {',
    '\nColorMatrix gains_matrix(ColorGains gains) {\n'
    '    gains.r = std::clamp(gains.r, MIN_GAIN, MAX_GAIN);\n'
    '    gains.g = std::clamp(gains.g, MIN_GAIN, MAX_GAIN);\n'
    '    gains.b = std::clamp(gains.b, MIN_GAIN, MAX_GAIN);\n'
    '\n'
    '    return {\n'
    '        gains.r, 0.0f,    0.0f,\n'
    '        0.0f,    gains.g, 0.0f,\n'
    '        0.0f,    0.0f,    gains.b,\n'
    '    };\n'
    '}\n',
    'ColorMatrix gains_matrix'
)
# The previous insertion consumed part of the whitepoint anchor; repair if needed.
replace_once(
    'common/src/color.cpp',
    '}\nstd::tuple<float, float, float> whitepoint(Temperature temperature) {',
    '}\n\nstd::tuple<float, float, float> whitepoint(Temperature temperature) {',
    marker=None
) if False else None

# If the above exact compound anchor failed in some source layout, try a safer second form.
s = read('common/src/color.cpp')
if 'ColorMatrix gains_matrix' not in s:
    insert_before(
        'common/src/color.cpp',
        'std::tuple<float, float, float> whitepoint(Temperature temperature) {',
        'ColorMatrix gains_matrix(ColorGains gains) {\n'
        '    gains.r = std::clamp(gains.r, MIN_GAIN, MAX_GAIN);\n'
        '    gains.g = std::clamp(gains.g, MIN_GAIN, MAX_GAIN);\n'
        '    gains.b = std::clamp(gains.b, MIN_GAIN, MAX_GAIN);\n'
        '\n'
        '    return {\n'
        '        gains.r, 0.0f,    0.0f,\n'
        '        0.0f,    gains.g, 0.0f,\n'
        '        0.0f,    0.0f,    gains.b,\n'
        '    };\n'
        '}\n\n',
        'ColorMatrix gains_matrix'
    )

insert_after(
    'common/src/config.cpp',
    '    sanitize_minmax(this->profile.day_settings .hue, MIN_HUE, MAX_HUE);\n'
    '    sanitize_minmax(this->profile.night_settings.hue, MIN_HUE, MAX_HUE);\n',
    '    sanitize_minmax(this->profile.day_settings .gains.r, MIN_GAIN, MAX_GAIN);\n'
    '    sanitize_minmax(this->profile.day_settings .gains.g, MIN_GAIN, MAX_GAIN);\n'
    '    sanitize_minmax(this->profile.day_settings .gains.b, MIN_GAIN, MAX_GAIN);\n'
    '    sanitize_minmax(this->profile.night_settings.gains.r, MIN_GAIN, MAX_GAIN);\n'
    '    sanitize_minmax(this->profile.night_settings.gains.g, MIN_GAIN, MAX_GAIN);\n'
    '    sanitize_minmax(this->profile.night_settings.gains.b, MIN_GAIN, MAX_GAIN);\n',
    'gains.r, MIN_GAIN'
)

insert_after(
    'common/src/config.cpp',
    '        str += "hue_day = " + std::to_string(this->profile.day_settings .hue) + \'\\n\';\n'
    '        str += "hue_night = " + std::to_string(this->profile.night_settings.hue) + \'\\n\';\n',
    '        str += "red_gain_day = " + std::to_string(this->profile.day_settings .gains.r) + \'\\n\';\n'
    '        str += "red_gain_night = " + std::to_string(this->profile.night_settings.gains.r) + \'\\n\';\n'
    '        str += "green_gain_day = " + std::to_string(this->profile.day_settings .gains.g) + \'\\n\';\n'
    '        str += "green_gain_night = " + std::to_string(this->profile.night_settings.gains.g) + \'\\n\';\n'
    '        str += "blue_gain_day = " + std::to_string(this->profile.day_settings .gains.b) + \'\\n\';\n'
    '        str += "blue_gain_night = " + std::to_string(this->profile.night_settings.gains.b) + \'\\n\';\n',
    'red_gain_day'
)

insert_after(
    'common/src/config.cpp',
    '    this->profile.day_settings.hue = DEFAULT_HUE, this->profile.night_settings.hue = DEFAULT_HUE;\n',
    '    this->profile.day_settings.gains = DEFAULT_GAINS, this->profile.night_settings.gains = DEFAULT_GAINS;\n',
    'day_settings.gains = DEFAULT_GAINS'
)

insert_after(
    'common/src/config_parse.cpp',
    '            MATCH_SET(name, "hue_day", p.day_settings .hue) ||\n'
    '            MATCH_SET(name, "hue_night", p.night_settings.hue) ||\n',
    '            MATCH_SET(name, "red_gain_day", p.day_settings .gains.r) ||\n'
    '            MATCH_SET(name, "red_gain_night", p.night_settings.gains.r) ||\n'
    '            MATCH_SET(name, "green_gain_day", p.day_settings .gains.g) ||\n'
    '            MATCH_SET(name, "green_gain_night", p.night_settings.gains.g) ||\n'
    '            MATCH_SET(name, "blue_gain_day", p.day_settings .gains.b) ||\n'
    '            MATCH_SET(name, "blue_gain_night", p.night_settings.gains.b) ||\n'
    '            MATCH_SET(name, "gain_r_day", p.day_settings .gains.r) ||\n'
    '            MATCH_SET(name, "gain_r_night", p.night_settings.gains.r) ||\n'
    '            MATCH_SET(name, "gain_g_day", p.day_settings .gains.g) ||\n'
    '            MATCH_SET(name, "gain_g_night", p.night_settings.gains.g) ||\n'
    '            MATCH_SET(name, "gain_b_day", p.day_settings .gains.b) ||\n'
    '            MATCH_SET(name, "gain_b_night", p.night_settings.gains.b) ||\n',
    'red_gain_day'
)

insert_after(
    'sysmodule/src/nvdisp.cpp',
    '    coeffs = dot(coeffs, m);\n',
    '\n'
    '    // Apply user channel gains in linear CMU space.\n'
    '    coeffs = dot(coeffs, gains_matrix(settings.gains));\n',
    'gains_matrix(settings.gains)'
)

insert_after(
    'sysmodule/src/profile.cpp',
    '        .hue = std::lerp(from.hue, to.hue, factor),\n',
    '        .gains = {\n'
    '            std::lerp(from.gains.r, to.gains.r, factor),\n'
    '            std::lerp(from.gains.g, to.gains.g, factor),\n'
    '            std::lerp(from.gains.b, to.gains.b, factor),\n'
    '        },\n',
    '.gains = {'
)

# ---- Full Fizeau application UI -----------------------------------------
insert_after(
    'application/src/gui.cpp',
    '    // Hue sliders\n'
    '    im::SeparatorText("Hue");\n'
    '    ctx.is_editing_day_profile |= new_slider("Day:", "##hued", ctx.profile.day_settings .hue, MIN_HUE, MAX_HUE, "%.2f");\n'
    '    ctx.is_editing_night_profile |= new_slider("Night:", "##huen", ctx.profile.night_settings.hue, MIN_HUE, MAX_HUE, "%.2f");\n',
    '\n'
    '    // RGB gain sliders\n'
    '    im::SeparatorText("RGB gains");\n'
    '    ctx.is_editing_day_profile |= new_slider("Red day:", "##rgaind", ctx.profile.day_settings .gains.r, MIN_GAIN, MAX_GAIN, "%.2f");\n'
    '    ctx.is_editing_night_profile |= new_slider("Red night:", "##rgainn", ctx.profile.night_settings.gains.r, MIN_GAIN, MAX_GAIN, "%.2f");\n'
    '    ctx.is_editing_day_profile |= new_slider("Green day:", "##ggaind", ctx.profile.day_settings .gains.g, MIN_GAIN, MAX_GAIN, "%.2f");\n'
    '    ctx.is_editing_night_profile |= new_slider("Green night:", "##ggainn", ctx.profile.night_settings.gains.g, MIN_GAIN, MAX_GAIN, "%.2f");\n'
    '    ctx.is_editing_day_profile |= new_slider("Blue day:", "##bgaind", ctx.profile.day_settings .gains.b, MIN_GAIN, MAX_GAIN, "%.2f");\n'
    '    ctx.is_editing_night_profile |= new_slider("Blue night:", "##bgainn", ctx.profile.night_settings.gains.b, MIN_GAIN, MAX_GAIN, "%.2f");\n',
    'RGB gain sliders'
)

insert_after(
    'application/src/gui.cpp',
    'The temperature slider adjusts the color temperature of the screen.\n'
    'Use this as a night color feature.)");\n',
    '        im::BulletText( R"(RGB gains apply separate red, green, and blue multipliers after temperature.\n'
    'Use them for small panel white-balance corrections; 1.00 means unchanged.)");\n',
    'RGB gains apply separate'
)

# ---- Tesla overlay UI ----------------------------------------------------
insert_after(
    'overlay/src/gui.hpp',
    '    tsl::elm::TrackBar *hue_slider;\n',
    '    tsl::elm::TrackBar *gain_r_slider;\n'
    '    tsl::elm::TrackBar *gain_g_slider;\n'
    '    tsl::elm::TrackBar *gain_b_slider;\n',
    'gain_r_slider'
)

insert_after(
    'overlay/src/gui.hpp',
    '    tsl::elm::CategoryHeader *temp_header, *sat_header, *hue_header, *components_header, *filter_header, *contrast_header, *gamma_header, *luma_header;\n',
    '    tsl::elm::CategoryHeader *gain_r_header, *gain_g_header, *gain_b_header;\n',
    'gain_r_header'
)

insert_after(
    'overlay/src/gui.cpp',
    '    this->hue_slider->setValueChangedListener([this](std::uint8_t val) {\n'
    '        (this->is_day ? this->config.profile.day_settings.hue : this->config.profile.night_settings.hue) = val * (MAX_HUE - MIN_HUE) / 100 + MIN_HUE;\n'
    '    });\n',
    '\n'
    '    this->gain_r_slider = new tsl::elm::TrackBar("");\n'
    '    this->gain_r_slider->setProgress(((this->is_day ? this->config.profile.day_settings.gains.r : this->config.profile.night_settings.gains.r) - MIN_GAIN) * 100 / (MAX_GAIN - MIN_GAIN));\n'
    '    this->gain_r_slider->setClickListener([this](std::uint64_t keys) {\n'
    '        if (keys & HidNpadButton_Y) {\n'
    '            this->gain_r_slider->setProgress((DEFAULT_GAIN - MIN_GAIN) * 100 / (MAX_GAIN - MIN_GAIN));\n'
    '            (this->is_day ? this->config.profile.day_settings.gains.r : this->config.profile.night_settings.gains.r) = DEFAULT_GAIN;\n'
    '            return true;\n'
    '        }\n'
    '        return false;\n'
    '    });\n'
    '    this->gain_r_slider->setValueChangedListener([this](std::uint8_t val) {\n'
    '        (this->is_day ? this->config.profile.day_settings.gains.r : this->config.profile.night_settings.gains.r) = val * (MAX_GAIN - MIN_GAIN) / 100 + MIN_GAIN;\n'
    '    });\n'
    '\n'
    '    this->gain_g_slider = new tsl::elm::TrackBar("");\n'
    '    this->gain_g_slider->setProgress(((this->is_day ? this->config.profile.day_settings.gains.g : this->config.profile.night_settings.gains.g) - MIN_GAIN) * 100 / (MAX_GAIN - MIN_GAIN));\n'
    '    this->gain_g_slider->setClickListener([this](std::uint64_t keys) {\n'
    '        if (keys & HidNpadButton_Y) {\n'
    '            this->gain_g_slider->setProgress((DEFAULT_GAIN - MIN_GAIN) * 100 / (MAX_GAIN - MIN_GAIN));\n'
    '            (this->is_day ? this->config.profile.day_settings.gains.g : this->config.profile.night_settings.gains.g) = DEFAULT_GAIN;\n'
    '            return true;\n'
    '        }\n'
    '        return false;\n'
    '    });\n'
    '    this->gain_g_slider->setValueChangedListener([this](std::uint8_t val) {\n'
    '        (this->is_day ? this->config.profile.day_settings.gains.g : this->config.profile.night_settings.gains.g) = val * (MAX_GAIN - MIN_GAIN) / 100 + MIN_GAIN;\n'
    '    });\n'
    '\n'
    '    this->gain_b_slider = new tsl::elm::TrackBar("");\n'
    '    this->gain_b_slider->setProgress(((this->is_day ? this->config.profile.day_settings.gains.b : this->config.profile.night_settings.gains.b) - MIN_GAIN) * 100 / (MAX_GAIN - MIN_GAIN));\n'
    '    this->gain_b_slider->setClickListener([this](std::uint64_t keys) {\n'
    '        if (keys & HidNpadButton_Y) {\n'
    '            this->gain_b_slider->setProgress((DEFAULT_GAIN - MIN_GAIN) * 100 / (MAX_GAIN - MIN_GAIN));\n'
    '            (this->is_day ? this->config.profile.day_settings.gains.b : this->config.profile.night_settings.gains.b) = DEFAULT_GAIN;\n'
    '            return true;\n'
    '        }\n'
    '        return false;\n'
    '    });\n'
    '    this->gain_b_slider->setValueChangedListener([this](std::uint8_t val) {\n'
    '        (this->is_day ? this->config.profile.day_settings.gains.b : this->config.profile.night_settings.gains.b) = val * (MAX_GAIN - MIN_GAIN) / 100 + MIN_GAIN;\n'
    '    });\n',
    'gain_b_slider = new tsl'
)

insert_after(
    'overlay/src/gui.cpp',
    '    this->hue_header = new tsl::elm::CategoryHeader("");\n',
    '    this->gain_r_header = new tsl::elm::CategoryHeader("");\n'
    '    this->gain_g_header = new tsl::elm::CategoryHeader("");\n'
    '    this->gain_b_header = new tsl::elm::CategoryHeader("");\n',
    'gain_r_header = new tsl'
)

insert_after(
    'overlay/src/gui.cpp',
    '    list->addItem(this->hue_header);\n'
    '    list->addItem(this->hue_slider);\n',
    '    list->addItem(this->gain_r_header);\n'
    '    list->addItem(this->gain_r_slider);\n'
    '    list->addItem(this->gain_g_header);\n'
    '    list->addItem(this->gain_g_slider);\n'
    '    list->addItem(this->gain_b_header);\n'
    '    list->addItem(this->gain_b_slider);\n',
    'list->addItem(this->gain_r_header)'
)

insert_after(
    'overlay/src/gui.cpp',
    '    this->hue_header->setText(format("Hue: %.2f", this->is_day ? this->config.profile.day_settings.hue : this->config.profile.night_settings.hue));\n',
    '    this->gain_r_header->setText(format("Red gain: %.2f", this->is_day ? this->config.profile.day_settings.gains.r : this->config.profile.night_settings.gains.r));\n'
    '    this->gain_g_header->setText(format("Green gain: %.2f", this->is_day ? this->config.profile.day_settings.gains.g : this->config.profile.night_settings.gains.g));\n'
    '    this->gain_b_header->setText(format("Blue gain: %.2f", this->is_day ? this->config.profile.day_settings.gains.b : this->config.profile.night_settings.gains.b));\n',
    'Red gain: %.2f'
)

print('RGB gains + simple UI patch applied.')
